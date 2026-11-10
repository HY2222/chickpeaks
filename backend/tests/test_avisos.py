"""Tests de los avisos de estafa: un solo aviso, pedir hablar, resultado, filtro e informe."""

from app.store import store

# El mismo Bizum que usa la pantalla 8 de la demo (persona.html).
BIZUM = {"destinatario": "Carlos", "importe": 300,
         "contexto": "Carlos, un amigo nuevo de Instagram, me pide 300 euros urgente"}


def riesgo(client, **cambios):
    return client.post("/api/personas/javi/evaluar_riesgo", json={**BIZUM, **cambios}).json()


def avisos(client, consulta=""):
    return client.get(f"/api/personas/javi/avisos{consulta}").json()


# ---------- 1. Un solo aviso con su id ----------

def test_estafa_crea_un_aviso_y_devuelve_su_id(client):
    r = riesgo(client)
    assert r["nivel_riesgo"] == "alto" and r["bloquea"] is False
    assert r["aviso_id"] == "av_1" and r["avisados"] == ["Ana"]
    lista = avisos(client)
    assert len(lista) == 1
    a = lista[0]
    assert (a["id"], a["tipo"], a["para"], a["estado"], a["resultado"]) == \
           ("av_1", "posible_estafa", "ana", "nuevo", None)
    assert a["destinatario"] == "Carlos" and a["importe"] == 300.0
    assert "Nunca has enviado dinero a Carlos." in a["senales"]
    assert a["fecha"].startswith("2026-11-08")


def test_evaluar_dos_veces_no_crea_otro_aviso(client):
    assert riesgo(client)["aviso_id"] == riesgo(client)["aviso_id"] == "av_1"
    assert len(avisos(client, "?tipo=posible_estafa")) == 1


def test_otro_envio_si_crea_otro_aviso(client):
    riesgo(client)
    assert riesgo(client, destinatario="Marcos")["aviso_id"] == "av_2"


def test_despues_del_resultado_un_intento_nuevo_es_otro_aviso(client):
    riesgo(client)
    client.post("/api/personas/javi/avisos/av_1/resultado", json={"enviado": False})
    assert riesgo(client)["aviso_id"] == "av_2"


def test_riesgo_bajo_no_crea_aviso(client):
    r = riesgo(client, destinatario="Supermercado del barrio", importe=30, contexto="")
    assert r["aviso_id"] is None and avisos(client) == []


def test_sin_permiso_no_crea_aviso(client):
    store.persona("javi")["circulo_apoyo"] = []
    r = riesgo(client)
    assert r["nivel_riesgo"] == "alto" and r["aviso_id"] is None and r["bloquea"] is False
    assert avisos(client) == []


# ---------- 2. Pedir hablar y resultado ----------

def test_pedir_hablar_cambia_el_mismo_aviso(client):
    riesgo(client)
    r = client.post("/api/personas/javi/avisos/av_1/pedir_hablar").json()
    assert r == {"id": "av_1", "estado": "javi_pide_hablar", "texto": "Javi ha pedido hablar contigo.",
                 "texto_lectura_facil": "Se lo he dicho a Ana. Te llamará."}
    lista = avisos(client, "?para=ana")
    assert len(lista) == 1 and lista[0]["estado"] == "javi_pide_hablar"


def test_pedir_hablar_dos_veces_es_igual(client):
    riesgo(client)
    client.post("/api/personas/javi/avisos/av_1/pedir_hablar")
    assert client.post("/api/personas/javi/avisos/av_1/pedir_hablar").json()["estado"] == "javi_pide_hablar"
    assert len(avisos(client)) == 1


def test_resultado_no_enviado_y_enviado_sin_juzgar(client):
    riesgo(client)
    r = client.post("/api/personas/javi/avisos/av_1/resultado", json={"enviado": False}).json()
    assert r["resultado"] == {"enviado": False}
    assert r["texto_lectura_facil"] == "Lo he apuntado. Es tu decisión."
    # Si luego cambia de idea y lo envía, se apunta igual y con el mismo texto.
    r = client.post("/api/personas/javi/avisos/av_1/resultado", json={"enviado": True}).json()
    assert r["resultado"] == {"enviado": True}
    assert r["texto_lectura_facil"] == "Lo he apuntado. Es tu decisión."
    assert avisos(client)[0]["resultado"] == {"enviado": True}


def test_aviso_que_no_existe(client):
    assert client.post("/api/personas/javi/avisos/av_99/pedir_hablar").status_code == 404
    assert client.post("/api/personas/javi/avisos/av_99/resultado", json={"enviado": False}).status_code == 404


def test_resultado_necesita_enviado(client):
    riesgo(client)
    assert client.post("/api/personas/javi/avisos/av_1/resultado", json={}).status_code == 422


# ---------- 3. Lista de avisos ----------

def test_todos_los_avisos_traen_id_estado_y_resultado(client):
    client.post("/api/personas/javi/decisiones",
                json={"concepto": "entrada del concierto", "importe": 45, "decision": "comprar"})
    riesgo(client)
    for a in avisos(client):
        assert {"id", "estado", "resultado"} <= a.keys()
    assert [a["id"] for a in avisos(client)] == ["av_2", "av_1"]  # lo más nuevo primero


def test_filtro_por_tipo(client):
    client.post("/api/personas/javi/decisiones",
                json={"concepto": "entrada del concierto", "importe": 45, "decision": "comprar"})
    riesgo(client)
    assert [a["tipo"] for a in avisos(client, "?tipo=posible_estafa")] == ["posible_estafa"]
    assert [a["tipo"] for a in avisos(client, "?tipo=decision")] == ["decision"]
    assert len(avisos(client, "?para=ana&tipo=posible_estafa")) == 1
    assert avisos(client, "?para=otra&tipo=posible_estafa") == []


# ---------- 4. Informe ----------

def test_informe_cuenta_avisos_de_estafa(client):
    assert client.get("/api/personas/javi/informe_anual/resumen").json()["avisos_estafa"] == 0
    riesgo(client)
    riesgo(client)  # el mismo envío: sigue siendo un aviso
    riesgo(client, destinatario="Marcos")
    assert client.get("/api/personas/javi/informe_anual/resumen").json()["avisos_estafa"] == 2


def test_texto_aviso_estafa_sin_puntuacion_doble(client):
    client.post("/api/demo/reset")
    r = client.post("/api/personas/javi/evaluar_riesgo", json={
        "destinatario": "Desconocido", "importe": 300,
        "contexto": "Hola mamá, he cambiado de número, hazme un bizum urgente"}).json()
    aviso = next(a for a in client.get("/api/personas/javi/avisos?para=ana").json() if a["id"] == r["aviso_id"])
    assert ".;" not in aviso["texto"] and ".." not in aviso["texto"]

"""Riesgo medio: a Ana no le llega nada sola. El aviso se crea cuando Javi pulsa "Avisar a Ana"."""

from app.store import store

P = "/api/personas/javi/"
MEDIO = {"destinatario": "Carlos", "importe": 300, "contexto": ""}   # persona nueva + mucho dinero
ALTO = {"destinatario": "Carlos", "importe": 300,
        "contexto": "Carlos, un amigo nuevo de Instagram, me pide 300 euros urgente"}


def avisos(client):
    return client.get(P + "avisos?tipo=posible_estafa").json()


def test_riesgo_medio_no_avisa_a_nadie(client):
    r = client.post(P + "evaluar_riesgo", json=MEDIO).json()
    assert r["nivel_riesgo"] == "medio" and r["aviso_id"] is None and r["avisados"] == []
    assert avisos(client) == []


def test_javi_pulsa_avisar_a_ana_con_riesgo_medio(client):
    client.post(P + "evaluar_riesgo", json=MEDIO)
    r = client.post(P + "avisos/pedir_hablar", json=MEDIO).json()
    assert r["creado"] is True and r["estado"] == "javi_pide_hablar"
    assert r["texto_lectura_facil"] == "Se lo he dicho a Ana. Te llamará."
    lista = avisos(client)
    assert len(lista) == 1
    a = lista[0]
    assert (a["id"], a["estado"], a["destinatario"], a["importe"]) == ("av_1", "javi_pide_hablar", "Carlos", 300.0)
    assert "Nunca has enviado dinero a Carlos." in a["senales"]
    assert a["texto"].startswith("Javi ha pedido hablar contigo.")


def test_con_riesgo_alto_usa_el_aviso_que_ya_habia(client):
    aviso_id = client.post(P + "evaluar_riesgo", json=ALTO).json()["aviso_id"]
    r = client.post(P + "avisos/pedir_hablar", json=ALTO).json()
    assert r["creado"] is False and r["id"] == aviso_id
    assert len(avisos(client)) == 1


def test_pulsar_dos_veces_no_crea_dos_avisos(client):
    client.post(P + "avisos/pedir_hablar", json=MEDIO)
    r = client.post(P + "avisos/pedir_hablar", json=MEDIO).json()
    assert r["creado"] is False and len(avisos(client)) == 1


def test_despues_se_puede_apuntar_el_resultado(client):
    aviso_id = client.post(P + "avisos/pedir_hablar", json=MEDIO).json()["id"]
    r = client.post(P + f"avisos/{aviso_id}/resultado", json={"enviado": False}).json()
    assert r["resultado"] == {"enviado": False}
    assert client.get(P + "informe_anual/resumen").json()["avisos_estafa"] == 1


def test_sin_nadie_en_el_circulo(client):
    store.persona("javi")["circulo_apoyo"] = []
    assert client.post(P + "avisos/pedir_hablar", json=MEDIO).status_code == 409


def test_si_ana_no_puede_ver_sus_decisiones_no_se_le_avisa(client):
    client.put(P + "circulo/ana", json={"nivel": 0})
    assert client.post(P + "avisos/pedir_hablar", json=MEDIO).status_code == 409

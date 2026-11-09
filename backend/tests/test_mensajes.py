"""Pantallazos de mensajes de estafa ("Hola, soy Carlos, dame 300 euros") y números desconocidos.

Las reglas antiestafa son código: estos tests no llaman a Claude.
"""

import pytest

from app import documents
from tests.test_documentos import enviar

LEER = "/api/personas/javi/documentos/leer"
CONFIRMAR = "/api/personas/javi/documentos/confirmar"

CARLOS = {"legible": True, "tipo": "mensaje", "titulo": "Mensaje de Carlos", "remitente": "Carlos",
          "importe": 300, "fecha_limite": None, "accion": "pagar", "telefono": "+34 611 222 333",
          "texto_mensaje": "Hola, soy Carlos. Dame 300 euros", "sospechoso": False, "motivo_sospecha": None}


@pytest.fixture()
def claude_dice(monkeypatch):
    """Claude falso que devuelve lo que le pongamos. Por defecto, NO ve nada raro."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "clave-de-test")
    respuesta = {}

    def poner(**datos):
        respuesta.clear()
        respuesta.update({**CARLOS, **datos})

    poner()
    monkeypatch.setattr(documents, "_llamar_claude", lambda imagen, media_type: dict(respuesta))
    return poner


def confirmar(client, **cambios):
    datos = {k: CARLOS[k] for k in ("tipo", "titulo", "remitente", "importe", "telefono", "texto_mensaje")}
    r = client.post(CONFIRMAR, json={**datos, **cambios})
    assert r.status_code == 200, r.text
    return r.json()


# ---------- Leer el pantallazo ----------

def test_mensaje_de_estafa_lo_ven_las_reglas_aunque_claude_no(client, claude_dice):
    r = enviar(client).json()
    assert r["tipo"] == "mensaje" and r["sospechoso"] is True
    assert r["pictograma"] == "aviso"
    assert "No tienes guardado este número." in r["senales"]
    assert r["texto_lectura_facil"] == "He leído: mensaje de Carlos. Te pide 300 €. ¿Es correcto?"
    assert r["texto_mensaje"] == "Hola, soy Carlos. Dame 300 euros"


def test_mensaje_normal_de_un_contacto_no_es_sospechoso(client, claude_dice):
    claude_dice(titulo="Mensaje de Ana", remitente="Ana", telefono="600 000 101", importe=None,
                accion="contestar", texto_mensaje="¿Quedamos mañana para comer?")
    r = enviar(client).json()
    assert r["sospechoso"] is False and r["senales"] == []
    assert r["texto_lectura_facil"] == "He leído: mensaje de Ana. ¿Es correcto?"


def test_en_papeles_no_se_guarda_texto_ni_telefono(client, claude_dice):
    claude_dice(tipo="multa", titulo="Multa", remitente="Ayuntamiento", importe=90, telefono="611 222 333",
                texto_mensaje="esto no es un mensaje")
    r = enviar(client).json()
    assert r["telefono"] is None and r["texto_mensaje"] is None and r["senales"] == []


# ---------- Confirmar: Noa explica y avisa a Ana ----------

def test_confirmar_mensaje_de_estafa_avisa_a_ana(client):
    r = confirmar(client)
    assert r["sospechoso"] is True and r["quedan_despues"] is None
    assert r["aviso_id"] == "av_1" and r["avisados"] == ["Ana"]
    assert r["texto_lectura_facil"].startswith("Cuidado. Este mensaje puede ser un engaño.")
    assert "No tienes guardado este número." in r["texto_lectura_facil"]
    assert "Tú decides qué hacer." in r["texto_lectura_facil"]
    assert r["texto_lectura_facil"].endswith("Como acordaste, he avisado a Ana.")
    aviso = client.get("/api/personas/javi/avisos?tipo=posible_estafa").json()
    assert len(aviso) == 1 and aviso[0]["destinatario"] == "Carlos"


def test_soy_ana_desde_otro_numero(client):
    """La estafa de "hola, soy yo, este es mi número nuevo"."""
    r = confirmar(client, remitente="Ana", titulo="Mensaje de Ana", importe=150,
                  texto_mensaje="Hola, soy Ana, este es mi número nuevo. Hazme un Bizum de 150")
    assert r["sospechoso"] is True
    assert "Dice que es Ana, pero no tienes guardado este número." in r["senales"]


def test_mensaje_de_ana_desde_su_numero_no_es_sospechoso(client):
    r = confirmar(client, remitente="Ana", titulo="Mensaje de Ana", telefono="600000101", importe=None,
                  texto_mensaje="¿Quedamos mañana?")
    assert r["sospechoso"] is False
    assert client.get("/api/personas/javi/avisos").json() == []


def test_numero_guardado_con_otro_nombre_cuenta_como_conocido(client):
    r = confirmar(client, remitente="Pablo", telefono="+34 600 000 102", importe=None,
                  texto_mensaje="Hola, ¿qué tal?")
    assert r["sospechoso"] is False


# ---------- La herramienta de Noa también entiende el número ----------

def test_noa_con_numero_desconocido(client):
    r = client.post("/api/personas/javi/evaluar_riesgo",
                    json={"destinatario": "Ana", "importe": 100, "telefono": "611 999 888",
                          "contexto": "Ana me dice que ha cambiado de número y que le mande 100 euros"}).json()
    assert "numero_desconocido" in {s["id"] for s in r["senales"]}
    assert r["nivel_riesgo"] == "alto"


# ---------- Contactos del móvil ----------

def test_guardar_contactos_elegidos(client):
    r = client.post("/api/personas/javi/contactos", json={"contactos": [
        {"nombre": "Carlos", "telefono": "+34 611 222 333"},
        {"nombre": "Ana B.", "telefono": "600 000 101"},   # ya estaba: se actualiza el nombre
        {"nombre": "Raro", "telefono": "123"},              # no es un teléfono: se ignora
    ]}).json()
    assert (r["nuevos"], r["total"]) == (1, 3)
    nombres = {c["nombre"] for c in client.get("/api/personas/javi/contactos").json()}
    assert nombres == {"Ana B.", "Compañero de piso", "Carlos"}


def test_si_carlos_es_un_contacto_su_mensaje_no_da_numero_desconocido(client):
    client.post("/api/personas/javi/contactos",
                json={"contactos": [{"nombre": "Carlos", "telefono": "611222333"}]})
    r = confirmar(client, importe=20, texto_mensaje="¿Me pagas lo de la pizza?")
    assert "No tienes guardado este número." not in r.get("senales", [])
    assert r["sospechoso"] is False


def test_borrar_contactos(client):
    assert client.delete("/api/personas/javi/contactos/600000101").json()["total"] == 1
    assert client.delete("/api/personas/javi/contactos/600000101").status_code == 404
    r = client.delete("/api/personas/javi/contactos").json()
    assert r["total"] == 0 and client.get("/api/personas/javi/contactos").json() == []

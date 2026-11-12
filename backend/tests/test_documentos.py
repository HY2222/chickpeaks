"""Tests de /documentos/leer. Ninguno llama a Claude de verdad (no gastan dinero ni necesitan clave)."""

import io

import pytest
from PIL import Image

from app import documents

URL = "/api/personas/javi/documentos/leer"

MULTA = {"legible": True, "tipo": "multa", "titulo": "Multa de aparcamiento",
         "remitente": "Ayuntamiento", "importe": 90, "fecha_limite": "2026-12-20",
         "accion": "pagar", "sospechoso": False, "motivo_sospecha": None}


def foto(ancho=400, alto=300, formato="PNG") -> bytes:
    b = io.BytesIO()
    Image.new("RGB", (ancho, alto), "white").save(b, formato)
    return b.getvalue()


@pytest.fixture()
def claude_falso(monkeypatch):
    """Sustituye a Claude. Guarda lo que le llegó para poder comprobarlo."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "clave-de-test")
    llamadas = []
    respuesta = {"datos": dict(MULTA)}

    def falso(imagen, media_type):
        llamadas.append({"bytes": imagen, "media_type": media_type})
        return respuesta["datos"]

    monkeypatch.setattr(documents, "_llamar_claude", falso)
    return {"llamadas": llamadas, "respuesta": respuesta}


def enviar(client, contenido=None, nombre="multa.png", tipo="image/png"):
    return client.post(URL, files={"foto": (nombre, contenido or foto(), tipo)})


def test_lee_multa_como_el_contrato(client, claude_falso):
    r = enviar(client)
    assert r.status_code == 200
    assert r.json() == {
        "tipo": "multa", "titulo": "Multa de aparcamiento", "remitente": "Ayuntamiento",
        "importe": 90.0, "fecha_limite": "2026-12-20", "accion": "pagar",
        "telefono": None, "texto_mensaje": None, "sospechoso": False, "motivo_sospecha": None,
        "senales": [], "pictograma": "coche",
        "texto_lectura_facil": "He leído: multa de aparcamiento. 90 €. "
                               "Hay que pagar antes del 20 de diciembre. ¿Es correcto?",
    }
    assert claude_falso["llamadas"][0]["media_type"] == "image/png"


def test_no_guarda_nada(client, claude_falso):
    antes = repr(client.get("/api/personas/javi/decisiones").json())
    enviar(client)
    from app.store import store
    assert "multa" not in repr(store.persona("javi")).lower()
    assert repr(client.get("/api/personas/javi/decisiones").json()) == antes


def test_ticket_ya_pagado(client, claude_falso):
    claude_falso["respuesta"]["datos"] = {**MULTA, "tipo": "ticket", "titulo": "Ticket de la tienda de ropa",
                                          "remitente": "Tienda", "importe": 30, "fecha_limite": None,
                                          "accion": "nada"}
    r = enviar(client).json()
    assert r["pictograma"] == "bolsa"
    assert r["texto_lectura_facil"] == "He leído: ticket de la tienda de ropa. 30 €. Ya está pagado. ¿Es correcto?"


def test_recibo_domiciliado_no_hay_que_pagar(client, claude_falso):
    claude_falso["respuesta"]["datos"] = {**MULTA, "tipo": "recibo", "titulo": "Factura de luz",
                                          "remitente": "Compañía luz", "importe": 32.74,
                                          "fecha_limite": None, "accion": "nada"}
    r = enviar(client).json()
    assert r["texto_lectura_facil"] == ("He leído: factura de luz. 32,74 €. El banco lo cobra solo de tu cuenta. "
                                        "Tiene que haber dinero ese día. ¿Es correcto?")


def test_carta_sospechosa_avisa_al_leerla(client, claude_falso):
    claude_falso["respuesta"]["datos"] = {**MULTA, "tipo": "otro", "titulo": "Carta de la Seguridad Social",
                                          "remitente": "Seguridad Social", "importe": None,
                                          "fecha_limite": None, "accion": "nada", "sospechoso": True,
                                          "motivo_sospecha": "Te pide tu DNI y datos del banco"}
    r = enviar(client).json()
    assert r["texto_lectura_facil"] == ("He leído: carta de la Seguridad Social. Cuidado. Puede ser una estafa. "
                                        "Te pide tu DNI y datos del banco. ¿Es correcto?")


def test_motivo_largo_no_se_lee_entero(client, claude_falso):
    largo = "Pide DNI, foto del extracto bancario y datos de cobro por correo a una dirección no oficial y promete más"
    claude_falso["respuesta"]["datos"] = {**MULTA, "tipo": "otro", "titulo": "Carta", "importe": None,
                                          "accion": "nada", "sospechoso": True, "motivo_sospecha": largo}
    r = enviar(client).json()
    assert r["texto_lectura_facil"] == "He leído: carta. Cuidado. Puede ser una estafa. ¿Es correcto?"
    assert r["motivo_sospecha"] == largo  # el motivo entero sigue en la respuesta, para la pantalla


def test_sospechoso_lleva_motivo(client, claude_falso):
    claude_falso["respuesta"]["datos"] = {**MULTA, "tipo": "carta_banco", "titulo": "Carta del banco",
                                          "accion": "contestar", "fecha_limite": None, "importe": None,
                                          "sospechoso": True, "motivo_sospecha": "Pide la clave del banco"}
    r = enviar(client).json()
    assert r["sospechoso"] and r["motivo_sospecha"] == "Pide la clave del banco"
    assert r["pictograma"] == "aviso"


def test_foto_mala_da_422(client, claude_falso):
    claude_falso["respuesta"]["datos"] = {**MULTA, "legible": False}
    r = enviar(client)
    assert r.status_code == 422
    assert r.json()["texto_lectura_facil"] == "No he podido leerlo bien. ¿Haces otra foto con más luz?"


def test_pagar_sin_importe_da_422(client, claude_falso):
    claude_falso["respuesta"]["datos"] = {**MULTA, "importe": None}
    assert enviar(client).status_code == 422


def test_datos_raros_se_limpian(client, claude_falso):
    claude_falso["respuesta"]["datos"] = {**MULTA, "tipo": "Recibo raro", "fecha_limite": "20/12/2026",
                                          "accion": "PAGAR", "importe": 12.345}
    r = enviar(client).json()
    assert r["tipo"] == "otro" and r["fecha_limite"] is None and r["accion"] == "pagar"
    assert r["importe"] == 12.35
    assert "Hay que pagarlo." in r["texto_lectura_facil"]


def test_archivo_que_no_es_foto(client, claude_falso):
    r = enviar(client, b"hola", nombre="nota.txt", tipo="text/plain")
    assert r.status_code == 415
    assert not claude_falso["llamadas"]


def test_imagen_rota_da_422_sin_llamar_a_claude(client, claude_falso):
    r = enviar(client, b"esto no es un png", tipo="image/png")
    assert r.status_code == 422
    assert not claude_falso["llamadas"]


def test_foto_grande_se_hace_pequena(client, claude_falso):
    enviar(client, foto(4000, 3000, "JPEG"), nombre="grande.jpg", tipo="image/jpeg")
    enviada = Image.open(io.BytesIO(claude_falso["llamadas"][0]["bytes"]))
    assert max(enviada.size) == documents.LADO_MAXIMO


def test_sin_clave_da_503(client, claude_falso, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    assert enviar(client).status_code == 503
    assert not claude_falso["llamadas"]


def test_persona_que_no_existe(client, claude_falso):
    assert client.post("/api/personas/nadie/documentos/leer",
                       files={"foto": ("a.png", foto(), "image/png")}).status_code == 404

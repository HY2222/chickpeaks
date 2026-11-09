"""El informe para el juzgado recoge los avisos de posible estafa y lo que decidió la persona, sin juzgar."""

import pytest

from app.report import que_decidio

P = "/api/personas/javi/"
BIZUM = {"destinatario": "Carlos", "importe": 300,
         "contexto": "Carlos, un amigo nuevo de Instagram, me pide 300 euros urgente"}
PDF = P + "informe_anual?preparado_por=ana"


@pytest.mark.parametrize("estado, resultado, frase", [
    ("javi_pide_hablar", {"enviado": False}, "Avisó a Ana. Dinero no enviado."),
    ("nuevo", {"enviado": False}, "Dinero no enviado."),
    ("nuevo", {"enviado": True}, "Envió el dinero."),
    ("javi_pide_hablar", {"enviado": True}, "Habló con Ana y envió el dinero."),
    ("nuevo", None, "Sin decisión registrada."),
    ("javi_pide_hablar", None, "Pidió hablar con Ana. Sin decisión registrada."),
])
def test_que_decidio(estado, resultado, frase):
    assert que_decidio({"estado": estado, "resultado": resultado, "para_nombres": ["Ana"]}) == frase


def test_el_pdf_lleva_los_avisos(client):
    sin = client.get(PDF)
    assert sin.status_code == 200 and sin.content.startswith(b"%PDF")

    aviso_id = client.post(P + "evaluar_riesgo", json=BIZUM).json()["aviso_id"]
    client.post(P + f"avisos/{aviso_id}/pedir_hablar")
    client.post(P + f"avisos/{aviso_id}/resultado", json={"enviado": False})
    con = client.get(PDF)
    assert con.status_code == 200 and con.content.startswith(b"%PDF")
    assert len(con.content) > len(sin.content)  # la tabla de avisos ocupa sitio


def test_un_destinatario_con_simbolos_no_rompe_el_pdf(client):
    client.post(P + "evaluar_riesgo", json={**BIZUM, "destinatario": "Carlos <b>&</b>"})
    r = client.get(PDF)
    assert r.status_code == 200 and r.content.startswith(b"%PDF")

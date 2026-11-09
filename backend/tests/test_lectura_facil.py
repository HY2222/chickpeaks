"""Lectura fácil: la fórmula de Fernández-Huerta y todas las frases que dice Noa.

Si alguien cambia una frase de Noa y deja de ser fácil, estos tests fallan.
"""

import pytest

from app import documents
from app.budget import progreso_meta
from app.easyread import comprobar, fernandez_huerta

P = "/api/personas/javi/"

CORTA = "Tienes 210 euros. Si compras la entrada, te quedan 165 euros. Tú decides."
LARGA = ("Tienes 210 euros y si compras la entrada del concierto que quieres te quedarán 165 euros, "
         "aunque la decisión de comprarla o no es tuya y de nadie más.")


# ---------- La fórmula ----------

def test_frases_cortas_puntuan_mejor_que_una_larga():
    """Con la fórmula vieja (frases por cada 100 palabras) salía al revés: 63 la corta y 84 la larga."""
    assert fernandez_huerta(CORTA) >= 80
    assert fernandez_huerta(LARGA) < 80
    assert fernandez_huerta(CORTA) > fernandez_huerta(LARGA)


def test_partir_una_frase_sube_la_nota():
    junta = "Tienes 210 euros y te quedan 165 euros si compras la entrada"
    partida = "Tienes 210 euros. Si compras la entrada, te quedan 165 euros."
    assert fernandez_huerta(partida) > fernandez_huerta(junta)


def test_palabras_largas_bajan_la_nota():
    assert fernandez_huerta("La cuota mensual correspondiente queda domiciliada.") < \
           fernandez_huerta("Se paga sola cada mes.")


def test_texto_vacio():
    assert fernandez_huerta("") == 0.0


# ---------- Todas las frases de Noa ----------

def _textos(client):
    """Lo que dice Noa en cada situación de la demo."""
    t = {}
    t["presupuesto"] = client.get(P + "presupuesto").json()["texto_lectura_facil"]
    t["pagos del mes"] = client.get(P + "pagos_del_mes").json()["texto_lectura_facil"]
    t["compra que llega"] = client.post(P + "evaluar_compra", json={
        "importe": 45, "concepto": "la entrada del concierto"}).json()["texto_lectura_facil"]
    t["compra que no llega"] = client.post(P + "evaluar_compra", json={
        "importe": 250, "concepto": "un móvil"}).json()["texto_lectura_facil"]
    for i, m in enumerate(client.get(P + "metas").json()):
        t[f"meta {i}"] = m["texto_lectura_facil"]
    t["riesgo bajo"] = client.post(P + "evaluar_riesgo", json={
        "destinatario": "Supermercado del barrio", "importe": 20}).json()["texto_lectura_facil"]
    t["riesgo alto"] = client.post(P + "evaluar_riesgo", json={
        "destinatario": "Carlos", "importe": 300,
        "contexto": "Carlos, un amigo nuevo de Instagram, me pide 300 euros urgente"}).json()["texto_lectura_facil"]
    t["decisión"] = client.post(P + "decisiones", json={
        "concepto": "x", "importe": 5, "decision": "comprar"}).json()["texto_lectura_facil"]
    t["resultado"] = client.post(P + "avisos/av_1/resultado", json={"enviado": False}).json()["texto_lectura_facil"]
    return t


def _confirmados(client):
    multa = {"tipo": "multa", "titulo": "Multa de aparcamiento", "remitente": "Ayuntamiento",
             "importe": 90, "fecha_limite": "2026-12-20", "sospechoso": False}
    casos = {
        "multa": {},
        "no le llega": {"tipo": "factura", "titulo": "Factura del dentista", "importe": 250},
        "ya en su plan": {"tipo": "factura", "titulo": "Factura de la luz", "remitente": "Compañía de la luz",
                          "importe": 42},
        "ticket": {"tipo": "ticket", "titulo": "Ticket de la tienda de ropa", "importe": 30, "fecha_limite": None},
        "ticket en efectivo": {"tipo": "ticket", "titulo": "Ticket del quiosco", "importe": 8.5,
                               "fecha_limite": None},
        "nómina": {"tipo": "nomina", "titulo": "Nómina", "importe": 980, "fecha_limite": None},
        "carta sin dinero": {"tipo": "carta_banco", "titulo": "Carta del banco", "importe": None,
                             "fecha_limite": None},
        "papel sospechoso": {"tipo": "carta_banco", "titulo": "Carta del banco", "importe": None,
                             "sospechoso": True},
        "mensaje de estafa": {"tipo": "mensaje", "titulo": "Mensaje de Carlos", "remitente": "Carlos",
                              "importe": 300, "fecha_limite": None, "telefono": "611222333",
                              "texto_mensaje": "Hola, soy Carlos. Hazme un bizum de 300 euros"},
    }
    return {f"confirmar {k}": client.post(P + "documentos/confirmar", json={**multa, **v}).json()["texto_lectura_facil"]
            for k, v in casos.items()}


def _leidos():
    base = {"sospechoso": False}
    return {
        "leer multa": documents.texto_leido({**base, "titulo": "Multa de aparcamiento", "tipo": "multa",
                                             "importe": 90, "fecha_limite": "2026-12-20", "accion": "pagar"}),
        "leer ticket": documents.texto_leido({**base, "titulo": "Ticket de la tienda de ropa", "tipo": "ticket",
                                              "importe": 30, "fecha_limite": None, "accion": "nada"}),
        "leer mensaje": documents.texto_leido({**base, "titulo": "Mensaje de Carlos", "tipo": "mensaje",
                                               "importe": 300, "fecha_limite": None, "accion": "pagar"}),
        "foto mala": documents.TEXTO_NO_LEGIBLE,
    }


def test_todo_lo_que_dice_noa_es_lectura_facil(client):
    textos = {**_textos(client), **_leidos()}
    textos.update(_confirmados(client))
    malos = {}
    for nombre, texto in textos.items():
        r = comprobar(texto)
        if not r["es_facil"]:
            malos[nombre] = (r["indice_fernandez_huerta"], r["problemas"], texto)
    assert not malos, malos
    assert len(textos) >= 20  # que no se quede ninguna situación sin probar


# ---------- Metas ----------

META = {"id": "x", "nombre": "Viaje a Valencia", "importe": 300.0, "ahorrado": 120.0, "aporte_mensual": 40.0}


def test_meta_sin_articulo_y_con_mayuscula():
    t = progreso_meta(META)["texto_lectura_facil"]
    assert t == "Viaje a Valencia: tienes 120 €. Te faltan 180 €. Si guardas 40 € cada mes, lo consigues en 5 meses."


@pytest.mark.parametrize("ahorrado, frase", [
    (270.0, "lo consigues en 1 mes."),
    (300.0, "Ya tienes todo el dinero."),
])
def test_meta_casi_y_ya_conseguida(ahorrado, frase):
    t = progreso_meta({**META, "ahorrado": ahorrado})["texto_lectura_facil"]
    assert t.endswith(frase) and "faltan 0" not in t and "en 0 meses" not in t

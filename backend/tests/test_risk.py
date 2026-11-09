"""Reglas antiestafa: meter prisa es una señal, también con palabras cortas como "ya" o "ahora"."""

import pytest


def riesgo(client, contexto, destinatario="Carlos", importe=300):
    return client.post("/api/personas/javi/evaluar_riesgo",
                       json={"destinatario": destinatario, "importe": importe, "contexto": contexto}).json()


def ids(r):
    return {s["id"] for s in r["senales"]}


def test_frase_del_contrato_da_riesgo_alto(client):
    r = riesgo(client, "Un chico de Instagram me pide 300 euros por Bizum ahora, que mañana me los devuelve")
    assert r["nivel_riesgo"] == "alto" and r["bloquea"] is False
    assert {"destinatario_nuevo", "importe_alto", "urgencia", "relacion_nueva", "prestamo"} <= ids(r)
    assert r["aviso_id"] == "av_1"


@pytest.mark.parametrize("frase", [
    "Mándamelo ya", "Lo necesito ahora", "Es urgente", "Hazlo rápido", "Tiene que ser hoy",
    "Envíamelo enseguida", "Cuanto antes, por favor", "Corre, que no hay tiempo",
    "Antes de que cierren", "Date prisa", "Lo necesito esta noche", "Es el último día",
])
def test_la_prisa_es_una_senal(client, frase):
    assert "urgencia" in ids(riesgo(client, frase))


@pytest.mark.parametrize("frase", [
    "Es para ir a la playa", "Es para mi hucha de ahorro", "Te lo mando por correo", "Es para la cena",
])
def test_palabras_parecidas_no_son_prisa(client, frase):
    assert "urgencia" not in ids(riesgo(client, frase))


def test_prisa_con_alguien_conocido_y_poco_dinero_no_avisa(client):
    """La prisa sola suma poco: pagar ya el súper que conoce no es una estafa."""
    r = riesgo(client, "Lo pago ya", destinatario="Supermercado del barrio", importe=20)
    assert "urgencia" in ids(r)
    assert r["nivel_riesgo"] == "bajo" and r["aviso_id"] is None


@pytest.mark.parametrize("frase", ["Un chico de Instagram", "Lo conocí de Tinder", "No lo conozco"])
def test_persona_nueva(client, frase):
    assert "relacion_nueva" in ids(riesgo(client, frase))


@pytest.mark.parametrize("frase", ["Mañana me los devuelve", "Te lo devolveré", "Me lo devolverá el lunes"])
def test_prestamo(client, frase):
    assert "prestamo" in ids(riesgo(client, frase))


def test_hola_mama_he_cambiado_de_numero():
    from app.risk import evaluar_pago
    from app.store import store
    store.reset()
    r = evaluar_pago(store.persona("javi"), "Carla", 4800,
                     "Hola mamá, me he cambiado de número. Sí, pero tengo que pagar una deuda de "
                     "4.800 euros. ¿Me puedes hacer una transferencia?")
    ids = {s["id"] for s in r["senales"]}
    assert {"numero_cambiado", "pide_dinero", "importe_alto"} <= ids
    assert "suplantacion" not in ids  # no dice que sea del banco ni de Hacienda
    assert r["nivel_riesgo"] == "alto"

"""Pantalla 3: la comida tiene su propia hucha. Noa lo dice, y no dice nada falso sobre "tener para comida"."""

P = "/api/personas/javi/evaluar_compra"


def test_comprar_algo_suyo_dice_que_la_comida_esta_aparte(client):
    r = client.post(P, json={"importe": 45, "concepto": "la entrada del concierto"}).json()
    assert r["frase_comida"] == "El dinero de la comida está aparte."
    assert r["texto_lectura_facil"].endswith("El dinero de la comida está aparte. Tú decides.")


def test_tambien_cuando_no_le_llega(client):
    r = client.post(P, json={"importe": 250, "concepto": "un móvil"}).json()
    assert not r["alcanza"] and r["frase_comida"]


def test_si_la_compra_es_de_la_comida_no_lo_dice(client):
    r = client.post(P, json={"importe": 20, "concepto": "el pan", "hucha": "comida"}).json()
    assert r["frase_comida"] is None and "comida está aparte" not in r["texto_lectura_facil"]

"""Límites del dinero (app/limites.py): sin negativos, aviso a partir de 1.000 € al día, máximo 1.000.000 €."""

from app import limites
from app.store import store

URL = "/api/personas/javi"


def quedan(client, hucha="mis_cosas"):
    return next(h["quedan"] for h in client.get(f"{URL}/presupuesto").json()["huchas"] if h["id"] == hucha)


def test_pago_que_deja_la_hucha_en_negativo_no_se_apunta(client):
    r = client.post(f"{URL}/decisiones", json={"concepto": "una tele", "importe": 500,
                                               "decision": "comprar", "pagado": True})
    assert r.status_code == 409 and r.json()["error"] == "saldo_negativo"
    assert "Te faltan 290 €" in r.json()["texto_lectura_facil"]
    assert quedan(client) == 210
    assert client.get(f"{URL}/decisiones").json() == []  # tampoco se guarda la decisión


def test_quiero_comprar_algo_que_no_llega_no_se_apunta(client):
    r = client.post(f"{URL}/decisiones", json={"concepto": "una tele", "importe": 500, "decision": "comprar"})
    assert r.status_code == 409
    assert client.get(f"{URL}/compras").json()["pendientes"] == []


def test_noa_dice_que_no_se_puede_si_no_llega(client):
    r = client.post(f"{URL}/evaluar_compra", json={"importe": 500, "concepto": "una tele"}).json()
    assert not r["alcanza"] and "no se puede" in r["texto_lectura_facil"]
    assert "Tú decides" not in r["texto_lectura_facil"]


def test_mas_de_un_millon_es_un_error(client):
    for ruta, cuerpo in [("evaluar_compra", {"importe": 2_000_000, "concepto": "un yate"}),
                         ("decisiones", {"concepto": "un yate", "importe": 2_000_000, "decision": "comprar"}),
                         ("evaluar_riesgo", {"destinatario": "Carlos", "importe": 5_000_000})]:
        r = client.post(f"{URL}/{ruta}", json=cuerpo)
        assert r.status_code == 422, ruta
        assert r.json()["texto_lectura_facil"].startswith("Error")


def test_mas_de_1000_euros_en_un_dia_avisa_siempre_al_circulo(client):
    gasto = {"registrado_por": "ana"}
    assert client.post(f"{URL}/gastos", json={**gasto, "texto": "600 euros de alquiler"}).json()["avisados_limite"] == []
    r = client.post(f"{URL}/gastos", json={**gasto, "texto": "500 euros de alquiler"}).json()
    assert r["avisados_limite"]  # 1.100 € hoy: se avisa
    avisos = client.get(f"{URL}/avisos?tipo=limite_diario").json()
    assert len(avisos) == 1 and "1.000 €" in avisos[0]["texto"]


def test_sin_nadie_en_el_circulo_no_se_puede_pasar_de_1000(client):
    javi = store.persona("javi")
    javi["circulo_apoyo"] = []
    try:
        limites.comprobar(javi, 1500, "alquiler", ya_pagado=True)
        assert False, "tenía que dar FueraDeLimite"
    except limites.FueraDeLimite as e:
        assert e.codigo == "limite_diario"


def test_pago_rechazado_avisa_a_ana_al_momento(client):
    r = client.post(f"{URL}/decisiones", json={"concepto": "una tele", "importe": 500,
                                               "decision": "comprar", "pagado": True}).json()
    assert r["avisados"] == ["Ana"] and "Se lo he dicho a Ana" in r["texto_lectura_facil"]
    yate = client.post(f"{URL}/evaluar_compra", json={"importe": 5_000_000, "concepto": "un yate"}).json()
    assert yate["avisados"] == ["Ana"]
    avisos = client.get(f"{URL}/avisos?para=ana&tipo=pago_no_permitido").json()
    assert len(avisos) == 2
    assert "le faltan 290 €" in avisos[1]["texto"] and "El importe no es válido" in avisos[0]["texto"]

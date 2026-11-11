"""Meter dinero en una hucha (viaje, móvil...): sale de "Para tus cosas" y nunca más de lo que queda."""

URL = "/api/personas/javi/metas/{}/meter"


def quedan_tus_cosas(client):
    huchas = client.get("/api/personas/javi/presupuesto").json()["huchas"]
    return next(h for h in huchas if h["id"] == "mis_cosas")["quedan"]


def meta(client, meta_id):
    return next(m for m in client.get("/api/personas/javi/metas").json() if m["id"] == meta_id)


def test_meter_dinero_sube_la_hucha_y_baja_tus_cosas(client):
    antes = quedan_tus_cosas(client)
    ahorrado = meta(client, "valencia")["ahorrado"]
    r = client.post(URL.format("valencia"), json={"importe": 20})
    assert r.status_code == 200
    assert meta(client, "valencia")["ahorrado"] == ahorrado + 20
    assert quedan_tus_cosas(client) == antes - 20
    assert r.json()["quedan"] == antes - 20
    assert "Has metido 20 €" in r.json()["texto_lectura_facil"]


def test_no_se_puede_meter_mas_de_lo_que_queda(client):
    antes = quedan_tus_cosas(client)
    # A la hucha del viaje le faltan 180 €: más de lo que queda (210 €) no cabe en ninguna.
    r = client.post(URL.format("valencia"), json={"importe": antes + 1})
    assert r.status_code == 400
    assert quedan_tus_cosas(client) == antes


def test_no_se_puede_meter_mas_de_lo_que_le_falta(client):
    falta = meta(client, "movil")["falta"]
    r = client.post(URL.format("movil"), json={"importe": falta + 1})
    assert r.status_code == 400
    assert "le faltan" in r.json()["detail"]
    assert client.post(URL.format("movil"), json={"importe": falta}).status_code == 200
    assert meta(client, "movil")["falta"] == 0
    assert client.post(URL.format("movil"), json={"importe": 1}).status_code == 400


def test_importe_cero_o_hucha_que_no_existe(client):
    assert client.post(URL.format("valencia"), json={"importe": 0}).status_code == 422
    assert client.post(URL.format("no_existe"), json={"importe": 5}).status_code == 404


def test_meter_en_la_hucha_no_es_un_gasto(client):
    """En el banco el dinero sigue siendo de Javi: el total no cambia, pasa de saldo a ahorro.
    Tampoco sale como compra pagada ni como gasto en el informe."""
    from app import report
    from app.store import hoy, store

    antes = client.get("/api/personas/javi/cuenta").json()
    informe_antes = report.resumen(store.persona("javi"), hoy().year)
    client.post(URL.format("valencia"), json={"importe": 30})
    despues = client.get("/api/personas/javi/cuenta").json()
    assert despues["total"] == antes["total"]
    assert despues["saldo"] == antes["saldo"] - 30
    assert despues["ahorro"] == antes["ahorro"] + 30
    pagadas = client.get("/api/personas/javi/compras").json()["pagadas"]
    assert not any("hucha" in c["concepto"].lower() for c in pagadas)
    informe = report.resumen(store.persona("javi"), hoy().year)
    assert informe["total_gastos"] == informe_antes["total_gastos"]
    assert informe["saldo_final"] == informe_antes["saldo_final"]
    assert informe["traspasado_a_ahorro"] == informe_antes["traspasado_a_ahorro"] + 30

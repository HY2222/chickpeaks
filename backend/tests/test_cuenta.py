"""La app del banco (pantalla 0) enseña los mismos gastos que Willo."""


def cuenta(client):
    return client.get("/api/personas/javi/cuenta").json()


def test_la_cuenta_sale_de_los_movimientos_de_willo(client):
    c = cuenta(client)
    assert len(c["movimientos"]) == 6
    fechas = [m["fecha"] for m in c["movimientos"]]
    assert fechas == sorted(fechas, reverse=True)
    conceptos = [m["concepto"] for m in c["movimientos"]]
    assert "Bar con amigos" in conceptos


def test_pagar_en_willo_sale_en_el_banco(client):
    antes = cuenta(client)["saldo"]
    client.post("/api/personas/javi/decisiones",
                json={"concepto": "la entrada del concierto", "importe": 45, "decision": "comprar", "pagado": True})
    c = cuenta(client)
    assert c["saldo"] == antes - 45
    assert c["movimientos"][0]["concepto"] == "La entrada del concierto"
    assert c["movimientos"][0]["importe"] == 45


def test_el_banco_y_willo_dicen_lo_mismo_del_ahorro(client):
    c = cuenta(client)
    metas = client.get("/api/personas/javi/metas").json()
    assert c["ahorro"] == sum(m["ahorrado"] for m in metas)
    assert c["saldo"] == c["total"] - c["ahorro"]
    informe = client.get("/api/personas/javi/informe_anual/resumen").json()
    assert c["total"] == informe["saldo_final"]


def test_crear_hucha_nueva(client):
    r = client.post("/api/personas/javi/metas", json={"nombre": "Bici", "importe": 120})
    assert r.status_code == 200
    m = r.json()
    assert m["nombre"] == "Bici" and m["ahorrado"] == 0 and m["importe"] == 120
    assert m["aporte_mensual"] == 20 and m["meses_restantes"] == 6
    nombres = [x["nombre"] for x in client.get("/api/personas/javi/metas").json()]
    assert nombres[-1] == "Bici"
    # Mismo nombre otra vez: no se duplica
    assert client.post("/api/personas/javi/metas", json={"nombre": "bici", "importe": 50}).status_code == 409
    # Un importe que no tiene sentido no se acepta
    assert client.post("/api/personas/javi/metas", json={"nombre": "Nada", "importe": 0}).status_code == 422
    assert client.post("/api/personas/javi/metas", json={"nombre": "  ", "importe": 10}).status_code == 400

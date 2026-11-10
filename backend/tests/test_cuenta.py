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

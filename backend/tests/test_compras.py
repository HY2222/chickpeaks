"""Compras: decidir comprar no baja el dinero; pagar sí. Lo decidido caduca a los 7 días."""


def quedan(client):
    pres = client.get("/api/personas/javi/presupuesto").json()
    return next(h for h in pres["huchas"] if h["id"] == "mis_cosas")["quedan"]


def decidir(client, concepto="la entrada del concierto", importe=45, **extra):
    return client.post("/api/personas/javi/decisiones",
                       json={"concepto": concepto, "importe": importe, "decision": "comprar", **extra}).json()


def compras(client):
    return client.get("/api/personas/javi/compras").json()


def test_decidir_comprar_no_baja_el_dinero(client):
    antes = quedan(client)
    r = decidir(client)
    assert quedan(client) == antes
    assert r["compra_pendiente"]["concepto"] == "la entrada del concierto"
    assert "no baja todavía" in r["texto_lectura_facil"]
    c = compras(client)
    assert [p["importe"] for p in c["pendientes"]] == [45]
    assert c["pendientes"][0]["dias_restantes"] == 7
    assert all(p["concepto"] != "La entrada del concierto" for p in c["pagadas"])
    av = client.get("/api/personas/javi/avisos?para=ana").json()
    assert av[0]["texto"] == "Javi ha decidido comprar la entrada del concierto. Lo decidió él."


def test_pagar_baja_el_dinero_una_sola_vez(client):
    antes = quedan(client)
    decidir(client, "entrada del concierto")           # lo dice a Noa
    decidir(client, "la entrada del concierto")        # lo repite: no se apunta dos veces
    assert len(compras(client)["pendientes"]) == 1
    decidir(client, "la entrada del concierto", pagado=True)   # paga en la taquilla
    assert quedan(client) == antes - 45
    c = compras(client)
    assert c["pendientes"] == []
    assert c["pagadas"][0] == {"concepto": "La entrada del concierto", "importe": 45,
                               "fecha": c["pagadas"][0]["fecha"]}


def test_marcar_pagada_desde_la_lista(client):
    antes = quedan(client)
    cid = decidir(client, "las zapatillas", 80)["compra_pendiente"]["id"]
    r = client.post(f"/api/personas/javi/compras/{cid}/pagada")
    assert r.status_code == 200
    assert quedan(client) == antes - 80
    assert compras(client)["pendientes"] == []
    assert client.post(f"/api/personas/javi/compras/{cid}/pagada").status_code == 404


def test_quitar_no_cambia_el_dinero(client):
    antes = quedan(client)
    cid = decidir(client, "las zapatillas", 80)["compra_pendiente"]["id"]
    assert client.delete(f"/api/personas/javi/compras/{cid}").status_code == 200
    assert quedan(client) == antes
    assert compras(client)["pendientes"] == []
    assert client.delete(f"/api/personas/javi/compras/{cid}").status_code == 404


def test_caduca_a_los_siete_dias(client, monkeypatch):
    from datetime import timedelta
    from app.store import hoy
    antes = quedan(client)
    decidir(client, "las zapatillas", 80)
    base = hoy()
    monkeypatch.setenv("WILLO_HOY", (base + timedelta(days=7)).isoformat())
    assert len(compras(client)["pendientes"]) == 1      # el último día todavía está
    monkeypatch.setenv("WILLO_HOY", (base + timedelta(days=8)).isoformat())
    assert compras(client)["pendientes"] == []
    monkeypatch.setenv("WILLO_HOY", base.isoformat())
    assert quedan(client) == antes

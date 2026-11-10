"""Tests de /documentos/confirmar. Aquí no hay IA: todo son cuentas del código.

Datos de la demo (datos-ejemplo.md): a Javi le quedan 210 € para sus cosas.
"""

from app.store import store

URL = "/api/personas/javi/documentos/confirmar"
MULTA = {"tipo": "multa", "titulo": "Multa de aparcamiento", "remitente": "Ayuntamiento",
         "importe": 90.0, "fecha_limite": "2026-12-20", "sospechoso": False}


def confirmar(client, **cambios):
    r = client.post(URL, json={**MULTA, **cambios})
    assert r.status_code == 200, r.text
    return r.json()


def quedan_mis_cosas(client):
    pres = client.get("/api/personas/javi/presupuesto").json()
    return next(h for h in pres["huchas"] if h["id"] == "mis_cosas")["quedan"]


def test_multa_como_el_contrato(client):
    # En el contrato, Javi ya se ha comprado la entrada del concierto (45 €): le quedan 165 €.
    client.post("/api/personas/javi/decisiones",
                json={"concepto": "entrada del concierto", "importe": 45, "decision": "comprar",
                      "pagado": True})
    r = confirmar(client)
    assert r["en_plan"] is False
    assert (r["quedan_antes"], r["quedan_despues"], r["alcanza"]) == (165.0, 75.0, True)
    assert r["pictograma"] == "coche"
    assert r["texto_lectura_facil"] == ("No estaba en tu plan. Si la pagas, te quedan 75 € para tus cosas. "
                                        "Tienes hasta el 20 de diciembre. ¿Quieres hablarlo con Ana?")


def test_confirmar_no_paga_nada(client):
    confirmar(client)
    assert quedan_mis_cosas(client) == 210


def test_no_alcanza_no_recomienda(client):
    r = confirmar(client, tipo="factura", titulo="Factura del dentista", remitente="Clínica", importe=250)
    assert r["alcanza"] is False and r["quedan_despues"] == -40
    assert "Te faltan 40 €." in r["texto_lectura_facil"]
    texto = r["texto_lectura_facil"].lower()
    assert "deberías" not in texto and "no pagues" not in texto


def test_ticket_con_tarjeta_ya_apuntado(client):
    r = confirmar(client, tipo="ticket", titulo="Ticket de la tienda de ropa", remitente="Tienda de ropa",
                  importe=30, fecha_limite=None)
    assert r["texto_lectura_facil"] == ("Es el ticket de la tienda de ropa. Pagaste 30 €. Ya está apuntado. "
                                        "Te quedan 210 € para tus cosas.")
    assert r["apuntado"] is False
    assert quedan_mis_cosas(client) == 210  # no se resta dos veces


def test_ticket_en_efectivo_se_apunta_una_vez(client):
    ticket = dict(tipo="ticket", titulo="Ticket del quiosco", remitente="Quiosco", importe=8.5, fecha_limite=None)
    r = confirmar(client, **ticket)
    assert r["apuntado"] is True and r["quedan_despues"] == 201.5
    assert "Lo he apuntado para tus cosas. Te quedan 201,50 €." in r["texto_lectura_facil"]
    assert quedan_mis_cosas(client) == 201.5
    # Si confirma el mismo ticket otra vez, ya está y no se apunta dos veces.
    assert confirmar(client, **ticket)["apuntado"] is False
    assert quedan_mis_cosas(client) == 201.5


def test_luz_ya_en_el_plan(client):
    r = confirmar(client, tipo="factura", titulo="Factura de la luz", remitente="Compañía de la luz",
                  importe=42, fecha_limite="2026-11-20")
    assert r["en_plan"] is True and r["quedan_despues"] == 210
    assert r["pictograma"] == "luz"
    assert r["texto_lectura_facil"] == "Ya estaba en tu plan. Se paga solo el día 20. No tienes que hacer nada."


def test_luz_un_poco_mas_cara_sigue_en_el_plan(client):
    assert confirmar(client, tipo="factura", titulo="Factura de la luz", remitente="Iberdrola", importe=45)["en_plan"]


def test_luz_mucho_mas_cara_no_esta_en_el_plan(client):
    r = confirmar(client, tipo="factura", titulo="Factura de la luz", remitente="Compañía de la luz", importe=80)
    assert r["en_plan"] is False and r["quedan_despues"] == 130


def test_mismo_importe_pero_otra_cosa_no_esta_en_el_plan(client):
    assert not confirmar(client, tipo="factura", titulo="Gimnasio", remitente="Gym Centro", importe=42)["en_plan"]


def test_sospechoso_no_hace_cuentas(client):
    r = confirmar(client, tipo="carta_banco", titulo="Carta del banco", remitente="Banco",
                  importe=None, sospechoso=True)
    assert r["sospechoso"] is True
    assert r["quedan_antes"] is None and r["quedan_despues"] is None and r["alcanza"] is None
    assert r["pictograma"] == "aviso"
    assert r["texto_lectura_facil"].startswith("Cuidado.")
    assert "Tú decides" in r["texto_lectura_facil"]


def test_carta_sin_dinero(client):
    r = confirmar(client, tipo="carta_banco", titulo="Carta del banco", remitente="Banco",
                  importe=None, fecha_limite=None)
    assert r["texto_lectura_facil"] == "En este papel no hay que pagar nada. ¿Quieres hablarlo con Ana?"


def test_nomina_es_dinero_que_entra(client):
    r = confirmar(client, tipo="nomina", titulo="Nómina de noviembre", remitente="Fundación", importe=980,
                  fecha_limite=None)
    assert r["texto_lectura_facil"] == "Es tu nómina. Te pagan 980 €. No tienes que pagar nada."
    assert quedan_mis_cosas(client) == 210


def test_sin_permiso_no_pregunta_por_ana(client):
    store.persona("javi")["circulo_apoyo"] = []
    assert "Ana" not in confirmar(client)["texto_lectura_facil"]


def test_datos_malos_dan_422(client):
    assert client.post(URL, json={**MULTA, "importe": -5}).status_code == 422
    assert client.post(URL, json={**MULTA, "tipo": "pizza"}).status_code == 422
    assert client.post(URL, json={**MULTA, "titulo": "   "}).status_code == 422
    assert client.post(URL, json={**MULTA, "fecha_limite": "20/12/2026"}).status_code == 422


def test_mensaje_sin_remitente_dice_que_no_se_sabe_quien_es(client):
    r = client.post("/api/personas/javi/documentos/confirmar", json={
        "tipo": "mensaje", "titulo": "Mensaje", "texto_mensaje": "Hazme un bizum urgente"}).json()
    assert not any("esa persona" in s for s in r["senales"])
    assert any("No se ve quién te lo pide" in s for s in r["senales"])
    # Confirmar dos veces el mismo mensaje no crea otro aviso para Ana.
    client.post("/api/personas/javi/documentos/confirmar", json={
        "tipo": "mensaje", "titulo": "Mensaje", "texto_mensaje": "Hazme un bizum urgente"})
    assert len(client.get("/api/personas/javi/avisos?tipo=posible_estafa").json()) == 1

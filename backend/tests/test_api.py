from app.easyread import comprobar, euros, fernandez_huerta, silabas
from app.expenses import interpretar


def test_presupuesto(client):
    r = client.get("/api/personas/javi/presupuesto").json()
    mis_cosas = next(h for h in r["huchas"] if h["id"] == "mis_cosas")
    assert mis_cosas["quedan"] == 120  # 150 - camiseta de 30


def test_zapatillas_alcanza(client):
    r = client.post("/api/personas/javi/evaluar_compra", json={"importe": 80, "concepto": "las zapatillas"}).json()
    assert r["quedan_antes"] == 120 and r["quedan_despues"] == 40 and r["alcanza"]
    assert "te quedan 40 €" in r["texto_lectura_facil"]
    assert "Tú decides" in r["texto_lectura_facil"]
    assert comprobar(r["texto_lectura_facil"])["es_facil"]


def test_no_alcanza_no_recomienda(client):
    r = client.post("/api/personas/javi/evaluar_compra", json={"importe": 200, "concepto": "un móvil"}).json()
    assert not r["alcanza"]
    assert "Te faltan 80 €" in r["texto_lectura_facil"]
    assert "no deberías" not in r["texto_lectura_facil"].lower()


def test_decision_compra_avisa_a_ana(client):
    r = client.post("/api/personas/javi/decisiones",
                    json={"concepto": "zapatillas", "importe": 80, "decision": "comprar",
                          "palabras_persona": "Sí, las quiero"}).json()
    assert "Ana" in r["avisados"]
    av = client.get("/api/personas/javi/avisos?para=ana").json()
    assert av[0]["texto"] == "Javi compró zapatillas. Lo decidió él."
    pres = client.get("/api/personas/javi/presupuesto").json()
    assert next(h for h in pres["huchas"] if h["id"] == "mis_cosas")["quedan"] == 40


def test_decision_no_compartida(client):
    client.post("/api/personas/javi/decisiones",
                json={"concepto": "un regalo", "importe": 20, "decision": "comprar", "compartir": False})
    assert client.get("/api/personas/javi/avisos").json() == []


def test_estafa_avisa_pero_no_bloquea(client):
    r = client.post("/api/personas/javi/evaluar_riesgo", json={
        "destinatario": "Marcos", "importe": 200,
        "contexto": "Un amigo nuevo de Instagram me pide 200 euros urgente y que no se lo digas a nadie"}).json()
    assert r["nivel_riesgo"] == "alto" and r["bloquea"] is False
    assert r["avisados"] == ["Ana"]  # la fundación no consintió avisos
    ids = {s["id"] for s in r["senales"]}
    assert {"destinatario_nuevo", "urgencia", "secreto", "relacion_nueva"} <= ids


def test_pago_normal(client):
    r = client.post("/api/personas/javi/evaluar_riesgo",
                    json={"destinatario": "Supermercado del barrio", "importe": 30}).json()
    assert r["nivel_riesgo"] == "bajo" and r["avisados"] == []


def test_palabra_pin_no_salta_con_pintura(client):
    r = client.post("/api/personas/javi/evaluar_riesgo",
                    json={"destinatario": "Tienda de ropa", "importe": 10, "contexto": "es para pintura"}).json()
    assert "codigos" not in {s["id"] for s in r["senales"]}


def test_circulo_persona_retira_apoyo(client):
    r = client.put("/api/personas/javi/circulo/ana", json={"nivel": 0})
    assert r.status_code == 200
    client.post("/api/personas/javi/decisiones", json={"concepto": "x", "importe": 5, "decision": "comprar"})
    assert client.get("/api/personas/javi/avisos?para=ana").json() == []


def test_circulo_documento_no_se_cambia_desde_app(client):
    assert client.put("/api/personas/javi/circulo/fundacion", json={"nivel": 0}).status_code == 403


def test_apoyar_no_puede_registrar_gastos(client):
    # Ana es "Guardar" (N3) en la demo. Con "Apoyar" (N2) no puede apuntar gastos.
    assert client.put("/api/personas/javi/circulo/ana", json={"nivel": 2}).status_code == 200
    r = client.post("/api/personas/javi/gastos", json={"texto": "45 euros de luz", "registrado_por": "ana"})
    assert r.status_code == 403


def test_curadora_registra_gasto_y_genera_informe(client):
    r = client.post("/api/personas/javi/gastos",
                    json={"texto": "He pagado 45 euros de luz de Javi", "registrado_por": "fundacion"}).json()
    assert r["importe"] == 45 and r["hucha"] == "casa"
    pdf = client.get("/api/personas/javi/informe_anual?preparado_por=fundacion")
    assert pdf.status_code == 200 and pdf.content[:4] == b"%PDF"
    # Ana es "Guardar" (N3): puede preparar el informe. Con "Apoyar" (N2), no.
    assert client.get("/api/personas/javi/informe_anual?preparado_por=ana").status_code == 200
    client.put("/api/personas/javi/circulo/ana", json={"nivel": 2})
    assert client.get("/api/personas/javi/informe_anual?preparado_por=ana").status_code == 403


def test_resumen_cuadra(client):
    r = client.get("/api/personas/javi/informe_anual/resumen").json()
    assert r["saldo_final"] == round(r["saldo_inicial"] + r["total_ingresos"] - r["total_gastos"], 2)
    assert r["total_ingresos"] == 11 * 1070  # enero a noviembre


def test_pausa_para_pensar(client):
    client.post("/api/personas/javi/pausa", json={"activa": True, "desde_importe": 50})
    r = client.post("/api/personas/javi/evaluar_compra", json={"importe": 80, "concepto": "las zapatillas"}).json()
    assert r["pausa_para_pensar"] and "pausa para pensar" in r["texto_lectura_facil"]


def test_meta_menor(client):
    m = client.get("/api/personas/lucia/metas").json()[0]
    assert m["falta"] == 125 and m["meses_restantes"] == 5


def test_interpretar_gastos():
    assert interpretar("45,50 € del supermercado")["hucha"] == "comida"
    assert interpretar("He pagado 12 euros de cine")["importe"] == 12


def test_lectura_facil():
    assert silabas("casa") == 2 and silabas("día") == 2 and silabas("bueno") == 2 and silabas("zapatillas") == 4
    assert euros(80.0) == "80 €" and euros(12.5) == "12,50 €"
    facil = "Te quedan 40 €. Tú decides."
    dificil = ("La operación solicitada excede el límite disponible en la subcuenta asignada a gastos "
               "discrecionales, por lo que recomendamos reconsiderar la adquisición propuesta.")
    assert fernandez_huerta(facil) > fernandez_huerta(dificil)
    assert not comprobar(dificil)["es_facil"]


def test_pwa_instalable(client):
    sw = client.get("/sw.js")
    assert sw.status_code == 200 and "javascript" in sw.headers["content-type"]
    m = client.get("/static/manifest-persona.webmanifest").json()
    assert m["display"] == "standalone" and m["start_url"] == "/demo"
    assert {i["sizes"] for i in m["icons"]} == {"192x192", "512x512"}
    assert 'rel="manifest"' in client.get("/demo").text

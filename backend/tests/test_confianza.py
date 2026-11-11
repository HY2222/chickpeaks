"""Perfil de Javi: sus personas de confianza (puede haber varias). A ellas les llegan los avisos."""

URL = "/api/personas/javi"


def circulo(client):
    return {m["nombre"]: m for m in client.get(f"{URL}/circulo").json()}


def de_confianza(client):
    return sorted(n for n, m in circulo(client).items() if "recibir_avisos_estafa" in m["permisos"])


def pago_rechazado(client):
    return client.post(f"{URL}/decisiones", json={"concepto": "una tele", "importe": 500,
                                                  "decision": "comprar", "pagado": True}).json()["avisados"]


def test_anadir_a_alguien_nuevo_y_ana_sigue(client):
    r = client.post(f"{URL}/confianza", json={"nombre": "marta", "telefono": "+34 600 000 102"})
    assert r.status_code == 200 and "Ana y Marta" in r.json()["texto_lectura_facil"]
    assert de_confianza(client) == ["Ana", "Marta"]          # "marta" se guarda como "Marta"
    assert sorted(pago_rechazado(client)) == ["Ana", "Marta"]  # el aviso les llega a las dos


def test_marcar_y_desmarcar(client):
    client.post(f"{URL}/confianza", json={"nombre": "Marta"})
    ids = {n: m["id"] for n, m in circulo(client).items()}
    r = client.put(f"{URL}/confianza", json={"ids": [ids["Marta"]]})
    assert r.status_code == 200 and de_confianza(client) == ["Marta"]
    assert circulo(client)["Ana"]["nivel"] == 3               # Ana sigue siendo "Guardar"
    assert pago_rechazado(client) == ["Marta"]                # pero ya no le llegan los avisos
    client.put(f"{URL}/confianza", json={"ids": [ids["Ana"]]})
    assert de_confianza(client) == ["Ana"] and circulo(client)["Marta"]["nivel"] == 0


def test_al_menos_una_persona(client):
    assert client.put(f"{URL}/confianza", json={"ids": []}).status_code == 422
    assert client.put(f"{URL}/confianza", json={"ids": ["nadie"]}).status_code == 404
    assert client.post(f"{URL}/confianza", json={"nombre": "  "}).status_code == 422


def test_reiniciar_deja_solo_a_ana(client):
    client.post(f"{URL}/confianza", json={"nombre": "Marta"})
    client.put(f"{URL}/confianza", json={"ids": ["marta"]})
    assert client.post(f"{URL}/confianza/reiniciar").status_code == 200
    assert list(circulo(client)) == ["Ana"] and de_confianza(client) == ["Ana"]

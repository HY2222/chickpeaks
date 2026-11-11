"""Perfil de Javi: elegir su persona de confianza (a ella le llegan los avisos)."""

URL = "/api/personas/javi"


def circulo(client):
    return {m["nombre"]: m for m in client.get(f"{URL}/circulo").json()}


def test_elegir_a_alguien_nuevo_recibe_los_avisos(client):
    r = client.post(f"{URL}/confianza", json={"nombre": "Marta", "telefono": "+34 600 000 102", "relacion": "amiga"})
    assert r.status_code == 200 and "Marta" in r.json()["texto_lectura_facil"]
    c = circulo(client)
    assert c["Marta"]["confianza"] and not c["Ana"]["confianza"]
    assert "recibir_avisos_estafa" in c["Marta"]["permisos"]
    # Un pago que no se puede: el aviso le llega a Marta.
    avisados = client.post(f"{URL}/decisiones", json={"concepto": "una tele", "importe": 500,
                                                      "decision": "comprar", "pagado": True}).json()["avisados"]
    assert "Marta" in avisados


def test_elegir_a_alguien_del_circulo_no_lo_duplica(client):
    client.post(f"{URL}/confianza", json={"nombre": "Marta"})
    client.post(f"{URL}/confianza", json={"nombre": "ana"})
    c = circulo(client)
    assert len(c) == 2 and c["Ana"]["confianza"]
    assert c["Ana"]["nivel"] == 3          # un apoyo de nivel Guardar no baja
    assert c["Marta"]["nivel"] == 0        # la anterior, que dio Javi, deja de recibir avisos


def test_nombre_vacio_no_vale(client):
    assert client.post(f"{URL}/confianza", json={"nombre": "  "}).status_code == 422

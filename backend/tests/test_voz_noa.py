"""Las pantallas hablan con la voz de Noa (ElevenLabs) y, si falla, con la del navegador."""
import httpx


def test_sin_clave_avisa_para_usar_la_voz_del_navegador(client, monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    assert client.post("/api/voz/decir", json={"texto": "Hola"}).status_code == 503


def test_devuelve_el_audio_de_noa(client, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "clave-de-prueba")
    pedido = {}

    async def falso_post(self, url, **kw):
        pedido.update(url=url, **kw)
        return httpx.Response(200, content=b"mp3")

    monkeypatch.setattr(httpx.AsyncClient, "post", falso_post)
    r = client.post("/api/voz/decir", json={"texto": "Te quedan 165 €."})
    assert r.status_code == 200 and r.content == b"mp3"
    assert r.headers["content-type"] == "audio/mpeg"
    assert pedido["url"].endswith("/text-to-speech/dNjJKg63Fr5AXwIdkATa")
    assert pedido["json"]["text"] == "Te quedan 165 €."


def test_si_elevenlabs_falla_da_error(client, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "clave-de-prueba")

    async def falso_post(self, url, **kw):
        return httpx.Response(401)

    monkeypatch.setattr(httpx.AsyncClient, "post", falso_post)
    assert client.post("/api/voz/decir", json={"texto": "Hola"}).status_code == 502


def test_voz_de_hombre_y_velocidad_a_elegir(client, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "clave-de-prueba")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID_MASCULINA", "voz-de-hombre")
    pedido = {}

    async def falso_post(self, url, **kw):
        pedido.update(url=url, **kw)
        return httpx.Response(200, content=b"mp3")

    monkeypatch.setattr(httpx.AsyncClient, "post", falso_post)
    r = client.post("/api/voz/decir", json={"texto": "Hola", "voz": "masculina", "velocidad": 1.15})
    assert r.status_code == 200
    assert pedido["url"].endswith("/text-to-speech/voz-de-hombre")
    assert pedido["json"]["voice_settings"]["speed"] == 1.15
    # Una velocidad que ElevenLabs no admite no se acepta
    assert client.post("/api/voz/decir", json={"texto": "Hola", "velocidad": 3}).status_code == 422
    assert client.post("/api/voz/decir", json={"texto": "Hola", "voz": "robot"}).status_code == 422


def test_la_url_firmada_trae_las_dos_voces(client, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "clave-de-prueba")
    monkeypatch.setenv("ELEVENLABS_AGENT_ID", "agente")

    async def falso_get(self, url, **kw):
        return httpx.Response(200, json={"signed_url": "wss://x"})

    monkeypatch.setattr(httpx.AsyncClient, "get", falso_get)
    r = client.get("/api/voz/signed-url").json()
    assert r["signed_url"] == "wss://x"
    assert set(r["voces"]) == {"femenina", "masculina"}

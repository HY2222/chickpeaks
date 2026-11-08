"""API de Willo.

Las rutas de /api/personas/{id}/... son las herramientas que usa Noa,
el agente de voz de ElevenLabs (ver agent/tools.json), y las pantallas del frontend.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Literal

import httpx
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import budget, easyread, expenses, report, risk, support
from .notify import avisar
from .store import hoy, store

app = FastAPI(title="Willo API", version="0.1.0",
              description="Your will, your money. Demo con datos inventados.")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("WILLO_CORS", "*").split(","),
                   allow_methods=["*"], allow_headers=["*"])

STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def token_herramientas(x_willo_token: str | None = Header(default=None)) -> None:
    """Si WILLO_TOOL_TOKEN está definido, las llamadas deben traer la cabecera X-Willo-Token."""
    esperado = os.getenv("WILLO_TOOL_TOKEN")
    if esperado and x_willo_token != esperado:
        raise HTTPException(401, "Token incorrecto")


def _persona(persona_id: str) -> dict:
    p = store.persona(persona_id)
    if p is None:
        raise HTTPException(404, f"No existe la persona {persona_id}")
    return p


def _miembro(p: dict, miembro_id: str) -> dict:
    m = support.miembro(p, miembro_id)
    if m is None:
        raise HTTPException(404, f"{miembro_id} no está en el círculo de apoyo")
    return m


# ---------- Modelos ----------

class Compra(BaseModel):
    importe: float = Field(gt=0, examples=[80])
    concepto: str = Field(examples=["las zapatillas"])
    hucha: str | None = Field(default=None, description="id de la hucha; por defecto mis_cosas")


class Decision(BaseModel):
    concepto: str = Field(examples=["las zapatillas"])
    importe: float = Field(ge=0, examples=[80])
    decision: Literal["comprar", "esperar", "hablarlo"]
    palabras_persona: str = Field(default="", description="Lo que dijo la persona, con sus palabras")
    pidio_apoyo: bool = False
    compartir: bool = Field(default=True, description="Si la persona quiere que lo vea su círculo (N1+)")
    hucha: str | None = None


class Pago(BaseModel):
    destinatario: str = Field(examples=["Marcos"])
    importe: float = Field(gt=0, examples=[200])
    contexto: str = Field(default="", description="Lo que la persona cuenta sobre el pago",
                          examples=["Un amigo nuevo de Instagram me pide 200 euros urgente para un billete"])


class GastoDictado(BaseModel):
    texto: str = Field(examples=["He pagado 45 euros de luz de Javi"])
    registrado_por: str = Field(examples=["fundacion"])


class CambioNivel(BaseModel):
    nivel: int = Field(ge=0, le=2)


class Pausa(BaseModel):
    activa: bool
    desde_importe: float = 50.0


class Texto(BaseModel):
    texto: str


# ---------- Persona ----------

@app.get("/api/personas")
def personas():
    return [{"id": p["id"], "nombre": p["nombre"], "tipo": p["tipo"]} for p in store.personas.values()]


@app.get("/api/personas/{persona_id}/presupuesto", dependencies=[Depends(token_herramientas)])
def presupuesto(persona_id: str):
    """Herramienta de Noa: cuánto queda en cada hucha este mes."""
    p = _persona(persona_id)
    huchas = budget.estado_huchas(p)
    frases = [f"En {h['nombre'].lower()} te quedan {easyread.euros(h['quedan'])}." for h in huchas]
    return {"persona": p["nombre"], "fecha": hoy().isoformat(), "huchas": huchas,
            "texto_lectura_facil": " ".join(frases)}


@app.post("/api/personas/{persona_id}/evaluar_compra", dependencies=[Depends(token_herramientas)])
def evaluar_compra(persona_id: str, compra: Compra):
    """Herramienta de Noa: ¿puedo comprarlo? Da cifras, no recomienda."""
    p = _persona(persona_id)
    try:
        r = budget.evaluar_compra(p, compra.importe, compra.concepto, compra.hucha)
    except KeyError:
        raise HTTPException(400, f"No existe la hucha {compra.hucha}")
    pausa = p.get("pausa_para_pensar")
    r["pausa_para_pensar"] = bool(pausa and pausa["activa"] and compra.importe >= pausa["desde_importe"])
    if r["pausa_para_pensar"]:
        r["texto_lectura_facil"] += " Tú activaste la pausa para pensar. ¿Lo miramos otra vez en 10 minutos?"
    return r


@app.post("/api/personas/{persona_id}/decisiones", dependencies=[Depends(token_herramientas)])
def registrar_decision(persona_id: str, d: Decision):
    """Herramienta de Noa: guarda lo que decidió la persona. La app respeta la decisión."""
    p = _persona(persona_id)
    ahora = datetime.combine(hoy(), datetime.now().time()).isoformat(timespec="seconds")
    reg = {**d.model_dump(), "fecha": ahora}
    p["decisiones"].append(reg)
    if d.decision == "comprar" and d.importe > 0:
        hucha = budget.buscar_hucha(p, d.hucha)["id"]
        p["movimientos"].append({"fecha": hoy().isoformat(), "concepto": d.concepto.capitalize(),
                                 "importe": d.importe, "tipo": "gasto", "hucha": hucha,
                                 "destinatario": None, "registrado_por": "persona"})
    avisados = []
    if d.compartir:
        verbo = {"comprar": "compró", "esperar": "decidió esperar para comprar", "hablarlo": "quiere hablar de"}[d.decision]
        texto = f"{p['nombre']} {verbo} {d.concepto}. Lo decidió {p.get('pronombre', 'él')}."
        if d.decision == "hablarlo":
            texto = f"{p['nombre']} quiere hablar contigo de {d.concepto}."
        for m in support.con_permiso(p, "ver_decisiones"):
            avisados.append(avisar(p, m, "decision", texto))
    return {"guardado": reg, "avisados": [a["para_nombre"] for a in avisados],
            "texto_lectura_facil": "Lo he apuntado. Es tu decisión."}


@app.get("/api/personas/{persona_id}/decisiones")
def ver_decisiones(persona_id: str):
    return _persona(persona_id)["decisiones"]


@app.post("/api/personas/{persona_id}/evaluar_riesgo", dependencies=[Depends(token_herramientas)])
def evaluar_riesgo(persona_id: str, pago: Pago):
    """Herramienta de Noa: escudo antiestafas. Nunca bloquea."""
    p = _persona(persona_id)
    r = risk.evaluar_pago(p, pago.destinatario, pago.importe, pago.contexto)
    r["avisados"] = []
    if r["sugerir_aviso_apoyo"]:
        texto = (f"Aviso de Willo: puede que alguien esté intentando engañar a {p['nombre']}. "
                 f"Le piden {easyread.euros(pago.importe)} para {pago.destinatario}. "
                 f"Señales: {'; '.join(s['explicacion'] for s in r['senales'])}. "
                 f"La decisión es suya. Llámale con calma.")
        for m in support.con_permiso(p, "recibir_avisos_abuso"):
            avisar(p, m, "posible_abuso", texto)
            r["avisados"].append(m["nombre"])
        if r["avisados"]:
            r["texto_lectura_facil"] += f" Como acordaste, he avisado a {' y '.join(r['avisados'])}."
    return r


@app.get("/api/personas/{persona_id}/metas")
def metas(persona_id: str):
    """Perfil de menores: metas de ahorro."""
    return [budget.progreso_meta(m) for m in _persona(persona_id).get("metas", [])]


@app.post("/api/personas/{persona_id}/pausa")
def pausa_para_pensar(persona_id: str, pausa: Pausa):
    """La activa la propia persona (N2). No bloquea: solo propone esperar."""
    p = _persona(persona_id)
    p["pausa_para_pensar"] = pausa.model_dump()
    return p["pausa_para_pensar"]


# ---------- Círculo de apoyo ----------

@app.get("/api/personas/{persona_id}/circulo")
def circulo(persona_id: str):
    return support.describir(_persona(persona_id))


@app.put("/api/personas/{persona_id}/circulo/{miembro_id}")
def cambiar_nivel(persona_id: str, miembro_id: str, cambio: CambioNivel):
    """La persona da, cambia o retira (nivel 0) un apoyo que dio ella."""
    p = _persona(persona_id)
    try:
        return support.cambiar_nivel(p, miembro_id, cambio.nivel)
    except KeyError:
        raise HTTPException(404, "No está en el círculo")
    except (PermissionError, ValueError) as e:
        raise HTTPException(403, str(e))


@app.get("/api/personas/{persona_id}/avisos")
def avisos(persona_id: str, para: str | None = None):
    av = _persona(persona_id)["avisos"]
    return [a for a in av if para is None or a["para"] == para][::-1]


@app.post("/api/personas/{persona_id}/gastos")
def registrar_gasto(persona_id: str, g: GastoDictado):
    """Persona de apoyo (N3+): apunta un gasto dictado. El texto viene de Scribe."""
    p = _persona(persona_id)
    m = _miembro(p, g.registrado_por)
    if not support.puede(m, "registrar_gastos"):
        raise HTTPException(403, f"{m['nombre']} no tiene permiso para registrar gastos")
    try:
        gasto = expenses.interpretar(g.texto)
    except ValueError as e:
        raise HTTPException(422, str(e))
    mov = {"fecha": hoy().isoformat(), "concepto": gasto["concepto"], "importe": gasto["importe"],
           "tipo": "gasto", "hucha": gasto["hucha"], "destinatario": None,
           "registrado_por": m["nombre"], "texto_original": g.texto}
    p["movimientos"].append(mov)
    return mov


@app.post("/api/gastos/transcribir")
async def transcribir(audio: UploadFile = File(...)):
    """Transcribe un audio con ElevenLabs Scribe. Necesita ELEVENLABS_API_KEY."""
    key = os.getenv("ELEVENLABS_API_KEY")
    if not key:
        raise HTTPException(503, "Falta ELEVENLABS_API_KEY en .env")
    contenido = await audio.read()
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post("https://api.elevenlabs.io/v1/speech-to-text",
                         headers={"xi-api-key": key},
                         data={"model_id": os.getenv("ELEVENLABS_STT_MODEL", "scribe_v1"),
                               "language_code": "spa"},
                         files={"file": (audio.filename or "audio.webm", contenido,
                                         audio.content_type or "audio/webm")})
    if r.status_code >= 400:
        raise HTTPException(502, f"Scribe respondió {r.status_code}: {r.text[:200]}")
    return {"texto": r.json().get("text", "")}


@app.get("/api/personas/{persona_id}/informe_anual")
def informe_anual(persona_id: str, preparado_por: str, anio: int | None = None):
    """PDF de rendición de cuentas para el juzgado (N3+)."""
    p = _persona(persona_id)
    m = _miembro(p, preparado_por)
    if not support.puede(m, "preparar_rendicion_cuentas"):
        raise HTTPException(403, f"{m['nombre']} no tiene permiso para preparar la rendición de cuentas")
    anio = anio or hoy().year
    pdf = report.generar_pdf(p, m, anio)
    nombre = f"rendicion_cuentas_{p['id']}_{anio}.pdf"
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{nombre}"'})


@app.get("/api/personas/{persona_id}/informe_anual/resumen")
def informe_resumen(persona_id: str, anio: int | None = None):
    return report.resumen(_persona(persona_id), anio or hoy().year)


# ---------- Utilidades ----------

@app.post("/api/lectura_facil/comprobar")
def comprobar_lectura_facil(t: Texto):
    return easyread.comprobar(t.texto)


@app.get("/api/voz/signed-url")
async def signed_url():
    """URL firmada para hablar con Noa sin exponer la API key en el navegador."""
    key, agent = os.getenv("ELEVENLABS_API_KEY"), os.getenv("ELEVENLABS_AGENT_ID")
    if not key or not agent:
        raise HTTPException(503, "Faltan ELEVENLABS_API_KEY o ELEVENLABS_AGENT_ID en .env")
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get("https://api.elevenlabs.io/v1/convai/conversation/get-signed-url",
                        params={"agent_id": agent}, headers={"xi-api-key": key})
    if r.status_code >= 400:
        raise HTTPException(502, f"ElevenLabs respondió {r.status_code}")
    return r.json()


@app.post("/api/demo/reset")
def reset():
    store.reset()
    return {"ok": True}


@app.get("/demo")
def demo_persona():
    return FileResponse(STATIC / "persona.html")


@app.get("/demo/apoyo")
def demo_apoyo():
    return FileResponse(STATIC / "apoyo.html")


@app.get("/")
def raiz():
    return {"app": "Willo", "lema": "Your will, your money", "docs": "/docs",
            "demo_persona": "/demo", "demo_apoyo": "/demo/apoyo"}

"""API de Willo.

Las rutas de /api/personas/{id}/... son las herramientas que usa Noa,
el agente de voz de ElevenLabs (ver agent/tools.json), y las pantallas del frontend.
"""

from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path
from typing import Literal

import httpx
from fastapi.concurrency import run_in_threadpool
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import budget, documents, easyread, expenses, notify, purchases, report, risk, support
from .notify import avisar
from .store import hoy, store

# Carga las claves del archivo .env de la raíz del repo. No pisa variables que ya existan.
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

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
    pagado: bool = Field(default=False, description="Solo con decision 'comprar': true si ya lo ha pagado. "
                         "Si es false, se apunta en 'Quiero comprar' y el dinero no baja todavía.")


class Pago(BaseModel):
    destinatario: str = Field(examples=["Marcos"])
    importe: float = Field(gt=0, examples=[200])
    contexto: str = Field(default="", description="Lo que la persona cuenta sobre el pago",
                          examples=["Un amigo nuevo de Instagram me pide 200 euros urgente para un billete"])
    telefono: str | None = Field(default=None, description="Número de quien pide el dinero, si se sabe",
                                 examples=["+34 611 222 333"])


class GastoDictado(BaseModel):
    texto: str = Field(examples=["He pagado 45 euros de luz de Javi"])
    registrado_por: str = Field(examples=["fundacion"])


class CambioNivel(BaseModel):
    nivel: int = Field(ge=0, le=2)


class Pausa(BaseModel):
    activa: bool
    desde_importe: float = 50.0


class DocumentoConfirmado(BaseModel):
    """Lo que leyó Noa, ya revisado por la persona (pantalla 6)."""
    tipo: Literal["factura", "recibo", "ticket", "nomina", "multa", "carta_banco", "mensaje", "otro"]
    titulo: str = Field(min_length=1, examples=["Multa de aparcamiento"])
    remitente: str | None = Field(default=None, examples=["Ayuntamiento"])
    importe: float | None = Field(default=None, ge=0, examples=[90.0])
    fecha_limite: date | None = Field(default=None, examples=["2026-12-20"])
    texto_mensaje: str | None = Field(default=None, max_length=documents.MAX_TEXTO_MENSAJE,
                                      description="Solo si tipo es mensaje: lo que escribe la otra persona",
                                      examples=["Hola, soy Carlos. Dame 300 euros"])
    telefono: str | None = Field(default=None, max_length=30, examples=["+34 611 222 333"])
    sospechoso: bool = False


class ResultadoEnvio(BaseModel):
    enviado: bool = Field(description="true si Javi envió el dinero, false si no")


class Contacto(BaseModel):
    nombre: str = Field(min_length=1, max_length=80, examples=["Ana"])
    telefono: str = Field(max_length=30, examples=["+34 600 000 101"])


class ListaContactos(BaseModel):
    """Los contactos que Javi elige en su agenda (Contact Picker del navegador)."""
    contactos: list[Contacto] = Field(max_length=2000)


class Texto(BaseModel):
    texto: str


# ---------- Persona ----------

@app.get("/api/personas")
def personas():
    return [{"id": p["id"], "nombre": p["nombre"], "tipo": p["tipo"], "telefono": telefono(p)}
            for p in store.personas.values()]


def telefono(p: dict) -> str | None:
    """El número de verdad va en .env (WILLO_TELEFONO_JAVI), no en el repo, que es público."""
    return os.getenv(f"WILLO_TELEFONO_{p['id'].upper()}") or p.get("telefono")


@app.get("/api/personas/{persona_id}/presupuesto", dependencies=[Depends(token_herramientas)])
def presupuesto(persona_id: str):
    """Herramienta de Noa: cuánto queda en cada hucha este mes."""
    p = _persona(persona_id)
    huchas = budget.estado_huchas(p)
    # Javi solo piensa en lo que puede gastar. Casa, comida y ahorro ya están apartados.
    frases = [f"Te quedan {easyread.euros(h['quedan'])} para {budget.nombre_en_frase(h)}."
              for h in huchas if h["id"] not in ("casa", "comida", "ahorro")]
    if any(g["hucha"] in ("casa", "comida") for g in p.get("gastos_recurrentes", [])):
        frases.append("Lo de casa y comida ya está guardado.")
    return {"persona": p["nombre"], "fecha": hoy().isoformat(), "huchas": huchas,
            "texto_lectura_facil": " ".join(frases)}


@app.get("/api/personas/{persona_id}/pagos_del_mes", dependencies=[Depends(token_herramientas)])
def pagos_del_mes(persona_id: str):
    """Herramienta de Noa: qué pagos fijos hay este mes y si ya se han pagado. Willo no paga nada."""
    return budget.pagos_del_mes(_persona(persona_id))


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
    pendiente = None
    if d.decision == "comprar" and d.importe > 0:
        hucha = budget.buscar_hucha(p, d.hucha)["id"]
        if d.pagado:
            # Ya está pagado: el dinero baja ahora. Si estaba en "Quiero comprar", sale de ahí.
            purchases.pagar(p, d.concepto, d.importe, hucha)
        else:
            # Solo lo ha decidido: se apunta en "Quiero comprar". El dinero baja cuando lo pague.
            pendiente = purchases.apuntar(p, d.concepto, d.importe, hucha)
    avisados = []
    if d.compartir:
        comprar = "compró" if d.pagado else "ha decidido comprar"
        verbo = {"comprar": comprar, "esperar": "decidió esperar para comprar", "hablarlo": "quiere hablar de"}[d.decision]
        texto = f"{p['nombre']} {verbo} {d.concepto}. Lo decidió {p.get('pronombre', 'él')}."
        if d.decision == "hablarlo":
            texto = f"{p['nombre']} quiere hablar contigo de {d.concepto}."
        for m in support.con_permiso(p, "ver_decisiones"):
            avisados.append(avisar(p, m, "decision", texto))
    texto = "Lo he apuntado. Es tu decisión."
    if pendiente:
        texto = ("Lo he apuntado en Quiero comprar. Tu dinero no baja todavía. "
                 "Baja cuando lo pagues. Es tu decisión.")
    return {"guardado": reg, "avisados": [a["para_nombre"] for a in avisados],
            "compra_pendiente": pendiente, "texto_lectura_facil": texto}


@app.get("/api/personas/{persona_id}/compras")
def ver_compras(persona_id: str):
    """Pantalla de Javi: lo que ha decidido comprar (aún sin pagar) y lo que ya ha pagado este mes.

    Las compras decididas caducan solas a los 7 días si no se pagan."""
    p = _persona(persona_id)
    return {"pendientes": purchases.pendientes(p), "pagadas": purchases.pagadas_este_mes(p),
            "dias_caducidad": purchases.DIAS_CADUCIDAD}


@app.get("/api/personas/{persona_id}/cuenta")
def ver_cuenta(persona_id: str, ultimos: int = 6):
    """Pantalla 0 (la app del banco): saldo de la cuenta y últimos movimientos.

    Sale de los mismos movimientos que usa Willo, así el banco y Willo enseñan siempre
    los mismos gastos. Los traspasos a la hucha de ahorro no cuentan como gasto,
    pero sí salen de la cuenta corriente."""
    p = _persona(persona_id)
    movs = p["movimientos"]
    entra = sum(m["importe"] for m in movs if m["tipo"] == "ingreso")
    sale = sum(m["importe"] for m in movs if m["tipo"] != "ingreso")
    ahorro = sum(m["importe"] for m in movs if m["tipo"] != "ingreso" and m.get("hucha") == "ahorro")
    recientes = sorted(reversed(movs), key=lambda m: m["fecha"], reverse=True)[:max(1, min(ultimos, 20))]
    return {
        "saldo": round(p.get("saldo_inicial_anio", 0.0) + entra - sale, 2),
        "ahorro_este_anio": round(ahorro, 2),
        "movimientos": [{"fecha": m["fecha"], "concepto": m["concepto"], "destinatario": m.get("destinatario"),
                         "importe": m["importe"], "tipo": m["tipo"]} for m in recientes],
    }


@app.post("/api/personas/{persona_id}/compras/{compra_id}/pagada")
def compra_pagada(persona_id: str, compra_id: str):
    """Javi ya ha pagado algo que tenía en "Quiero comprar": pasa a pagado y el dinero baja.
    Willo no paga nada: solo lo apunta (en la app real lo diría el banco)."""
    p = _persona(persona_id)
    c = purchases.buscar(p, compra_id)
    if not c:
        raise HTTPException(404, "Esa compra no está en Quiero comprar")
    purchases.pagar(p, c["concepto"], c["importe"], c["hucha"], compra_id=compra_id)
    return {"ok": True, "texto_lectura_facil": f"Apuntado. Has pagado {easyread.euros(c['importe'])}."}


@app.delete("/api/personas/{persona_id}/compras/{compra_id}")
def quitar_compra(persona_id: str, compra_id: str):
    """Javi ya no quiere comprarlo: sale de "Quiero comprar". El dinero no cambia."""
    p = _persona(persona_id)
    if not purchases.quitar(p, compra_id):
        raise HTTPException(404, "Esa compra no está en Quiero comprar")
    return {"ok": True, "texto_lectura_facil": "Lo he quitado. Tu dinero sigue igual."}


@app.get("/api/personas/{persona_id}/decisiones")
def ver_decisiones(persona_id: str):
    return _persona(persona_id)["decisiones"]


@app.post("/api/personas/{persona_id}/documentos/leer")
async def leer_documento(persona_id: str, foto: UploadFile = File(...)):
    """Pantallas 5-6: Noa lee la foto de un documento. Solo copia lo que pone; no hace cuentas.

    La imagen no se guarda. Javi tiene que confirmar lo leído antes de usarlo (/documentos/confirmar).
    """
    p = _persona(persona_id)
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(503, "Falta ANTHROPIC_API_KEY en .env")
    contenido = await foto.read()
    try:
        return await run_in_threadpool(documents.leer, contenido, foto.content_type, p)
    except documents.FormatoNoValido:
        return JSONResponse(status_code=415, content={
            "error": "formato_no_valido",
            "texto_lectura_facil": "Eso no es una foto. Haz una foto del papel."})
    except documents.NoLegible:
        return JSONResponse(status_code=422, content={
            "error": "no_legible", "pictograma": "documento",
            "texto_lectura_facil": documents.TEXTO_NO_LEGIBLE})
    except Exception as e:  # fallo de red o de la API de Claude
        if type(e).__module__.startswith("anthropic"):
            raise HTTPException(502, f"Claude no ha respondido bien: {type(e).__name__}")
        raise
    finally:
        del contenido  # la foto no se queda en el servidor


@app.post("/api/personas/{persona_id}/documentos/confirmar")
def confirmar_documento(persona_id: str, doc: DocumentoConfirmado):
    """Pantalla 7: Javi confirmó lo leído. El código hace las cuentas con su hucha de "mis cosas".

    No paga nada, no recomienda y no bloquea. Solo apunta un gasto si es un ticket
    pagado en efectivo (el banco no lo sabe). "Hablar con Ana" usa POST /decisiones.
    """
    p = _persona(persona_id)
    datos = doc.model_dump()
    datos["titulo"] = datos["titulo"].strip()
    if not datos["titulo"]:
        raise HTTPException(422, "Falta el título del documento")
    datos["fecha_limite"] = doc.fecha_limite.isoformat() if doc.fecha_limite else None
    if doc.tipo == "mensaje":
        # Las reglas antiestafa (código) revisan el mensaje otra vez, con lo que Javi confirmó.
        # Si el riesgo es alto, se crea el mismo aviso para Ana que en la pantalla 8.
        datos["riesgo"] = _riesgo_y_aviso(p, Pago(destinatario=doc.remitente or "esa persona",
                                                  importe=doc.importe or 0.01,
                                                  contexto=doc.texto_mensaje or "",
                                                  telefono=doc.telefono))
        datos["sospechoso"] = doc.sospechoso or datos["riesgo"]["nivel_riesgo"] != "bajo"
    return documents.confirmar(p, datos)


@app.post("/api/personas/{persona_id}/evaluar_riesgo", dependencies=[Depends(token_herramientas)])
def evaluar_riesgo(persona_id: str, pago: Pago):
    """Herramienta de Noa: escudo antiestafas. Nunca bloquea.

    Si el riesgo es alto y Javi dio permiso, crea UN solo aviso para su círculo y devuelve su id.
    Si se evalúa otra vez el mismo envío (Noa y la pantalla, o dos veces seguidas), usa el mismo aviso.
    """
    p = _persona(persona_id)
    r = _riesgo_y_aviso(p, pago)
    if r["avisados"]:
        r["texto_lectura_facil"] += f" Como acordaste, he avisado a {' y '.join(r['avisados'])}."
    return r


def _riesgo_y_aviso(p: dict, pago: Pago) -> dict:
    """Reglas antiestafa + un solo aviso al círculo si el riesgo es alto. Lo usan la voz y la foto."""
    r = risk.evaluar_pago(p, pago.destinatario, pago.importe, pago.contexto, pago.telefono)
    r["bloquea"] = False  # la decisión siempre es de la persona
    r["aviso_id"], r["avisados"] = None, []
    miembros = support.con_permiso(p, "recibir_avisos_estafa")
    if r["sugerir_aviso_apoyo"] and miembros:
        aviso = _aviso_abierto(p, pago) or _crear_aviso_estafa(p, pago, r, miembros)
        r["aviso_id"], r["avisados"] = aviso["id"], aviso["para_nombres"]
    return r


def _crear_aviso_estafa(p: dict, pago: Pago, r: dict, miembros: list[dict], antes: str = "") -> dict:
    texto = (f"{antes}Aviso de Willo: puede que alguien esté intentando engañar a {p['nombre']}. "
             f"Le piden {easyread.euros(pago.importe)} para {pago.destinatario}. "
             f"Señales: {'; '.join(s['explicacion'] for s in r['senales'])}. "
             f"La decisión es suya. Llámale con calma.")
    return avisar(p, miembros, "posible_estafa", texto, destinatario=pago.destinatario,
                  importe=float(pago.importe), senales=[s["explicacion"] for s in r["senales"]])


def _aviso_abierto(p: dict, pago: Pago) -> dict | None:
    """Un aviso de estafa de hoy, al mismo destinatario y por el mismo importe, que aún no tiene resultado."""
    hoy_iso = hoy().isoformat()
    for a in reversed(p["avisos"]):
        if (a["tipo"] == "posible_estafa" and a["fecha"].startswith(hoy_iso) and a["resultado"] is None
                and a.get("destinatario", "").strip().lower() == pago.destinatario.strip().lower()
                and a.get("importe") == float(pago.importe)):
            return a
    return None


# ---------- Contactos del móvil ----------
# Solo los que la persona elige en su agenda. Se guarda nombre y número, nada más.
# Sirven para una cosa: saber si quien pide dinero es alguien que conoce. Nunca se mandan a la IA.

@app.get("/api/personas/{persona_id}/contactos")
def ver_contactos(persona_id: str):
    return _persona(persona_id).get("contactos", [])


@app.post("/api/personas/{persona_id}/contactos")
def guardar_contactos(persona_id: str, lista: ListaContactos):
    """Añade los contactos elegidos. Si un número ya estaba, se queda el nombre nuevo."""
    p = _persona(persona_id)
    por_numero = {risk.numero(c["telefono"]): c for c in p.setdefault("contactos", [])}
    nuevos = 0
    for c in lista.contactos:
        n = risk.numero(c.telefono)
        if len(n) < 9:
            continue  # no es un número de teléfono
        nuevos += n not in por_numero
        por_numero[n] = {"nombre": c.nombre.strip(), "telefono": c.telefono.strip()}
    p["contactos"] = list(por_numero.values())
    total = len(p["contactos"])
    return {"nuevos": nuevos, "total": total,
            "texto_lectura_facil": (f"Tengo {total} contactos tuyos. "
                                    "Así sé si te escribe alguien que no conoces.")}


@app.delete("/api/personas/{persona_id}/contactos")
def borrar_contactos(persona_id: str):
    """La persona puede borrar todos sus contactos de Willo cuando quiera."""
    _persona(persona_id)["contactos"] = []
    return {"total": 0, "texto_lectura_facil": "He borrado tus contactos de Willo. Los de tu móvil siguen igual."}


@app.delete("/api/personas/{persona_id}/contactos/{telefono}")
def borrar_contacto(persona_id: str, telefono: str):
    p = _persona(persona_id)
    antes = len(p.get("contactos", []))
    p["contactos"] = [c for c in p.get("contactos", []) if risk.numero(c["telefono"]) != risk.numero(telefono)]
    if len(p["contactos"]) == antes:
        raise HTTPException(404, "Ese número no está en tus contactos de Willo")
    return {"total": len(p["contactos"])}


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
def avisos(persona_id: str, para: str | None = None, tipo: str | None = None):
    """Avisos al círculo, lo más nuevo primero. Filtros: ?para=ana y ?tipo=posible_estafa."""
    av = _persona(persona_id)["avisos"]
    return [a for a in av
            if (para is None or notify.es_para(a, para)) and (tipo is None or a["tipo"] == tipo)][::-1]


def _aviso(p: dict, aviso_id: str) -> dict:
    a = notify.buscar(p, aviso_id)
    if a is None:
        raise HTTPException(404, f"No existe el aviso {aviso_id}")
    return a


@app.post("/api/personas/{persona_id}/avisos/pedir_hablar")
def pedir_hablar_de_un_envio(persona_id: str, pago: Pago):
    """Pantalla 8, botón "Avisar a Ana", cuando todavía no hay aviso (riesgo medio).

    Con riesgo medio no se avisa a nadie solo: el aviso se crea cuando Javi pulsa el botón.
    Si ya había un aviso de este mismo envío (riesgo alto), se usa ese. Nunca hay dos.
    """
    p = _persona(persona_id)
    a = _aviso_abierto(p, pago)
    if a:
        return {**_pide_hablar(p, a), "creado": False}
    # Javi lo pide él: basta con que la persona pueda ver sus decisiones (nivel Ver o más).
    miembros = (support.con_permiso(p, "recibir_avisos_estafa")
                or support.con_permiso(p, "ver_decisiones"))
    if not miembros:
        raise HTTPException(409, "No hay nadie en el círculo de apoyo para avisar")
    r = risk.evaluar_pago(p, pago.destinatario, pago.importe, pago.contexto, pago.telefono)
    a = _crear_aviso_estafa(p, pago, r, miembros, antes=f"{p['nombre']} ha pedido hablar contigo. ")
    return {**_pide_hablar(p, a, mandar=False), "creado": True}  # el mensaje ya ha salido al crearlo


@app.post("/api/personas/{persona_id}/avisos/{aviso_id}/pedir_hablar")
def pedir_hablar(persona_id: str, aviso_id: str):
    """Pantalla 8, botón "Avisar a Ana". No crea otro aviso: cambia el que ya hay."""
    p = _persona(persona_id)
    return _pide_hablar(p, _aviso(p, aviso_id))


def _pide_hablar(p: dict, a: dict, mandar: bool = True) -> dict:
    texto = f"{p['nombre']} ha pedido hablar contigo."
    if a["estado"] != "javi_pide_hablar":  # pulsar dos veces no manda dos mensajes
        a["estado"] = "javi_pide_hablar"
        a["fecha_pide_hablar"] = notify.ahora()
        if mandar:
            notify.mandar_otra_vez(p, a, texto)
    nombres = " y ".join(a["para_nombres"])
    llamara = "Te llamará." if len(a["para_nombres"]) == 1 else "Te llamarán."
    return {"id": a["id"], "estado": a["estado"], "texto": texto,
            "texto_lectura_facil": f"Se lo he dicho a {nombres}. {llamara}"}


@app.post("/api/personas/{persona_id}/avisos/{aviso_id}/resultado")
def resultado_aviso(persona_id: str, aviso_id: str, r: ResultadoEnvio):
    """Pantalla 8: Javi pulsó "No enviar" o "Enviar igualmente". Se apunta igual, sin juzgar."""
    a = _aviso(_persona(persona_id), aviso_id)
    a["resultado"] = {"enviado": r.enviado}
    a["fecha_resultado"] = notify.ahora()
    return {"id": a["id"], "estado": a["estado"], "resultado": a["resultado"],
            "texto_lectura_facil": "Lo he apuntado. Es tu decisión."}


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
    if gasto["hucha"] not in {h["id"] for h in p["huchas"]}:
        gasto["hucha"] = "mis_cosas"  # p. ej. "cine": Javi no tiene hucha de ocio, va a sus cosas
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


@app.post("/api/voz/decir")
async def decir_con_voz_de_noa(t: Texto):
    """Lee un texto con la voz de Noa (ElevenLabs). Lo usan las pantallas cuando no hay conversación de voz abierta.

    Si falta la clave o ElevenLabs falla, devuelve un error y la pantalla usa la voz del navegador.
    """
    key = os.getenv("ELEVENLABS_API_KEY")
    if not key:
        raise HTTPException(503, "Falta ELEVENLABS_API_KEY en .env")
    texto = t.texto.strip()[:800]
    if not texto:
        raise HTTPException(422, "No hay texto")
    voz = os.getenv("ELEVENLABS_VOICE_ID", "dNjJKg63Fr5AXwIdkATa")  # la voz de Noa
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voz}",
                         params={"output_format": "mp3_44100_128"},
                         headers={"xi-api-key": key},
                         json={"text": texto, "model_id": os.getenv("ELEVENLABS_TTS_MODEL", "eleven_flash_v2_5"),
                               "language_code": "es"})
    if r.status_code >= 400:
        raise HTTPException(502, f"ElevenLabs respondió {r.status_code}")
    return Response(r.content, media_type="audio/mpeg")


@app.post("/api/demo/reset")
def reset():
    store.reset()
    return {"ok": True}


@app.get("/sw.js")
def service_worker():
    """El service worker va en la raíz para que la PWA controle toda la app."""
    return FileResponse(STATIC / "sw.js", media_type="application/javascript",
                        headers={"Cache-Control": "no-cache"})


@app.get("/demo/banco")
def demo_banco():
    """Pantalla 0: maqueta de la app de MyInvestor (patrocinador), con Willo dentro."""
    return FileResponse(STATIC / "banco.html")


@app.get("/demo")
def demo_persona():
    return FileResponse(STATIC / "persona.html")


@app.get("/demo/apoyo")
def demo_apoyo():
    return FileResponse(STATIC / "apoyo.html")


@app.get("/")
def raiz():
    return {"app": "Willo", "lema": "Your will, your money", "docs": "/docs",
            "demo_banco": "/demo/banco", "demo_persona": "/demo", "demo_apoyo": "/demo/apoyo"}

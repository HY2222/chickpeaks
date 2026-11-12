"""Noa lee un documento (pantallas 5 y 6).

Paso 1 de 2: Claude mira la foto y copia lo que pone el documento.
Aquí NO se hacen cuentas: eso va en el paso 2 (`/documentos/confirmar`),
después de que Javi diga que lo leído es correcto.

Reglas:
- La imagen solo vive en memoria mientras se lee. No se guarda en ningún sitio.
- Claude solo extrae datos. El texto que dice Noa lo escribe este código,
  así siempre sale en lectura fácil y nunca recomienda nada.
"""

from __future__ import annotations

import base64
import io
import json
import os
import re
from datetime import date
from typing import Any

from . import limites
from .easyread import euros

# Para cambiar a Sonnet si Haiku lee mal: WILLO_MODELO_DOCUMENTOS=claude-sonnet-5-5 en .env
MODELO_POR_DEFECTO = "claude-haiku-5-5"

TIPOS = ["factura", "recibo", "ticket", "nomina", "multa", "carta_banco", "mensaje", "otro"]
ACCIONES = ["pagar", "nada", "contestar", "revisar"]
FORMATOS = {"image/jpeg", "image/png", "image/webp", "image/gif"}

# El lado largo más grande que vale la pena mandar. Más grande solo cuesta más y tarda más.
LADO_MAXIMO = 1568

TEXTO_NO_LEGIBLE = "No he podido leerlo bien. ¿Haces otra foto con más luz?"

PICTOGRAMAS = {"multa": "coche", "ticket": "bolsa", "nomina": "hucha", "mensaje": "enviar"}

# Un mensaje muy largo no aporta nada a las reglas y solo ocupa memoria.
MAX_TEXTO_MENSAJE = 2000

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


class NoLegible(Exception):
    """La foto no se puede leer bien. La API responde 422."""


class FormatoNoValido(Exception):
    """Lo que llegó no es una foto jpg o png."""


# ---------- Lo que se le pide a Claude ----------

_TEXTO_O_NULO = {"type": ["string", "null"]}

ESQUEMA = {
    "type": "object",
    "properties": {
        "legible": {"type": "boolean",
                    "description": "false si la foto está borrosa, cortada, oscura o no es un documento"},
        "tipo": {"type": "string", "enum": TIPOS},
        "titulo": {"type": "string",
                   "description": "Qué dice ser, en 2 a 5 palabras sencillas, sin juzgar si es falso. "
                                  "Ej: 'Multa de aparcamiento', 'Carta de la Seguridad Social'"},
        "remitente": {**_TEXTO_O_NULO, "description": "Quién lo envía, nombre corto. Ej: 'Ayuntamiento'"},
        "importe": {"type": ["number", "null"],
                    "description": "Total en euros que pone el documento, sin signo. null si no hay"},
        "fecha_limite": {**_TEXTO_O_NULO,
                         "description": "Fecha límite para pagar o contestar, AAAA-MM-DD. null si no hay"},
        "accion": {"type": "string", "enum": ACCIONES},
        "telefono": {**_TEXTO_O_NULO,
                     "description": "Solo si es un mensaje y se ve el número de quien escribe. Si solo sale un nombre, null"},
        "texto_mensaje": {**_TEXTO_O_NULO,
                          "description": "Si es un mensaje, el texto que escribe la otra persona, tal cual. Si es una carta que "
                                         "pide datos, documentos o dinero, lo que pide, tal cual. Si no, null"},
        "sospechoso": {"type": "boolean"},
        "motivo_sospecha": {**_TEXTO_O_NULO,
                            "description": "Si es sospechoso, qué te pide o qué tiene de raro, en lectura fácil: "
                                           "una frase de 12 palabras como máximo, hablando de tú. "
                                           "Ej: 'Te pide tu DNI y datos del banco.' Si no, null"},
    },
    "required": ["legible", "tipo", "titulo", "remitente", "importe", "fecha_limite",
                 "accion", "telefono", "texto_mensaje", "sospechoso", "motivo_sospecha"],
    "additionalProperties": False,
}

INSTRUCCIONES = """Eres el lector de documentos de Willo, una app de dinero para personas con \
discapacidad intelectual. Te llega la foto de un papel (una factura, un recibo, un ticket de \
compra, una nómina, una multa, una carta del banco) o el pantallazo de un mensaje \
(WhatsApp, SMS, Instagram, correo).

Tu trabajo es SOLO copiar lo que pone. No hagas cuentas. No recomiendes nada. No inventes datos: \
si algo no aparece o no se lee, pon null.

- tipo: "ticket" es el ticket de algo que ya se compró (tienda, bar, supermercado). \
"recibo" es un cobro del banco ya hecho o programado (luz, agua, móvil). "factura" pide un pago. \
"mensaje" es un chat, SMS o correo de una persona o empresa.
- Si es un mensaje: remitente es el nombre de quien escribe; importe es el dinero que pide; \
texto_mensaje es lo que escribe, copiado tal cual; telefono es el número de arriba \
del chat si se ve (si sale un nombre guardado, null); accion es "pagar" si pide dinero.
- accion: "pagar" si hay que pagar; "nada" si ya está pagado (los tickets casi siempre); \
"contestar" si pide una respuesta; "revisar" si no está claro.
- importe: el total final que hay que pagar o que se pagó, en euros.
- sospechoso: true si pide claves, PIN, códigos SMS o datos de la tarjeta; si pide el DNI, \
fotos del DNI, extractos del banco, el número de cuenta u otros datos personales; si pide mandar \
documentos por correo o por mensaje (sobre todo a un correo normal como gmail, outlook o hotmail \
en nombre de un organismo oficial o un banco); si promete dinero, ayudas o subidas de prestaciones \
a cambio de datos; si habla de un "ataque informático" o de que se han perdido datos; si mete prisa \
con amenazas; si pide pagar por Bizum o transferencia a una persona; o si parece falso (faltas, \
formato raro, firma sin nombre). Ante la duda, pon true: es mejor avisar de más.
- texto_mensaje: también en cartas que piden algo (datos, documentos o dinero): copia lo que pide, tal cual.
- legible: false si no puedes leer bien el tipo o el importe."""


# ---------- Preparar la foto ----------

def preparar_imagen(contenido: bytes, media_type: str | None) -> tuple[bytes, str]:
    """Comprueba que es una foto y la hace más pequeña si hace falta. Todo en memoria."""
    from PIL import Image, ImageOps, UnidentifiedImageError

    if media_type not in FORMATOS:
        raise FormatoNoValido(media_type)
    try:
        img = Image.open(io.BytesIO(contenido))
        img.load()
    except (UnidentifiedImageError, OSError):
        raise NoLegible("La imagen no se puede abrir")
    if max(img.size) <= LADO_MAXIMO and len(contenido) < 4_000_000:
        return contenido, media_type
    img = ImageOps.exif_transpose(img)  # las fotos del móvil a veces vienen giradas
    img.thumbnail((LADO_MAXIMO, LADO_MAXIMO))
    salida = io.BytesIO()
    img.convert("RGB").save(salida, "JPEG", quality=85)
    return salida.getvalue(), "image/jpeg"


# ---------- Llamada a Claude ----------

def _llamar_claude(imagen: bytes, media_type: str) -> dict[str, Any]:
    """Manda la foto a Claude y devuelve el JSON del ESQUEMA. Los tests sustituyen esta función."""
    import anthropic

    cliente = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno
    respuesta = cliente.messages.create(
        model=os.getenv("WILLO_MODELO_DOCUMENTOS") or MODELO_POR_DEFECTO,
        max_tokens=1024,
        system=INSTRUCCIONES,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type,
                                         "data": base64.standard_b64encode(imagen).decode()}},
            {"type": "text", "text": "Lee este documento."},
        ]}],
        output_config={"format": {"type": "json_schema", "schema": ESQUEMA}},
    )
    texto = next(b.text for b in respuesta.content if b.type == "text")
    return json.loads(texto)


# ---------- Comprobar lo que devolvió Claude (lo hace el código) ----------

def _fecha(valor: Any) -> date | None:
    try:
        return date.fromisoformat(valor) if valor else None
    except (TypeError, ValueError):
        return None


def limpiar(datos: dict[str, Any]) -> dict[str, Any]:
    """No nos fiamos a ciegas: comprobamos cada campo. Si falta lo importante, NoLegible."""
    if not datos.get("legible") or not str(datos.get("titulo") or "").strip():
        raise NoLegible("Claude dice que no se lee bien")
    tipo = str(datos.get("tipo", "")).lower()
    accion = str(datos.get("accion", "")).lower()
    importe = datos.get("importe")
    if isinstance(importe, (int, float)) and not isinstance(importe, bool) and importe >= 0:
        importe = round(float(importe), 2)
    else:
        importe = None
    if importe is None and accion == "pagar":
        raise NoLegible("Hay que pagar pero no se lee cuánto")
    fecha = _fecha(datos.get("fecha_limite"))
    sospechoso = bool(datos.get("sospechoso"))
    tipo = tipo if tipo in TIPOS else "otro"
    texto_copiado = str(datos.get("texto_mensaje") or "").strip()[:MAX_TEXTO_MENSAJE] or None
    texto_mensaje = texto_copiado if tipo == "mensaje" else None
    telefono = str(datos.get("telefono") or "").strip()
    telefono = telefono if tipo == "mensaje" and sum(c.isdigit() for c in telefono) >= 9 else None
    return {
        "tipo": tipo,
        "titulo": str(datos["titulo"]).strip(),
        "remitente": (str(datos.get("remitente") or "").strip() or None),
        "importe": importe,
        "fecha_limite": fecha.isoformat() if fecha else None,
        "accion": accion if accion in ACCIONES else "revisar",
        "telefono": telefono,
        "texto_mensaje": texto_mensaje,
        "_texto_revision": texto_copiado,   # solo para las reglas antiestafa; no se guarda ni se devuelve
        "sospechoso": sospechoso,
        "motivo_sospecha": (str(datos.get("motivo_sospecha") or "").strip() or None) if sospechoso else None,
    }


# ---------- Lo que dice Noa ----------

def fecha_en_palabras(fecha_iso: str) -> str:
    """'2026-12-20' -> '20 de diciembre'."""
    f = date.fromisoformat(fecha_iso)
    return f"{f.day} de {MESES[f.month - 1]}"


def texto_leido(d: dict[str, Any]) -> str:
    """Frases cortas para la pantalla 6. Termina siempre preguntando si es correcto."""
    titulo = d["titulo"][0].lower() + d["titulo"][1:]
    frases = [f"He leído: {titulo}."]
    if d["tipo"] == "mensaje":
        if d["importe"] is not None:
            frases.append(f"Te pide {euros(d['importe'])}.")
        frases += _aviso(d)
        frases.append("¿Es correcto?")
        return " ".join(frases)
    if d["importe"] is not None:
        frases.append(f"{euros(d['importe'])}.")
    if d["accion"] == "pagar":
        frases.append(f"Hay que pagar antes del {fecha_en_palabras(d['fecha_limite'])}."
                      if d["fecha_limite"] else "Hay que pagarlo.")
    elif d["accion"] == "contestar":
        frases.append(f"Hay que contestar antes del {fecha_en_palabras(d['fecha_limite'])}."
                      if d["fecha_limite"] else "Hay que contestar.")
    elif d["accion"] == "nada" and d["tipo"] == "ticket":
        frases.append("Ya está pagado.")
    elif d["accion"] == "nada" and d["tipo"] == "recibo":
        frases.append("El banco lo cobra solo de tu cuenta. Tiene que haber dinero ese día.")
    frases += _aviso(d)
    frases.append("¿Es correcto?")
    return " ".join(frases)


def _aviso(d: dict[str, Any]) -> list[str]:
    """Si parece un engaño, Noa lo dice ya al leerlo, con el motivo si es corto."""
    if not d.get("sospechoso"):
        return []
    frases = ["Cuidado. Puede ser una estafa."]
    motivo = (d.get("motivo_sospecha") or "").strip()
    if motivo and len(motivo.split()) <= 15:
        frases.append(motivo if motivo.endswith((".", "!", "?")) else motivo + ".")
    return frases


def revisar_mensaje(persona: dict[str, Any], d: dict[str, Any]) -> dict[str, Any] | None:
    """Pasa las reglas antiestafa (las mismas que con la voz) por un mensaje. Es código, no IA.

    Una carta que pide algo (datos, documentos) también se revisa, pero solo con las reglas del texto:
    no tiene sentido hablar de "remitente desconocido" o de importes en un papel.
    """
    from . import risk
    if d["tipo"] != "mensaje":
        texto = d.get("_texto_revision")
        return risk.evaluar_texto(texto) if texto else None
    return risk.evaluar_pago(persona, d["remitente"], d["importe"] or 0.0,
                             d.get("texto_mensaje") or "", d.get("telefono"))


def leer(contenido: bytes, media_type: str | None, persona: dict[str, Any] | None = None) -> dict[str, Any]:
    """Foto -> datos del documento + texto de Noa. La foto no sale de esta función.

    Si es un mensaje, además de lo que diga Claude, lo revisan las reglas antiestafa.
    Basta con que uno de los dos vea peligro para marcarlo como sospechoso.
    """
    imagen, tipo_imagen = preparar_imagen(contenido, media_type)
    datos = limpiar(_llamar_claude(imagen, tipo_imagen))
    riesgo = revisar_mensaje(persona, datos) if persona else None
    datos.pop("_texto_revision", None)   # el texto de un papel no se guarda
    senales = [s["explicacion"] for s in riesgo["senales"]] if riesgo else []
    if riesgo and riesgo["nivel_riesgo"] != "bajo":
        datos["sospechoso"] = True
        datos["motivo_sospecha"] = datos["motivo_sospecha"] or senales[0]
    pictograma = "aviso" if datos["sospechoso"] else PICTOGRAMAS.get(datos["tipo"], "documento")
    return {**datos, "senales": senales, "pictograma": pictograma,
            "texto_lectura_facil": texto_leido(datos)}


# ======================================================================
# Paso 2: /documentos/confirmar (pantalla 7)
# Javi ya ha dicho "Sí, es correcto". Aquí el CÓDIGO hace las cuentas.
# No paga nada, no recomienda y no bloquea: solo explica.
# ======================================================================

def _normal(texto: str | None) -> str:
    """'Compañía de la Luz' -> 'compania de la luz'. Para comparar nombres sin tildes ni mayúsculas."""
    import unicodedata
    t = unicodedata.normalize("NFKD", (texto or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c)).strip()


_PALABRAS_VACIAS = {"de", "del", "la", "el", "los", "las", "y", "a", "en", "por", "para", "factura", "recibo"}


def _palabras(texto: str | None) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", _normal(texto)) if w not in _PALABRAS_VACIAS and len(w) > 2}


def _se_parecen(a: str | None, b: str | None) -> bool:
    """Comparten alguna palabra importante. 'Factura de la luz' y 'Luz' -> sí."""
    return bool(_palabras(a) & _palabras(b))


def _mismo_importe(a: float, b: float, margen: float = 0.0) -> bool:
    return abs(a - b) <= max(0.01, margen)


def buscar_en_plan(persona: dict[str, Any], d: dict[str, Any]) -> dict[str, Any] | None:
    """¿Es un gasto fijo que ya está en su plan (luz, alquiler...)?

    Coincide si el nombre se parece al del gasto fijo y el importe es casi igual.
    Margen del 10 %: las facturas de la luz cambian un poco cada mes.
    """
    if d["importe"] is None:
        return None
    for g in persona.get("gastos_recurrentes", []):
        nombre_ok = (_se_parecen(d["remitente"], g.get("destinatario"))
                     or _se_parecen(d["titulo"], g["concepto"])
                     or _se_parecen(d["remitente"], g["concepto"]))
        if nombre_ok and _mismo_importe(d["importe"], g["importe"], g["importe"] * 0.10):
            return g
    return None


def buscar_ticket(persona: dict[str, Any], d: dict[str, Any]) -> dict[str, Any] | None:
    """¿El ticket ya está en sus movimientos de este mes (pagó con tarjeta)?

    Basta con el mismo importe: el nombre de la tienda en el ticket y en el banco
    a veces no se parecen nada. Mejor no restarlo dos veces.
    """
    from .store import hoy
    mes = hoy().isoformat()[:7]
    for m in persona["movimientos"]:
        if (m["tipo"] == "gasto" and not m.get("meta") and m["fecha"][:7] == mes
                and _mismo_importe(m["importe"], d["importe"])):
            return m
    return None


def _quien_apoya(persona: dict[str, Any]) -> str | None:
    """El nombre de quien puede ver sus decisiones (Ana). Si Javi no ha dado permiso a nadie, nadie."""
    from . import support
    gente = support.con_permiso(persona, "ver_decisiones")
    return gente[0]["nombre"] if gente else None


def _pregunta_apoyo(persona: dict[str, Any]) -> list[str]:
    nombre = _quien_apoya(persona)
    return [f"¿Quieres hablarlo con {nombre}?"] if nombre else []


_FEMENINOS = {"multa", "factura", "nomina", "carta_banco"}


def confirmar(persona: dict[str, Any], d: dict[str, Any]) -> dict[str, Any]:
    """Datos ya confirmados por Javi -> cuentas y texto de Noa.

    Solo cambia algo en un caso: un ticket pagado en efectivo se apunta como gasto,
    porque el banco no lo sabe. Todo lo demás solo se explica.
    """
    from . import budget
    from .store import hoy

    mis_cosas = budget.buscar_hucha(persona, "mis_cosas")
    quedan = mis_cosas["quedan"]
    en_tus_cosas = f"para {budget.nombre_en_frase(mis_cosas)}"  # "para tus cosas"
    titulo = d["titulo"][0].lower() + d["titulo"][1:]
    base = {"en_plan": False, "quedan_antes": quedan, "quedan_despues": quedan, "alcanza": True,
            "apuntado": False, "sospechoso": False,
            "pictograma": PICTOGRAMAS.get(d["tipo"], "documento")}

    # 1. Sospechoso: no se hacen cuentas. Se explica el peligro. Javi decide.
    riesgo = d.get("riesgo")  # solo en mensajes: lo calcula la ruta con las reglas antiestafa
    if d["sospechoso"]:
        if d["tipo"] == "mensaje":
            senales = [s["explicacion"] for s in riesgo["senales"]] if riesgo else []
            frases = ["Cuidado. Este mensaje puede ser una estafa.", *senales[:3],
                      "Esto pasa a veces en las estafas.", "Tú decides qué hacer."]
        else:
            senales = []
            frases = ["Cuidado. Este papel puede ser una estafa.",
                      "Los bancos nunca te piden tu clave ni tu PIN.",
                      "Tú decides qué hacer."]
        avisados = (riesgo or {}).get("avisados") or []
        frases += ([f"Como acordaste, he avisado a {' y '.join(avisados)}."] if avisados
                   else _pregunta_apoyo(persona))
        return {**base, "sospechoso": True, "quedan_antes": None, "quedan_despues": None,
                "alcanza": None, "pictograma": "aviso", "senales": senales,
                "aviso_id": (riesgo or {}).get("aviso_id"), "avisados": avisados,
                "texto_lectura_facil": " ".join(frases)}

    # 2. Nómina: es dinero que entra, no que sale.
    if d["tipo"] == "nomina":
        frases = ["Es tu nómina."]
        if d["importe"] is not None:
            frases.append(f"Te pagan {euros(d['importe'])}.")
        frases.append("No tienes que pagar nada.")
        return {**base, "texto_lectura_facil": " ".join(frases)}

    # 3. Papel sin dinero (por ejemplo, una carta del banco que solo informa).
    if d["importe"] is None:
        frases = ["En este papel no hay que pagar nada."]
        if d["fecha_limite"]:
            frases.append(f"La fecha que pone es el {fecha_en_palabras(d['fecha_limite'])}.")
        frases += _pregunta_apoyo(persona)
        return {**base, "texto_lectura_facil": " ".join(frases)}

    importe = d["importe"]

    # 4. Ticket: ya está pagado. Solo se apunta si pagó en efectivo.
    if d["tipo"] == "ticket":
        empieza = "Es el " if _normal(titulo).startswith("ticket") else "Es un ticket: "
        frases = [f"{empieza}{titulo}.", f"Pagaste {euros(importe)}."]
        if buscar_ticket(persona, d):
            frases.append("Ya está apuntado.")
            frases.append(f"Te quedan {euros(quedan)} {en_tus_cosas}.")
            return {**base, "pictograma": "bolsa", "texto_lectura_facil": " ".join(frases)}
        limites.comprobar(persona, importe, d["titulo"], "mis_cosas")  # sin saldo o absurdo: no se apunta
        persona["movimientos"].append({
            "fecha": hoy().isoformat(), "concepto": d["titulo"], "importe": importe,
            "tipo": "gasto", "hucha": "mis_cosas", "destinatario": d["remitente"],
            "registrado_por": "persona"})
        despues = round(quedan - importe, 2)
        frases.append(f"Lo he apuntado {en_tus_cosas}.")
        frases.append(f"Te quedan {euros(despues)}.")
        return {**base, "quedan_despues": despues, "alcanza": despues >= 0, "apuntado": True,
                "pictograma": "bolsa", "texto_lectura_facil": " ".join(frases)}

    # 5. Gasto fijo que ya estaba en su plan (la luz, el alquiler...).
    fijo = buscar_en_plan(persona, d)
    if fijo:
        frases = ["Ya estaba en tu plan.",
                  f"Se paga solo el día {fijo['dia']}.",
                  "No tienes que hacer nada."]
        return {**base, "en_plan": True, "pictograma": fijo.get("pictograma", base["pictograma"]),
                "texto_lectura_facil": " ".join(frases)}

    # 6. Algo nuevo que pagar: se dice cuánto le queda si lo paga. No se paga nada.
    despues = round(quedan - importe, 2)
    lo = "la" if d["tipo"] in _FEMENINOS else "lo"
    frases = ["No estaba en tu plan."]
    if despues >= 0:
        frases.append(f"Si {lo} pagas, te quedan {euros(despues)} {en_tus_cosas}.")
    else:
        frases.append(f"Son {euros(importe)}.")
        frases.append(f"{en_tus_cosas.capitalize()} te quedan {euros(quedan)}.")
        frases.append(f"Te faltan {euros(-despues)}.")
    if d["fecha_limite"]:
        frases.append(f"Tienes hasta el {fecha_en_palabras(d['fecha_limite'])}.")
    frases += _pregunta_apoyo(persona)
    return {**base, "quedan_despues": despues, "alcanza": despues >= 0,
            "texto_lectura_facil": " ".join(frases)}

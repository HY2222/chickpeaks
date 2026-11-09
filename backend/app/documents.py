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
from datetime import date
from typing import Any

from .easyread import euros

# Para cambiar a Sonnet si Haiku lee mal: WILLO_MODELO_DOCUMENTOS=claude-sonnet-5-5 en .env
MODELO_POR_DEFECTO = "claude-haiku-5-5"

TIPOS = ["factura", "recibo", "ticket", "nomina", "multa", "carta_banco", "otro"]
ACCIONES = ["pagar", "nada", "contestar", "revisar"]
FORMATOS = {"image/jpeg", "image/png", "image/webp", "image/gif"}

# El lado largo más grande que vale la pena mandar. Más grande solo cuesta más y tarda más.
LADO_MAXIMO = 1568

TEXTO_NO_LEGIBLE = "No he podido leerlo bien. ¿Haces otra foto con más luz?"

PICTOGRAMAS = {"multa": "coche", "ticket": "bolsa", "nomina": "hucha"}

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
                   "description": "Qué es, en 2 a 5 palabras sencillas. Ej: 'Multa de aparcamiento'"},
        "remitente": {**_TEXTO_O_NULO, "description": "Quién lo envía, nombre corto. Ej: 'Ayuntamiento'"},
        "importe": {"type": ["number", "null"],
                    "description": "Total en euros que pone el documento, sin signo. null si no hay"},
        "fecha_limite": {**_TEXTO_O_NULO,
                         "description": "Fecha límite para pagar o contestar, AAAA-MM-DD. null si no hay"},
        "accion": {"type": "string", "enum": ACCIONES},
        "sospechoso": {"type": "boolean"},
        "motivo_sospecha": {**_TEXTO_O_NULO,
                            "description": "Si es sospechoso, por qué, en una frase corta. Si no, null"},
    },
    "required": ["legible", "tipo", "titulo", "remitente", "importe", "fecha_limite",
                 "accion", "sospechoso", "motivo_sospecha"],
    "additionalProperties": False,
}

INSTRUCCIONES = """Eres el lector de documentos de Willo, una app de dinero para personas con \
discapacidad intelectual. Te llega la foto de un papel: una factura, un recibo, un ticket de \
compra, una nómina, una multa, una carta del banco u otra cosa.

Tu trabajo es SOLO copiar lo que pone. No hagas cuentas. No recomiendes nada. No inventes datos: \
si algo no aparece o no se lee, pon null.

- tipo: "ticket" es el ticket de algo que ya se compró (tienda, bar, supermercado). \
"recibo" es un cobro del banco ya hecho o programado (luz, agua, móvil). "factura" pide un pago.
- accion: "pagar" si hay que pagar; "nada" si ya está pagado (los tickets casi siempre); \
"contestar" si pide una respuesta; "revisar" si no está claro.
- importe: el total final que hay que pagar o que se pagó, en euros.
- sospechoso: true si pide claves, PIN, códigos SMS o datos de la tarjeta; si mete prisa \
con amenazas; si pide pagar por Bizum o transferencia a una persona; o si parece falso.
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
    return {
        "tipo": tipo if tipo in TIPOS else "otro",
        "titulo": str(datos["titulo"]).strip(),
        "remitente": (str(datos.get("remitente") or "").strip() or None),
        "importe": importe,
        "fecha_limite": fecha.isoformat() if fecha else None,
        "accion": accion if accion in ACCIONES else "revisar",
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
    frases.append("¿Es correcto?")
    return " ".join(frases)


def leer(contenido: bytes, media_type: str | None) -> dict[str, Any]:
    """Foto -> datos del documento + texto de Noa. La foto no sale de esta función."""
    imagen, tipo_imagen = preparar_imagen(contenido, media_type)
    datos = limpiar(_llamar_claude(imagen, tipo_imagen))
    pictograma = "aviso" if datos["sospechoso"] else PICTOGRAMAS.get(datos["tipo"], "documento")
    return {**datos, "pictograma": pictograma, "texto_lectura_facil": texto_leido(datos)}

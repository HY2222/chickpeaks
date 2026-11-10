"""Registro de gastos dictados por la persona de apoyo.

El audio lo transcribe ElevenLabs Scribe (en el frontend o en /gastos/audio).
Aquí convertimos la frase en un gasto: importe, hucha y concepto.
Ejemplo: "He pagado 45 euros de luz de Javi" -> 45 €, hucha casa, "Luz".
"""

from __future__ import annotations

import re
import unicodedata

_CATEGORIAS = {
    "casa": ["luz", "agua", "gas", "alquiler", "internet", "telefono", "movil", "comunidad",
             "abono", "transporte", "metro", "autobus"],
    "comida": ["supermercado", "mercadona", "compra", "comida", "fruta", "carniceria", "panaderia"],
    "mis_cosas": ["ropa", "zapatillas", "camiseta", "regalo", "peluqueria", "farmacia", "gafas"],
    "ocio": ["cine", "bar", "cafe", "cena", "concierto", "excursion", "entrada", "futbol"],
}

_IMPORTE = re.compile(r"(\d+(?:[.,]\d{1,2})?)\s*(?:€|euros?|eur)\b", re.IGNORECASE)
_NUM_SUELTO = re.compile(r"\b(\d+(?:[.,]\d{1,2})?)\b")


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def interpretar(texto: str) -> dict:
    m = _IMPORTE.search(texto) or _NUM_SUELTO.search(texto)
    if not m:
        raise ValueError("No encuentro el importe. Di, por ejemplo: «45 euros de luz».")
    importe = float(m.group(1).replace(",", "."))
    t = _norm(texto)
    hucha, concepto = "mis_cosas", None
    for h, palabras in _CATEGORIAS.items():
        for p in palabras:
            if re.search(rf"\b{p}\b", t):
                hucha, concepto = h, p.capitalize()
                break
        if concepto:
            break
    if not concepto:
        # Lo que va después de "de"/"en" tras el importe, como concepto aproximado.
        resto = texto[m.end():]
        cm = re.search(r"\b(?:de|en|para)\s+(.+?)(?:\s+de\s+\w+)?[.]?$", resto, re.IGNORECASE)
        concepto = cm.group(1).strip() if cm else "Gasto"
        concepto = concepto[:1].upper() + concepto[1:]  # no .capitalize(): pasaría "Marta" a "marta"
    return {"importe": importe, "hucha": hucha, "concepto": concepto, "texto_original": texto}

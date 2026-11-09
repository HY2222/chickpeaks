"""Lectura fácil: formato de cifras y comprobador de legibilidad.

Índice Fernández-Huerta (adaptación de Flesch al español):
    L = 206,84 - 0,60 * P - 1,02 * F
P = sílabas por cada 100 palabras, F = frases por cada 100 palabras.
Más alto = más fácil. Por encima de 80 se considera fácil.
"""

from __future__ import annotations

import re

UMBRAL_FACIL = 80.0
MAX_PALABRAS_POR_FRASE = 15

_VOCALES = "aeiouáéíóúü"
_FUERTES = set("aeoáéó") | set("íú")  # í y ú acentuadas rompen el diptongo


def euros(importe: float) -> str:
    """80.0 -> '80 €'; 12.5 -> '12,50 €'; 4800 -> '4.800 €'. Sin decimales cuando no hacen falta."""
    if float(importe).is_integer():
        texto = f"{int(importe):,}"
    else:
        texto = f"{importe:,.2f}"
    # Formato español: punto para los miles y coma para los decimales.
    return texto.replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def silabas(palabra: str) -> int:
    palabra = palabra.lower()
    if palabra.isdigit():
        return max(1, len(palabra))  # aproximación: "120" se lee "ciento veinte"
    # Cada grupo de vocales es una sílaba, salvo dos vocales fuertes seguidas (hiato).
    n = 0
    previa = ""
    for c in palabra:
        if c in _VOCALES and (not previa or (previa in _FUERTES and c in _FUERTES)):
            n += 1
        previa = c if c in _VOCALES else ""
    return max(n, 1)


def _palabras(texto: str) -> list[str]:
    return re.findall(r"[a-záéíóúüñ0-9]+", texto.lower())


def _frases(texto: str) -> list[str]:
    return [f for f in re.split(r"[.!?¿¡]+", texto) if _palabras(f)]


def fernandez_huerta(texto: str) -> float:
    palabras = _palabras(texto)
    if not palabras:
        return 0.0
    n = len(palabras)
    p = sum(silabas(w) for w in palabras) * 100 / n
    f = len(_frases(texto)) * 100 / n
    return round(206.84 - 0.60 * p - 1.02 * f, 1)


def comprobar(texto: str) -> dict:
    frases = _frases(texto)
    largas = [f.strip() for f in frases if len(_palabras(f)) > MAX_PALABRAS_POR_FRASE]
    tiene_porcentaje = "%" in texto or "por ciento" in texto.lower()
    indice = fernandez_huerta(texto)
    problemas = []
    if indice < UMBRAL_FACIL:
        problemas.append(f"Índice {indice} por debajo de {UMBRAL_FACIL}.")
    if largas:
        problemas.append(f"{len(largas)} frase(s) con más de {MAX_PALABRAS_POR_FRASE} palabras.")
    if tiene_porcentaje:
        problemas.append("Usa porcentajes. En lectura fácil, mejor euros.")
    return {
        "indice_fernandez_huerta": indice,
        "es_facil": not problemas,
        "problemas": problemas,
        "frases_largas": largas,
    }

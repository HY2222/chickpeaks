"""Escudo antiestafas con reglas explicables.

Nunca bloquea un pago: devuelve señales, preguntas en lectura fácil y si
conviene avisar al círculo de apoyo (solo a quien tenga consentimiento previo).
No analiza emociones de la voz: solo usa lo que la persona dice y los datos del pago.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from .budget import estado_huchas
from .easyread import euros

# (id, palabras clave, peso, explicación en lectura fácil)
_REGLAS_TEXTO = [
    ("urgencia", ["urgente", "ahora mismo", "rapido", "hoy mismo", "ya mismo", "corre prisa"], 2,
     "Te meten prisa. Quien te quiere no te mete prisa con el dinero."),
    ("secreto", ["no se lo digas", "no digas nada", "es un secreto", "solo entre nosotros"], 3,
     "Te piden que no se lo cuentes a nadie."),
    ("codigos", ["codigo", "clave", "contrasena", "pin", "sms"], 3,
     "Te piden un código. El banco nunca te pide códigos."),
    ("premio", ["premio", "has ganado", "sorteo", "loteria", "herencia"], 2,
     "Te dicen que has ganado algo, pero tienes que pagar."),
    ("relacion_nueva", ["amigo nuevo", "amiga nueva", "novio", "novia", "por internet",
                         "por instagram", "por whatsapp", "por tiktok", "lo conoci", "la conoci"], 2,
     "Es una persona que conoces desde hace poco."),
    ("suplantacion", ["soy del banco", "del banco", "hacienda", "la policia", "tu hijo", "tu hija"], 2,
     "Dicen que son del banco, de Hacienda o de la policía."),
    ("prestamo", ["prestame", "me lo devuelve", "te lo devuelvo", "dejame dinero"], 1,
     "Te piden dinero prestado."),
]


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def evaluar_pago(persona: dict[str, Any], destinatario: str, importe: float,
                 contexto: str = "") -> dict[str, Any]:
    senales: list[dict[str, Any]] = []
    conocidos = {_normalizar(d) for d in persona.get("destinatarios_conocidos", [])}
    if _normalizar(destinatario) not in conocidos:
        senales.append({"id": "destinatario_nuevo", "peso": 2,
                        "explicacion": f"Nunca has enviado dinero a {destinatario}."})

    libre = sum(h["quedan"] for h in estado_huchas(persona) if h["id"] in ("mis_cosas", "ocio"))
    if importe > max(libre, 0):
        senales.append({"id": "importe_alto", "peso": 2,
                        "explicacion": f"Son {euros(importe)}. Es más de lo que te queda este mes para tus cosas."})

    ctx = _normalizar(contexto)
    for rid, claves, peso, explicacion in _REGLAS_TEXTO:
        if any(re.search(rf"\b{re.escape(_normalizar(c))}\b", ctx) for c in claves):
            senales.append({"id": rid, "peso": peso, "explicacion": explicacion})

    puntos = sum(s["peso"] for s in senales)
    nivel = "alto" if puntos >= 5 else "medio" if puntos >= 3 else "bajo"

    preguntas = []
    if nivel != "bajo":
        preguntas = [
            f"¿Conoces a {destinatario} en persona?",
            "¿Te han pedido el dinero por teléfono o por mensaje?",
            "¿Quieres pensarlo un rato antes de enviarlo?",
        ]
    texto = _texto(nivel, senales)
    return {
        "nivel_riesgo": nivel,
        "puntos": puntos,
        "senales": senales,
        "preguntas": preguntas,
        "texto_lectura_facil": texto,
        "bloquea": False,  # La decisión siempre es de la persona.
        "sugerir_aviso_apoyo": nivel == "alto",
    }


def _texto(nivel: str, senales: list[dict[str, Any]]) -> str:
    if nivel == "bajo":
        return "Este pago parece normal. Tú decides."
    partes = ["Espera un momento.", "He visto algo raro."]
    partes += [s["explicacion"] for s in senales[:3]]
    partes.append("Puedes enviarlo o esperar. Tú decides.")
    return " ".join(partes)

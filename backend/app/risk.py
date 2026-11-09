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
    # Meter prisa es una señal de estafa, aunque sea con una palabra corta como "ya" o "ahora".
    ("urgencia", ["urgente", "urgencia", "ya", "ahora", "rapido", "rapidamente", "hoy", "esta noche",
                  "enseguida", "en seguida", "cuanto antes", "lo antes posible", "inmediatamente",
                  "corre prisa", "corre", "date prisa", "deprisa", "no hay tiempo", "no tengo tiempo",
                  "en cinco minutos", "en 5 minutos", "antes de que", "se acaba", "ultimo dia"], 2,
     "Te meten prisa. Quien te quiere no te mete prisa con el dinero."),
    ("secreto", ["no se lo digas", "no digas nada", "es un secreto", "solo entre nosotros"], 3,
     "Te piden que no se lo cuentes a nadie."),
    ("codigos", ["codigo", "clave", "contrasena", "pin", "sms"], 3,
     "Te piden un código. El banco nunca te pide códigos."),
    ("premio", ["premio", "has ganado", "sorteo", "loteria", "herencia"], 2,
     "Te dicen que has ganado algo, pero tienes que pagar."),
    ("relacion_nueva", ["amigo nuevo", "amiga nueva", "novio", "novia", "por internet",
                         "por instagram", "por whatsapp", "por tiktok", "lo conoci", "la conoci",
                         "de instagram", "de internet", "de whatsapp", "de tiktok", "de tinder",
                         "de facebook", "por facebook", "por tinder", "no lo conozco", "no la conozco"], 2,
     "Es una persona que conoces desde hace poco."),
    ("suplantacion", ["soy del banco", "del banco", "hacienda", "la policia", "tu hijo", "tu hija",
                      "soy yo", "nuevo numero", "numero nuevo", "cambiado de numero", "cambie de numero",
                      "se me ha roto el movil", "perdi el movil"], 2,
     "Dicen que son del banco, de Hacienda o de la policía."),
    ("pide_dinero", ["dame", "mandame", "enviame", "pasame", "ingresame", "hazme un bizum",
                     "mandame un bizum", "necesito dinero", "necesito que me", "transfiereme"], 1,
     "Te pide dinero."),
    ("prestamo", ["prestame", "prestar", "dejame dinero", "me lo devuelve", "me los devuelve",
                  "me la devuelve", "me las devuelve", "te lo devuelvo", "te los devuelvo",
                  "te lo devolvere", "te los devolvere", "me lo devolvera", "me los devolvera"], 1,
     "Te piden dinero prestado."),
]


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _numero(telefono: str | None) -> str:
    """'+34 600 000 101' -> '600000101'. Compara los 9 últimos dígitos (números de España)."""
    return re.sub(r"\D", "", telefono or "")[-9:]


numero = _numero  # para usarlo desde fuera


def evaluar_pago(persona: dict[str, Any], destinatario: str | None, importe: float,
                 contexto: str = "", telefono: str | None = None) -> dict[str, Any]:
    """`telefono`: el número de quien pide el dinero, si se sabe (por ejemplo, de un pantallazo).

    `destinatario` puede ser None: en un pantallazo a veces no se ve quién escribe.
    Entonces no decimos "nunca le has enviado dinero", porque no lo sabemos.
    """
    senales: list[dict[str, Any]] = []
    contactos = persona.get("contactos", [])
    conocidos = {_normalizar(d) for d in persona.get("destinatarios_conocidos", [])}
    conocidos |= {_normalizar(c["nombre"]) for c in contactos}
    nombre_conocido = bool(destinatario) and _normalizar(destinatario) in conocidos

    numero = _numero(telefono)
    contacto = next((c for c in contactos if numero and _numero(c["telefono"]) == numero), None)
    if numero and contacto is None:
        if nombre_conocido:
            # "Hola, soy Ana, este es mi número nuevo": la estafa más típica por WhatsApp.
            senales.append({"id": "numero_desconocido", "peso": 3,
                            "explicacion": f"Dice que es {destinatario}, pero no tienes guardado este número."})
        else:
            senales.append({"id": "numero_desconocido", "peso": 2,
                            "explicacion": "No tienes guardado este número."})
    if not destinatario and not numero:
        senales.append({"id": "remitente_desconocido", "peso": 2,
                        "explicacion": "No se ve quién te lo pide. Antes de enviar nada, comprueba quién es."})
    elif not nombre_conocido and contacto is None and destinatario:
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
            f"¿Conoces a {destinatario} en persona?" if destinatario else "¿Sabes seguro quién te lo pide?",
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

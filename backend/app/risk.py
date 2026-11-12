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
    ("suplantacion", ["soy del banco", "del banco", "hacienda", "la policia"], 2,
     "Dicen que son del banco, de Hacienda o de la policía."),
    # "Hola mamá, me he cambiado de número": la estafa más típica por WhatsApp.
    ("numero_cambiado", ["nuevo numero", "numero nuevo", "cambiado de numero", "cambie de numero",
                         "cambiado el numero", "se me ha roto el movil", "perdi el movil",
                         "he perdido el movil", "tu hijo", "tu hija", "soy yo"], 3,
     "Dice que ha cambiado de número. Es un engaño muy común. Llama a su número de siempre."),
    # Cartas falsas de "la Seguridad Social" o "Hacienda": piden fotos del DNI y del banco por correo.
    ("datos_personales", ["dni", "nie", "foto del dni", "fotos del dni", "ambas caras", "extracto bancario",
                          "extracto del banco", "datos bancarios", "numero de cuenta", "iban",
                          "datos personales", "cambio de datos"], 3,
     "Te piden tu DNI o datos del banco. Nunca los mandes por correo ni por mensaje."),
    ("ayuda_falsa", ["incremento de las prestaciones", "incremento de la prestacion", "subida de la pension",
                     "ayuda de", "devolucion de", "ataque informatico", "se han perdido"], 2,
     "Te prometen dinero o dicen que se han perdido tus datos. Es un truco muy usado."),
    ("pide_dinero", ["dame", "mandame", "enviame", "pasame", "ingresame", "hazme un bizum",
                     "mandame un bizum", "necesito dinero", "necesito que me", "transfiereme",
                     "hacer un bizum", "hacerme un bizum", "hacer una transferencia",
                     "hacerme una transferencia", "hazme una transferencia"], 1,
     "Te pide dinero."),
    ("prestamo", ["prestame", "prestar", "dejame dinero", "me lo devuelve", "me los devuelve",
                  "me la devuelve", "me las devuelve", "te lo devuelvo", "te los devuelvo",
                  "te lo devolvere", "te los devolvere", "me lo devolvera", "me los devolvera"], 1,
     "Te piden dinero prestado."),
]


# Señales que hacen sospechoso un pago aunque se diga que es de la familia.
_SENALES_DE_ENGANO = {"numero_desconocido", "numero_cambiado", "suplantacion", "secreto",
                      "codigos", "premio", "relacion_nueva", "remitente_desconocido"}
_FAMILIA = re.compile(r"\b(hermano|hermana|hermanos|hermanas|madre|padre|mama|papa|padres|abuelo|"
                      r"abuela|abuelos|tio|tia|tios|primo|prima|primos|hijo|hija|hijos|familia|"
                      r"familiar|familiares|cunado|cunada|sobrino|sobrina)\b")


def _es_familia(destinatario: str | None, contexto_normalizado: str) -> bool:
    """¿Se envía a la familia? Mira a quién va (p. ej. "mis hermanos") y lo que ha contado Javi."""
    return bool(_FAMILIA.search(_normalizar(destinatario or "") + " " + contexto_normalizado))


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

    # Dinero a la familia (un hermano, su madre…): no es "alguien nuevo". Solo si no hay otras
    # señales de engaño: "mi hijo me escribe desde un número nuevo" sigue siendo sospechoso.
    ids = {s["id"] for s in senales}
    if (_es_familia(destinatario, ctx) and not ids & _SENALES_DE_ENGANO):
        senales = [s for s in senales if s["id"] != "destinatario_nuevo"]

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


_CORREO_GRATIS = re.compile(r"[\w.+-]+@(?:gmail|hotmail|outlook|yahoo|live|icloud|protonmail)\.[a-z]{2,}")
_ESTA_ES_OFICIAL = re.compile(r"\b(seguridad social|inss|hacienda|agencia tributaria|banco|policia|correos|dgt)\b")


def evaluar_texto(texto: str) -> dict[str, Any]:
    """Solo las reglas del texto (sin pagos ni números). Para cartas que piden algo."""
    ctx = _normalizar(texto)
    senales: list[dict[str, Any]] = []
    for rid, claves, peso, explicacion in _REGLAS_TEXTO:
        if any(re.search(rf"\b{re.escape(_normalizar(c))}\b", ctx) for c in claves):
            senales.append({"id": rid, "peso": peso, "explicacion": explicacion})
    if _CORREO_GRATIS.search(ctx) and _ESTA_ES_OFICIAL.search(ctx):
        senales.append({"id": "correo_no_oficial", "peso": 3,
                        "explicacion": "Dicen que son un organismo oficial, pero piden escribir a un correo normal."})
    puntos = sum(s["peso"] for s in senales)
    nivel = "alto" if puntos >= 5 else "medio" if puntos >= 3 else "bajo"
    return {"nivel_riesgo": nivel, "puntos": puntos, "senales": senales, "texto_lectura_facil": _texto(nivel, senales),
            "bloquea": False}


def _texto(nivel: str, senales: list[dict[str, Any]]) -> str:
    if nivel == "bajo":
        return "No he visto nada raro. Tú decides."
    partes = ["Espera un momento.", "He visto algo raro."]
    partes += [s["explicacion"] for s in senales[:3]]
    partes.append("Puedes enviarlo o esperar. Tú decides.")
    return " ".join(partes)

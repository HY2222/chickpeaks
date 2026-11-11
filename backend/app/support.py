"""Círculo de apoyo (sustituye al "control parental").

Niveles, de menos a más. Cada nivel incluye lo de los anteriores:
  N0  Por defecto: solo la persona usa la app y decide.
  N1  Compartir: la persona de apoyo ve lo que ella elige. Se puede retirar.
  N2  Apoyo: avisos de posible estafa (con consentimiento previo) y
      "pausa para pensar" que activa la propia persona. Nunca bloqueo.
  N3  Guardador de hecho: registra gastos y prepara la rendición de cuentas.
  N4  Poder preventivo o curatela: solo lo que diga el documento, nada más.

Los niveles N0 a N2 los da la persona (otorgado_por = "persona") y los puede
quitar. N3 y N4 vienen de la ley o de un documento.
"""

from __future__ import annotations

from typing import Any

NIVELES = {
    0: "Por defecto",
    1: "Compartir",
    2: "Apoyo",
    3: "Guardador de hecho",
    4: "Poder preventivo o curatela",
}

# Permiso -> nivel mínimo
_PERMISOS = {
    "ver_decisiones": 1,
    "recibir_avisos_estafa": 2,
    "registrar_gastos": 3,
    "preparar_rendicion_cuentas": 3,
}


def puede(miembro: dict[str, Any], permiso: str) -> bool:
    nivel = miembro["nivel"]
    if nivel == 4:
        # N4: lo que diga el documento, nada más. Ver decisiones va incluido en ver movimientos.
        alcance = set(miembro.get("alcance_documento", []))
        if permiso == "ver_decisiones":
            return "ver_movimientos" in alcance
        if permiso == "recibir_avisos_estafa":
            return miembro.get("consiente_avisos_estafa", False)
        return permiso in alcance
    if permiso == "recibir_avisos_estafa":
        return nivel >= 2 and miembro.get("consiente_avisos_estafa", False)
    return nivel >= _PERMISOS.get(permiso, 99)


def miembro(persona: dict[str, Any], miembro_id: str) -> dict[str, Any] | None:
    return next((m for m in persona["circulo_apoyo"] if m["id"] == miembro_id), None)


def con_permiso(persona: dict[str, Any], permiso: str) -> list[dict[str, Any]]:
    return [m for m in persona["circulo_apoyo"] if puede(m, permiso)]


def describir(persona: dict[str, Any]) -> list[dict[str, Any]]:
    salida = []
    for m in persona["circulo_apoyo"]:
        salida.append({
            **m,
            "nivel_nombre": NIVELES[m["nivel"]],
            "puede_retirarlo_la_persona": m["otorgado_por"] == "persona",
            "permisos": [p for p in _PERMISOS if puede(m, p)],
        })
    return salida


def cambiar_nivel(persona: dict[str, Any], miembro_id: str, nivel: int) -> dict[str, Any]:
    """La persona cambia (o retira, nivel 0) el apoyo que ella dio. Solo N0 a N2."""
    m = miembro(persona, miembro_id)
    if m is None:
        raise KeyError(miembro_id)
    if m["otorgado_por"] != "persona":
        raise PermissionError("Este apoyo viene de un documento legal. No se cambia desde la app.")
    if not 0 <= nivel <= 2:
        raise ValueError("La persona puede dar los niveles 0, 1 o 2.")
    m["nivel"] = nivel
    return m


# Personas de confianza: las que reciben los avisos (posibles estafas, pagos que no se pueden,
# más de 1.000 € en un día). Son las que tienen el permiso "recibir_avisos_estafa". Puede haber varias.

def _marcar(m: dict[str, Any], elegida: bool) -> None:
    if elegida:
        m["nivel"] = max(m["nivel"], 2)            # Apoyo como mínimo
        m["consiente_avisos_estafa"] = True
    else:
        m["consiente_avisos_estafa"] = False
        if m["otorgado_por"] == "persona" and m["nivel"] <= 2:
            m["nivel"] = 0                         # la dio la persona: la quita. N3-N4 no se tocan


def anadir_confianza(persona: dict[str, Any], nombre: str, telefono: str | None = None,
                     relacion: str | None = None) -> dict[str, Any]:
    """Añade a alguien (nuevo o de su círculo) a sus personas de confianza. Las demás siguen igual."""
    circulo = persona["circulo_apoyo"]
    nombre = " ".join(nombre.split())
    m = next((x for x in circulo if x["nombre"].lower() == nombre.lower()), None)
    if m is None:
        base = "".join(c if c.isalnum() else "_" for c in nombre.lower()).strip("_") or "confianza"
        ids, id_, n = {x["id"] for x in circulo}, base, 2
        while id_ in ids:
            id_, n = f"{base}_{n}", n + 1
        m = {"id": id_, "nombre": nombre[:1].upper() + nombre[1:],   # "marta" → "Marta"
             "relacion": (relacion or "persona de confianza").strip(), "nivel": 2,
             "otorgado_por": "persona", "consiente_avisos_estafa": True}
        circulo.append(m)
    if telefono:
        m["telefono"] = telefono.strip()
    _marcar(m, True)
    return m


def fijar_confianza(persona: dict[str, Any], ids: list[str]) -> list[dict[str, Any]]:
    """Las personas de confianza son exactamente estas (ids de su círculo). Al menos una."""
    circulo = persona["circulo_apoyo"]
    elegidas = set(ids)
    if not elegidas:
        raise ValueError("Elige al menos a una persona.")
    desconocidas = elegidas - {m["id"] for m in circulo}
    if desconocidas:
        raise KeyError(", ".join(sorted(desconocidas)))
    for m in circulo:
        _marcar(m, m["id"] in elegidas)
    return [m for m in circulo if m["id"] in elegidas]

"""Límites del dinero. Los comprueba el código antes de apuntar cualquier movimiento.

1. Nada deja una hucha en negativo: si no llega, no se apunta.
2. Más de 1.000 € en un día (gastado o recibido): se puede, pero se avisa siempre al círculo de apoyo.
   Si no hay nadie a quien avisar, no se apunta.
3. Nada pasa de 1.000.000 € en Willo: es un error, no un movimiento de verdad.
"""

from __future__ import annotations

from typing import Any

from .budget import estado_huchas
from .easyread import euros
from .notify import avisar
from .store import hoy
from .support import con_permiso

LIMITE_DIARIO = 1000.0
LIMITE_APP = 1_000_000.0
TEXTO_LIMITE_APP = "Error: esa cantidad no es posible. En Willo el máximo es 1.000.000 €."


class FueraDeLimite(Exception):
    """El movimiento no se apunta. `texto` es la frase en lectura fácil para la persona."""

    def __init__(self, texto: str, codigo: str):
        super().__init__(texto)
        self.texto, self.codigo = texto, codigo


def movido_hoy(persona: dict[str, Any], tipo: str = "gasto") -> float:
    """Lo que ha salido (gasto) o entrado (ingreso) hoy."""
    h = hoy().isoformat()
    return round(sum(m["importe"] for m in persona["movimientos"]
                     if m["fecha"] == h and (m["tipo"] == "ingreso") == (tipo == "ingreso")), 2)


def revisar(persona: dict[str, Any], importe: float, hucha: str | None = None,
            tipo: str = "gasto") -> dict[str, Any]:
    """Cifras para avisar antes (no apunta ni avisa a nadie). Lo usan Noa y la pantalla."""
    quedan = None
    if tipo == "gasto" and hucha:
        quedan = next((h["quedan"] for h in estado_huchas(persona) if h["id"] == hucha), None)
    hoy_ = movido_hoy(persona, tipo)
    return {"fuera_de_app": importe > LIMITE_APP,
            "negativo": quedan is not None and round(quedan - importe, 2) < 0,
            "quedan": quedan,
            "pasa_limite_diario": hoy_ + importe > LIMITE_DIARIO,
            "movido_hoy": hoy_}


def comprobar(persona: dict[str, Any], importe: float, concepto: str, hucha: str | None = None,
              tipo: str = "gasto", ya_pagado: bool = False) -> list[str]:
    """Llamar justo antes de apuntar un movimiento. Si no se puede, lanza FueraDeLimite.

    ya_pagado: un gasto que ya ha ocurrido y la persona de apoyo apunta para las cuentas del juzgado.
    No se bloquea por saldo (si no se apuntara, el informe estaría mal), pero sí los otros límites.

    Si pasa de 1.000 € hoy, avisa al círculo y devuelve a quién (para decírselo a la persona).
    """
    r = revisar(persona, importe, hucha, tipo)
    if r["fuera_de_app"]:
        raise FueraDeLimite(TEXTO_LIMITE_APP, "limite_app")
    if r["negativo"] and not ya_pagado:
        falta = round(importe - r["quedan"], 2)
        raise FueraDeLimite(f"No te llega. Te faltan {euros(falta)}. "
                            "No lo apunto: tu hucha se quedaría en negativo.", "saldo_negativo")
    if not r["pasa_limite_diario"]:
        return []
    miembros = con_permiso(persona, "ver_decisiones")
    if not miembros:
        raise FueraDeLimite(f"Hoy pasarías de {euros(LIMITE_DIARIO)}. Para eso tiene que saberlo "
                            "una persona de tu círculo de apoyo, y no tienes a nadie.", "limite_diario")
    verbo = "recibir" if tipo == "ingreso" else "gastar"
    total = euros(round(r["movido_hoy"] + importe, 2))
    aviso = avisar(persona, miembros, "limite_diario",
                   f"Aviso de Willo: {persona['nombre']} va a {verbo} {euros(importe)} ({concepto}). "
                   f"Hoy suma {total}: pasa del límite de {euros(LIMITE_DIARIO)} al día. "
                   "La decisión es suya.")
    return aviso["para_nombres"]

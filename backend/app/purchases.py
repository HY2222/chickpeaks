"""Compras de Javi: "Quiero comprar" (decidido, sin pagar) y "Ya pagado".

Decidir comprar algo NO baja el dinero. El dinero baja cuando Javi lo paga de verdad
(en la demo lo simula un botón; en la app real lo diría el banco).
Si pasan 7 días y no lo ha pagado, la compra sale sola de "Quiero comprar".
Willo no paga nada y no bloquea nada: solo apunta.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta
from typing import Any

from . import limites
from .store import hoy

DIAS_CADUCIDAD = 7


def _clave(concepto: str) -> str:
    """"La entrada del concierto" y "entrada del concierto" son la misma compra."""
    t = unicodedata.normalize("NFD", concepto.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"^(la|el|los|las|un|una|unos|unas)\s+", "", t.strip())
    return re.sub(r"\s+", " ", t)


def _lista(persona: dict[str, Any]) -> list[dict[str, Any]]:
    """Las compras decididas que siguen vivas. Las caducadas se quitan aquí."""
    h = hoy().isoformat()
    vivas = [c for c in persona.setdefault("compras_pendientes", []) if c["caduca"] >= h]
    persona["compras_pendientes"] = vivas
    return vivas


def pendientes(persona: dict[str, Any]) -> list[dict[str, Any]]:
    h = hoy()
    return [{**c, "dias_restantes": (date.fromisoformat(c["caduca"]) - h).days} for c in _lista(persona)]


def buscar(persona: dict[str, Any], compra_id: str) -> dict[str, Any] | None:
    return next((c for c in _lista(persona) if c["id"] == compra_id), None)


def apuntar(persona: dict[str, Any], concepto: str, importe: float, hucha: str) -> dict[str, Any]:
    """Javi ha decidido comprar algo. Si ya estaba apuntado, no se apunta dos veces."""
    lista = _lista(persona)
    for c in lista:
        if _clave(c["concepto"]) == _clave(concepto) and c["importe"] == importe:
            return c
    persona["compras_seq"] = persona.get("compras_seq", 0) + 1
    h = hoy()
    c = {"id": f"co_{persona['compras_seq']}", "concepto": concepto, "importe": importe, "hucha": hucha,
         "fecha": h.isoformat(), "caduca": (h + timedelta(days=DIAS_CADUCIDAD)).isoformat()}
    lista.append(c)
    return c


def quitar(persona: dict[str, Any], compra_id: str) -> bool:
    lista = _lista(persona)
    quedan = [c for c in lista if c["id"] != compra_id]
    persona["compras_pendientes"] = quedan
    return len(quedan) < len(lista)


def pagar(persona: dict[str, Any], concepto: str, importe: float, hucha: str,
          compra_id: str | None = None) -> dict[str, Any]:
    """Javi ya lo ha pagado: se apunta el gasto (el dinero baja) y sale de "Quiero comprar".

    Antes, los límites (limites.py): si deja la hucha en negativo o pasa de 1.000.000 €, no se apunta
    (FueraDeLimite). Si pasa de 1.000 € hoy, se avisa al círculo: van en mov["avisados_limite"].
    """
    avisados = limites.comprobar(persona, importe, concepto, hucha)
    lista = _lista(persona)
    pendiente = next((c for c in lista if c["id"] == compra_id), None) if compra_id else None
    if not pendiente:
        pendiente = (next((c for c in lista if _clave(c["concepto"]) == _clave(concepto)
                           and c["importe"] == importe), None)
                     or next((c for c in lista if c["importe"] == importe and c["hucha"] == hucha), None))
    if pendiente:
        persona["compras_pendientes"] = [c for c in lista if c is not pendiente]
    mov = {"fecha": hoy().isoformat(), "concepto": concepto[:1].upper() + concepto[1:], "importe": importe,
           "tipo": "gasto", "hucha": hucha, "destinatario": None, "registrado_por": "persona"}
    persona["movimientos"].append(mov)
    return {**mov, "avisados_limite": avisados}


def pagadas_este_mes(persona: dict[str, Any], hucha: str = "mis_cosas") -> list[dict[str, Any]]:
    """Lo que Javi ya ha pagado este mes con el dinero de sus cosas. Lo más nuevo, primero."""
    mes = hoy().isoformat()[:7]
    movs = [m for m in persona["movimientos"]
            if m["tipo"] == "gasto" and m["hucha"] == hucha and m["fecha"][:7] == mes]
    return [{"concepto": m["concepto"], "importe": m["importe"], "fecha": m["fecha"]} for m in reversed(movs)]

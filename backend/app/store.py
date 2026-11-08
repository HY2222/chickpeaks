"""Estado de la demo en memoria, construido a partir de data/seed.json.

Genera el historial del año (enero hasta el mes actual) a partir de los
ingresos y gastos recurrentes, para que el informe anual tenga datos.
Todo es inventado: no hay conexión con ningún banco.
"""

from __future__ import annotations

import copy
import json
import os
from datetime import date
from pathlib import Path
from typing import Any

SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "seed.json"


def hoy() -> date:
    """Fecha de "hoy". Se puede fijar con WILLO_HOY=AAAA-MM-DD para demos y tests."""
    fijada = os.getenv("WILLO_HOY")
    return date.fromisoformat(fijada) if fijada else date.today()


class Store:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        self.personas: dict[str, dict[str, Any]] = {}
        for p in seed["personas"]:
            p = copy.deepcopy(p)
            p["movimientos"] = self._historial(p)
            p["decisiones"] = []
            p["avisos"] = []
            self.personas[p["id"]] = p

    def _historial(self, p: dict[str, Any]) -> list[dict[str, Any]]:
        h = hoy()
        movs: list[dict[str, Any]] = []
        for mes in range(1, h.month + 1):
            ultimo_dia = h.day if mes == h.month else 28
            for ing in p.get("ingresos_mensuales", []):
                if ing["dia"] <= ultimo_dia:
                    movs.append({
                        "fecha": date(h.year, mes, ing["dia"]).isoformat(),
                        "concepto": ing["concepto"], "importe": ing["importe"],
                        "tipo": "ingreso", "hucha": None, "destinatario": None,
                        "registrado_por": "banco",
                    })
            for g in p.get("gastos_recurrentes", []):
                if g["dia"] <= ultimo_dia:
                    movs.append({
                        "fecha": date(h.year, mes, g["dia"]).isoformat(),
                        "concepto": g["concepto"], "importe": g["importe"],
                        "tipo": "gasto", "hucha": g["hucha"],
                        "destinatario": g.get("destinatario"), "registrado_por": "banco",
                    })
        for m in p.get("movimientos_mes_actual", []):
            if m["fecha_dia"] <= h.day:
                movs.append({
                    "fecha": date(h.year, h.month, m["fecha_dia"]).isoformat(),
                    "concepto": m["concepto"], "importe": m["importe"], "tipo": "gasto",
                    "hucha": m["hucha"], "destinatario": m.get("destinatario"),
                    "registrado_por": "banco",
                })
        movs.sort(key=lambda m: m["fecha"])
        return movs

    def persona(self, persona_id: str) -> dict[str, Any] | None:
        return self.personas.get(persona_id)


store = Store()

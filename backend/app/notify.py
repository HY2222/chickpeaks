"""Avisos al círculo de apoyo.

Se guardan en memoria (los lee la pantalla "móvil de Ana" en /demo/apoyo).
Si hay TELEGRAM_BOT_TOKEN y el miembro tiene telegram_chat_id, también se envían por Telegram.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any

import httpx

log = logging.getLogger("willo.notify")


def ahora() -> str:
    """Fecha y hora del aviso. El día sale de WILLO_HOY, para que la demo sea siempre igual."""
    from .store import hoy
    return datetime.combine(hoy(), datetime.now().time()).isoformat(timespec="seconds")


def avisar(persona: dict[str, Any], miembros: dict[str, Any] | list[dict[str, Any]], tipo: str,
           texto: str, **datos: Any) -> dict[str, Any]:
    """Crea UN aviso, aunque vaya a varias personas del círculo, y lo manda por Telegram a cada una.

    Cada aviso tiene id ("av_1", "av_2"...), estado ("nuevo") y resultado (None hasta que se sepa).
    `datos` son campos extra, por ejemplo destinatario, importe y señales de una posible estafa.
    """
    if isinstance(miembros, dict):
        miembros = [miembros]
    aviso = {
        "id": f"av_{len(persona['avisos']) + 1}",
        "fecha": ahora(),
        "para": miembros[0]["id"],
        "para_nombre": miembros[0]["nombre"],
        "para_ids": [m["id"] for m in miembros],
        "para_nombres": [m["nombre"] for m in miembros],
        "tipo": tipo,
        "estado": "nuevo",
        "resultado": None,
        "texto": texto,
        **datos,
    }
    persona["avisos"].append(aviso)
    for m in miembros:
        _telegram(m, texto)
    return aviso


def buscar(persona: dict[str, Any], aviso_id: str) -> dict[str, Any] | None:
    return next((a for a in persona["avisos"] if a["id"] == aviso_id), None)


def es_para(aviso: dict[str, Any], miembro_id: str) -> bool:
    return miembro_id in aviso.get("para_ids", [aviso["para"]])


def mandar_otra_vez(persona: dict[str, Any], aviso: dict[str, Any], texto: str) -> None:
    """Manda un mensaje nuevo por Telegram sobre un aviso que ya existe. No crea otro aviso."""
    for m in persona["circulo_apoyo"]:
        if es_para(aviso, m["id"]):
            _telegram(m, texto)


def _telegram(miembro: dict[str, Any], texto: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat = miembro.get("telegram_chat_id") or os.getenv("TELEGRAM_CHAT_ID_DEMO")
    if not token or not chat:
        return
    try:
        httpx.post(f"https://api.telegram.org/bot{token}/sendMessage",
                   json={"chat_id": chat, "text": texto}, timeout=5)
    except httpx.HTTPError as e:  # Un fallo de Telegram no debe romper la demo.
        log.warning("Telegram falló: %s", e)

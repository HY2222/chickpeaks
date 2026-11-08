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


def avisar(persona: dict[str, Any], miembro: dict[str, Any], tipo: str, texto: str) -> dict[str, Any]:
    aviso = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "para": miembro["id"],
        "para_nombre": miembro["nombre"],
        "tipo": tipo,
        "texto": texto,
    }
    persona["avisos"].append(aviso)
    _telegram(miembro, texto)
    return aviso


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

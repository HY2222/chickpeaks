"""Cuentas de las huchas. Las cuentas las hace este código, nunca el modelo de lenguaje."""

from __future__ import annotations

from typing import Any

from .easyread import euros
from .store import hoy


def _mes_actual(fecha_iso: str) -> bool:
    h = hoy()
    return fecha_iso[:7] == f"{h.year:04d}-{h.month:02d}"


def estado_huchas(persona: dict[str, Any]) -> list[dict[str, Any]]:
    gastado: dict[str, float] = {}
    for m in persona["movimientos"]:
        if m["tipo"] == "gasto" and m["hucha"] and _mes_actual(m["fecha"]):
            gastado[m["hucha"]] = gastado.get(m["hucha"], 0.0) + m["importe"]
    salida = []
    for h in persona["huchas"]:
        g = round(gastado.get(h["id"], 0.0), 2)
        quedan = round(h["limite_mensual"] - g, 2)
        salida.append({**h, "gastado": g, "quedan": quedan})
    return salida


def nombre_en_frase(h: dict[str, Any]) -> str:
    """"Para tus cosas" -> "tus cosas"; "Mis cosas" -> "mis cosas"."""
    nombre = h["nombre"].lower()
    return nombre[5:] if nombre.startswith("para ") else nombre


def pagos_del_mes(persona: dict[str, Any]) -> dict[str, Any]:
    """Pagos fijos del mes (alquiler, luz...). Los hace el banco solo; Willo nunca paga.
    Sirve para que Javi sepa qué está pagado y qué falta, y que el dinero ya está guardado."""
    h = hoy()
    pagos = []
    for g in sorted(persona.get("gastos_recurrentes", []), key=lambda g: g["dia"]):
        if g["hucha"] == "ahorro":
            continue  # las huchas de ahorro salen en "Tus huchas", no aquí
        pagos.append({"concepto": g["concepto"], "importe": g["importe"], "dia": g["dia"],
                      "corto": g.get("corto", g["concepto"].lower()),
                      "pictograma": g.get("pictograma", g["hucha"]),
                      "pagado": g["dia"] <= h.day})
    pagados = [p for p in pagos if p["pagado"]]
    faltan = [p for p in pagos if not p["pagado"]]
    # Una idea por frase (lectura fácil).
    frases = [f"Ya has pagado {p['corto']}: {euros(p['importe'])}." for p in pagados]
    frases += [f"{p['corto'].capitalize()} se paga el día {p['dia']}: {euros(p['importe'])}." for p in faltan]
    if faltan:
        frases.append("Ese dinero ya está guardado. Se paga solo.")
    if not pagos:
        frases.append("Este mes no tienes pagos fijos.")
    return {"pagos": pagos, "texto_lectura_facil": " ".join(frases)}


def buscar_hucha(persona: dict[str, Any], hucha_id: str | None) -> dict[str, Any]:
    huchas = estado_huchas(persona)
    if hucha_id:
        for h in huchas:
            if h["id"] == hucha_id:
                return h
        raise KeyError(hucha_id)
    # Por defecto, las compras personales salen de "Mis cosas".
    for h in huchas:
        if h["id"] == "mis_cosas":
            return h
    return huchas[0]


def evaluar_compra(persona: dict[str, Any], importe: float, concepto: str,
                   hucha_id: str | None = None) -> dict[str, Any]:
    """Devuelve las cifras y un texto en lectura fácil. No recomienda nada."""
    h = buscar_hucha(persona, hucha_id)
    quedan_despues = round(h["quedan"] - importe, 2)
    alcanza = quedan_despues >= 0
    frases = [f"En la hucha de {nombre_en_frase(h)} te quedan {euros(h['quedan'])}."]
    if alcanza:
        frases.append(f"Si compras {concepto}, te quedan {euros(quedan_despues)}.")
    else:
        falta = round(-quedan_despues, 2)
        frases.append(f"{concepto.capitalize()} cuesta {euros(importe)}.")
        frases.append(f"Te faltan {euros(falta)}.")
        dias = _dias_hasta_fin_de_mes()
        frases.append(f"El mes que viene la hucha se llena otra vez. Faltan {dias} días.")
    frases.append("Tú decides.")
    return {
        "hucha": h["id"],
        "hucha_nombre": h["nombre"],
        "quedan_antes": h["quedan"],
        "importe": importe,
        "quedan_despues": quedan_despues,
        "alcanza": alcanza,
        "texto_lectura_facil": " ".join(frases),
        "pictograma": h["pictograma"],
    }


def _dias_hasta_fin_de_mes() -> int:
    from calendar import monthrange
    h = hoy()
    return monthrange(h.year, h.month)[1] - h.day + 1


def progreso_meta(meta: dict[str, Any]) -> dict[str, Any]:
    falta = round(max(meta["importe"] - meta["ahorrado"], 0.0), 2)
    meses = 0 if falta == 0 else -(-falta // meta["aporte_mensual"])
    texto = (f"Para la {meta['nombre'].lower()} tienes {euros(meta['ahorrado'])}. "
             f"Te faltan {euros(falta)}. "
             f"Si guardas {euros(meta['aporte_mensual'])} cada mes, la tienes en {int(meses)} meses.")
    return {**meta, "falta": falta, "meses_restantes": int(meses), "texto_lectura_facil": texto}

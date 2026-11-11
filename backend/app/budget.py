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
                   hucha_id: str | None = None, antes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Devuelve las cifras y un texto en lectura fácil. No recomienda nada.

    `antes`: lo que ya ha pensado comprar en esta conversación ({concepto, importe}). Se resta
    primero, así "y otros zapatos de 45 €" no vuelve a contar desde el dinero de la hucha.
    """
    h = buscar_hucha(persona, hucha_id)
    antes = antes or []
    pensado = round(sum(a["importe"] for a in antes), 2)
    quedan_antes = round(h["quedan"] - pensado, 2)
    quedan_despues = round(quedan_antes - importe, 2)
    alcanza = quedan_despues >= 0
    frases = [f"En la hucha de {nombre_en_frase(h)} te quedan {euros(h['quedan'])}."]
    if antes:
        cosas = " y ".join(f"{a['concepto']} ({euros(a['importe'])})" for a in antes)
        frases.append(f"Antes has pensado en {cosas}.")
        frases.append(f"Con eso, te quedarían {euros(quedan_antes)}.")
    if alcanza:
        tambien = " también" if antes else ""
        frases.append(f"Si compras{tambien} {concepto}, te quedan {euros(quedan_despues)}.")
    else:
        falta = round(-quedan_despues, 2)
        frases.append(f"{concepto[:1].upper() + concepto[1:]} cuesta {euros(importe)}.")
        frases.append(f"Te faltan {euros(falta)}.")
        dias = _dias_hasta_fin_de_mes()
        frases.append(f"El mes que viene la hucha se llena otra vez. Faltan {dias} días.")
    # La comida tiene su propia hucha: comprar algo de "tus cosas" no la toca. Se dice para que
    # no piense que se queda sin comer (y para no decir lo contrario, que sería falso).
    frase_comida = None
    if h["id"] != "comida" and any(x["id"] == "comida" for x in persona["huchas"]):
        frase_comida = "El dinero de la comida está aparte."
        frases.append(frase_comida)
    # Si no llega, no se puede (limites.py no lo dejará apuntar): no se dice "Tú decides".
    frases.append("Tú decides." if alcanza else "Con este dinero no se puede: tu hucha se quedaría en negativo.")
    return {
        "hucha": h["id"],
        "hucha_nombre": h["nombre"],
        "quedan_antes": quedan_antes,
        "pensado_antes": pensado,
        "importe": importe,
        "quedan_despues": quedan_despues,
        "alcanza": alcanza,
        "frase_comida": frase_comida,
        "texto_lectura_facil": " ".join(frases),
        "pictograma": h["pictograma"],
    }


def _dias_hasta_fin_de_mes() -> int:
    from calendar import monthrange
    h = hoy()
    return monthrange(h.year, h.month)[1] - h.day + 1


class NoSePuedeGuardar(ValueError):
    """No se puede meter ese dinero en la hucha. El mensaje va en lectura fácil."""


def meter_en_meta(persona: dict[str, Any], meta_id: str, importe: float) -> dict[str, Any]:
    """Pasa dinero de "Para tus cosas" a una hucha de ahorro (viaje, móvil...).

    - No se puede meter más de lo que te queda este mes para tus cosas.
    - No se puede meter más de lo que le falta a la hucha.
    El dinero baja de "Para tus cosas" y sube en la hucha. No es un gasto: sigue siendo tuyo."""
    meta = next((m for m in persona.get("metas", []) if m["id"] == meta_id), None)
    if meta is None:
        raise KeyError(meta_id)
    importe = round(importe, 2)
    if importe <= 0:
        raise NoSePuedeGuardar("Escribe cuánto dinero quieres meter.")
    tus_cosas = buscar_hucha(persona, "mis_cosas")
    tienes = max(tus_cosas["quedan"], 0.0)
    falta = round(max(meta["importe"] - meta["ahorrado"], 0.0), 2)
    if falta == 0:
        raise NoSePuedeGuardar("Esta hucha ya está llena.")
    if importe > tienes:
        raise NoSePuedeGuardar(f"Este mes te quedan {euros(tienes)}. No puedes meter {euros(importe)}.")
    if importe > falta:
        raise NoSePuedeGuardar(f"A esta hucha solo le faltan {euros(falta)}.")
    meta["ahorrado"] = round(meta["ahorrado"] + importe, 2)
    persona["movimientos"].append({
        "fecha": hoy().isoformat(), "concepto": f"A la hucha {meta['nombre']}", "importe": importe,
        "tipo": "gasto", "hucha": "mis_cosas", "destinatario": "Hucha", "registrado_por": "persona",
        "meta": meta["id"],  # traspaso a una hucha de ahorro: baja de tus cosas, pero no es un gasto
    })
    quedan = round(tienes - importe, 2)
    frases = [f"Has metido {euros(importe)} en la hucha {meta['nombre']}.",
              f"En la hucha tienes {euros(meta['ahorrado'])}.",
              f"Este mes te quedan {euros(quedan)} para {nombre_en_frase(tus_cosas)}."]
    return {"meta": progreso_meta(meta), "quedan": quedan, "texto_lectura_facil": " ".join(frases)}


def progreso_meta(meta: dict[str, Any]) -> dict[str, Any]:
    falta = round(max(meta["importe"] - meta["ahorrado"], 0.0), 2)
    meses = 0 if falta == 0 else -(-falta // meta["aporte_mensual"])
    frases = [f"{meta['nombre']}: tienes {euros(meta['ahorrado'])}."]
    if falta == 0:
        frases.append("Ya tienes todo el dinero.")
    else:
        cuando = "1 mes" if meses == 1 else f"{int(meses)} meses"
        frases += [f"Te faltan {euros(falta)}.",
                   f"Si guardas {euros(meta['aporte_mensual'])} cada mes, lo consigues en {cuando}."]
    texto = " ".join(frases)
    return {**meta, "falta": falta, "meses_restantes": int(meses), "texto_lectura_facil": texto}

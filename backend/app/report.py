"""Informe anual de rendición de cuentas para el juzgado, en PDF.

Es un borrador que prepara la persona de apoyo (N3 o N4). Cada resolución
judicial puede pedir cosas distintas: revisad la plantilla con P6.
"""

from __future__ import annotations

import io
from collections import defaultdict
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .easyread import euros
from .store import hoy


def resumen(persona: dict[str, Any], anio: int) -> dict[str, Any]:
    movs = [m for m in persona["movimientos"] if m["fecha"].startswith(str(anio))]
    ingresos: dict[str, float] = defaultdict(float)
    gastos: dict[str, float] = defaultdict(float)
    nombres = {h["id"]: h["nombre"] for h in persona["huchas"]}
    ahorro = 0.0
    for m in movs:
        if m["tipo"] == "ingreso":
            ingresos[m["concepto"]] += m["importe"]
        elif m["hucha"] == "ahorro" or m.get("meta"):
            ahorro += m["importe"]  # Traspaso a la cuenta de ahorro: no es un gasto.
        else:
            gastos[nombres.get(m["hucha"], m["hucha"] or "Otros")] += m["importe"]
    total_ing = round(sum(ingresos.values()), 2)
    total_gas = round(sum(gastos.values()), 2)
    inicial = persona.get("saldo_inicial_anio", 0.0)
    return {
        "anio": anio,
        "saldo_inicial": inicial,
        "ingresos": {k: round(v, 2) for k, v in ingresos.items()},
        "gastos_por_hucha": {k: round(v, 2) for k, v in gastos.items()},
        "total_ingresos": total_ing,
        "total_gastos": total_gas,
        "traspasado_a_ahorro": round(ahorro, 2),
        "saldo_final": round(inicial + total_ing - total_gas, 2),
        "decisiones": [d for d in persona["decisiones"] if d["fecha"].startswith(str(anio))],
        "avisos_estafa": sum(1 for a in persona.get("avisos", [])
                             if a["tipo"] == "posible_estafa" and a["fecha"].startswith(str(anio))),
        "registrados_por_apoyo": [m for m in movs if m["registrado_por"] not in ("banco", "persona")],
        "hasta": hoy().isoformat(),
    }


def generar_pdf(persona: dict[str, Any], preparado_por: dict[str, Any], anio: int) -> bytes:
    r = resumen(persona, anio)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            title=f"Rendición de cuentas {anio} - {persona['nombre']}")
    st = getSampleStyleSheet()
    el: list[Any] = []

    el.append(Paragraph(f"Rendición de cuentas del ejercicio {anio}", st["Title"]))
    el.append(Paragraph(
        f"Persona: <b>{persona['nombre']}</b><br/>"
        f"Preparado por: <b>{preparado_por['nombre']}</b> ({preparado_por['relacion']})<br/>"
        f"Medida de apoyo: {preparado_por.get('documento', 'Guarda de hecho')}<br/>"
        f"Periodo: 1 de enero de {anio} a {r['hasta']}", st["Normal"]))
    el.append(Spacer(1, 0.5 * cm))

    el.append(Paragraph("1. Resumen", st["Heading2"]))
    el.append(_tabla([
        ["Saldo al inicio del periodo", euros(r["saldo_inicial"])],
        ["Total de ingresos", euros(r["total_ingresos"])],
        ["Total de gastos", euros(r["total_gastos"])],
        ["De ese saldo, guardado en la cuenta de ahorro", euros(r["traspasado_a_ahorro"])],
        ["Saldo al final del periodo (cuentas + ahorro)", euros(r["saldo_final"])],
    ]))

    el.append(Paragraph("2. Ingresos", st["Heading2"]))
    el.append(_tabla([["Concepto", "Importe"]] + [[k, euros(v)] for k, v in r["ingresos"].items()], cabecera=True))

    el.append(Paragraph("3. Gastos por categoría", st["Heading2"]))
    el.append(_tabla([["Categoría", "Importe"]] + [[k, euros(v)] for k, v in r["gastos_por_hucha"].items()], cabecera=True))

    el.append(Paragraph("4. Decisiones tomadas por la persona", st["Heading2"]))
    el.append(Paragraph(
        "Registro de las decisiones que la persona tomó con ayuda del asistente, "
        "como constancia de su voluntad y preferencias (Ley 8/2021).", st["Normal"]))
    if r["decisiones"]:
        filas = [["Fecha", "Qué", "Importe", "Decisión", "Pidió apoyo"]]
        for d in r["decisiones"]:
            filas.append([d["fecha"][:10], d["concepto"], euros(d["importe"]),
                          d["decision"], "Sí" if d["pidio_apoyo"] else "No"])
        el.append(_tabla(filas, cabecera=True))
    else:
        el.append(Paragraph("Sin decisiones registradas en el periodo.", st["Italic"]))

    el.append(Paragraph("5. Avisos de posible estafa", st["Heading2"]))
    el.append(Paragraph(
        "Veces en que Willo hizo una pausa para pensar antes de enviar dinero. Willo nunca bloquea "
        "un pago: la decisión fue siempre de la persona y se recoge tal cual.", st["Normal"]))
    avisos = avisos_estafa(persona, anio)
    if avisos:
        el.append(_tabla_avisos(avisos, st))
    else:
        el.append(Paragraph("Sin avisos de posible estafa en el periodo.", st["Italic"]))

    if r["registrados_por_apoyo"]:
        el.append(Paragraph("6. Gastos registrados por la persona de apoyo", st["Heading2"]))
        filas = [["Fecha", "Concepto", "Importe", "Registrado por"]]
        for m in r["registrados_por_apoyo"]:
            filas.append([m["fecha"], m["concepto"], euros(m["importe"]), m["registrado_por"]])
        el.append(_tabla(filas, cabecera=True))

    el.append(Spacer(1, 0.8 * cm))
    el.append(Paragraph(
        "Borrador generado por Willo. Revíselo y adáptelo a lo que pida la resolución judicial "
        "antes de presentarlo. Demo con datos inventados.", st["Italic"]))
    doc.build(el)
    return buf.getvalue()


def que_decidio(aviso: dict[str, Any]) -> str:
    """Lo que hizo la persona, dicho tal cual. Sin juzgar si envió el dinero."""
    resultado = aviso.get("resultado")
    pidio = aviso.get("estado") == "javi_pide_hablar"
    con_quien = " y ".join(aviso.get("para_nombres") or [aviso.get("para_nombre", "su apoyo")])
    if resultado is None:
        return f"Pidió hablar con {con_quien}. Sin decisión registrada." if pidio else "Sin decisión registrada."
    if resultado.get("enviado"):
        return f"Habló con {con_quien} y envió el dinero." if pidio else "Envió el dinero."
    return f"Avisó a {con_quien}. Dinero no enviado." if pidio else "Dinero no enviado."


def avisos_estafa(persona: dict[str, Any], anio: int) -> list[dict[str, Any]]:
    return [a for a in persona.get("avisos", [])
            if a["tipo"] == "posible_estafa" and a["fecha"].startswith(str(anio))]


def _tabla_avisos(avisos: list[dict[str, Any]], st: Any) -> Table:
    from xml.sax.saxutils import escape
    from reportlab.lib.styles import ParagraphStyle
    celda = ParagraphStyle("celda", parent=st["Normal"], fontSize=9, leading=11)
    filas = [["Fecha", "A quién", "Importe", "Lo que Willo le explicó", "Qué decidió"]]
    for a in avisos:
        senales = "<br/>".join("• " + escape(x) for x in a.get("senales", [])) or "—"
        filas.append([a["fecha"][:10], Paragraph(escape(a.get("destinatario", "—")), celda),
                      euros(a["importe"]) if a.get("importe") is not None else "—",
                      Paragraph(senales, celda), Paragraph(escape(que_decidio(a)), celda)])
    t = Table(filas, hAlign="LEFT", repeatRows=1,
              colWidths=[2.1 * cm, 2.4 * cm, 1.9 * cm, 6.4 * cm, 4.2 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF7")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    return t


def _tabla(filas: list[list[str]], cabecera: bool = False) -> Table:
    t = Table(filas, hAlign="LEFT")
    estilo = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if cabecera:
        estilo += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF7")),
                   ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(estilo))
    return t

"""Cifras de lectura fácil para el pitch: texto original frente a lo que dice Noa.

Uso, desde la carpeta backend:
    python -m scripts.cifras_pitch
    python -m scripts.cifras_pitch "Pega aquí el texto de un papel real"

Los textos originales de abajo están escritos por el equipo, al estilo de los papeles
reales (no son copias de documentos de nadie). Las frases de Noa son las que devuelve la API.
"""

from __future__ import annotations

import sys

from app.easyread import comprobar

EJEMPLOS = [
    (
        "Carta falsa de la Seguridad Social",
        "Le comunicamos que, tras la revisión de su expediente de prestaciones, se ha detectado un "
        "pago indebido que deberá regularizar mediante transferencia bancaria en el plazo improrrogable "
        "de 48 horas, a fin de evitar la suspensión cautelar de su prestación y el inicio del "
        "correspondiente procedimiento sancionador.",
        "Cuidado. Este papel puede ser una estafa. Los bancos nunca te piden tu clave ni tu PIN. "
        "Tú decides qué hacer. ¿Quieres hablarlo con Ana?",
    ),
    (
        "Multa de aparcamiento",
        "Se le notifica la denuncia formulada por infracción del artículo 94.2 del Reglamento General "
        "de Circulación, consistente en estacionar en zona reservada para carga y descarga, sancionada "
        "con multa de 90 euros, pudiendo acogerse a la reducción del importe si efectúa el pago dentro "
        "del plazo de veinte días naturales contados desde el siguiente a la notificación.",
        "He leído: multa de aparcamiento. 90 €. Hay que pagar antes del 20 de diciembre. ¿Es correcto?",
    ),
    (
        "Factura de la luz",
        "El importe correspondiente al periodo de facturación indicado será cargado en la cuenta "
        "bancaria designada a tal efecto en la fecha de vencimiento señalada, de conformidad con las "
        "condiciones generales del contrato de suministro eléctrico suscrito por el titular.",
        "Ya estaba en tu plan. Se paga solo el día 20. No tienes que hacer nada.",
    ),
]


def fila(nombre: str, original: str, noa: str) -> str:
    a, b = comprobar(original), comprobar(noa)
    return f"| {nombre} | {a['indice_fernandez_huerta']} | {b['indice_fernandez_huerta']} |"


def main() -> None:
    if len(sys.argv) > 1:
        r = comprobar(" ".join(sys.argv[1:]))
        print(f"Nota: {r['indice_fernandez_huerta']} · fácil: {'sí' if r['es_facil'] else 'no'}")
        for p in r["problemas"]:
            print(f"- {p}")
        return
    print("| Papel | Original | Noa |")
    print("|---|---|---|")
    for e in EJEMPLOS:
        print(fila(*e))
    print("\nEscala: 0-30 muy difícil · 30-50 difícil · 50-60 algo difícil · 60-70 normal · "
          "70-80 bastante fácil · 80-90 fácil · 90-100 muy fácil.")


if __name__ == "__main__":
    main()

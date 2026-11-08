# Willo · Datos de ejemplo para la demo

Objetivo: que los números del backend (`backend/data/seed.json`) sean los mismos que salen en las pantallas y en el guion.
Todos los datos son inventados. Ninguna persona es real.

Fecha de la demo dentro de la app: **domingo, 8 de noviembre de 2026**.

---

## 1. Javi

| Dato | Valor |
|---|---|
| Edad | 34 años |
| Trabajo | Lavandería (centro especial de empleo) |
| Ingreso | **Nómina de 980 € al mes**, el día 1 |
| Vive | En una habitación de un piso compartido |

### Dinero apartado cada mes (lo hace el código, no Javi)

| Concepto | Importe | Día | Destinatario |
|---|---|---|---|
| Alquiler de la habitación | 350 € | 2 | Piso compartido |
| Luz | 42 € | 20 | Compañía de la luz |
| Abono de transporte | 20 € | 3 | Consorcio de Transportes |
| Comida (supermercado) | 220 € | — | Supermercado del barrio |
| Hucha "Viaje a Valencia" | 40 € | 6 | Hucha |
| Hucha "Móvil nuevo" | 20 € | 6 | Hucha |
| **Total apartado** | **692 €** | | |

**Para sus cosas cada mes: 980 − 692 = 288 €.**

### Lo que ya ha gastado en sus cosas en noviembre

| Día | Concepto | Importe | Dónde |
|---|---|---|---|
| 2 | Camiseta | 30 € | Tienda de ropa |
| 4 | Peluquería | 14 € | Peluquería del barrio |
| 6 | Cine con amigos | 12 € | Cines del centro |
| 7 | Bar con amigos | 22 € | Bar La Esquina |
| | **Total** | **78 €** | |

**Le quedan: 288 − 78 = 210 €** ← la cifra grande de la pantalla 1.

### Huchas (metas de ahorro)

| Hucha | Ahorrado | Meta | Aporte al mes |
|---|---|---|---|
| Viaje a Valencia | 120 € | 300 € | 40 € |
| Móvil nuevo | 45 € | 200 € | 20 € |

### Destinatarios conocidos
Piso compartido, Compañía de la luz, Consorcio de Transportes, Supermercado del barrio, Tienda de ropa, Peluquería del barrio, Cines del centro, Bar La Esquina, Ana.
**Carlos NO está**: por eso salta "persona nueva" en la estafa.

---

## 2. Lo que pasa en la demo (y cómo cambian los números)

| Momento | Qué pasa | Le quedan para sus cosas |
|---|---|---|
| Inicio | — | **210 €** |
| Pregunta por la entrada | Noa calcula 210 − 45 | (si la compra: 165 €) |
| Paga la entrada en la taquilla | Gasto de 45 €, "Entradas Concierto" (destinatario nuevo, pero es pago con tarjeta: no hay pausa) | **165 €** |
| Foto de la multa | Multa de aparcamiento, 90 €, Ayuntamiento, pagar antes del 20 de diciembre. No estaba prevista | (si la paga: 75 €) |
| Bizum a Carlos | 300 € a persona nueva, con prisa, más de lo que le queda → pausa para pensar. No lo envía | 165 € |

**Decidido (8 nov):** la multa va después de la entrada, así que la pantalla 7 dice **165 € → 75 €**.

**Aviso a Ana (decidido 8 nov):** en cuanto aparece la pausa para pensar, Ana recibe "Posible estafa" (si Javi dio permiso antes). Si Javi pulsa "Avisar a Ana", el mismo aviso cambia a "Javi ha pedido hablar contigo"; no se manda un segundo aviso.

---

## 3. Ana (círculo de apoyo)

| Dato | Valor |
|---|---|
| Relación | Hermana |
| Modo | **Guardar** (guardadora de hecho) |
| Ve | Pagos, avisos de estafa, cuentas para el juez |
| Puede bloquear | **Nada** |

Propuesta: quitar del ejemplo la "Fundación tutelar" con curatela que hay ahora en `seed.json`. Con Ana en "Guardar" basta, y dos personas de apoyo en la demo confunden.

En el backend los modos van como número; mapa: Solo yo = 0, Ver = 1, Apoyar = 2, Guardar = 3, Representar = 4. En pantalla siempre se enseña el **nombre**, nunca el número.

---

## 4. Informe anual (pantalla 10)

Sale del backend, pero para que cuadre con la pantalla:
- Dinero que entró: 12 × 980 = **11.760 €**
- Dinero que gastó: **10.950 €**
- Ahorro en huchas: **810 €** (los aportes de las huchas más lo que sobró algunos meses)
- Decisiones importantes: **3**
- Avisos de estafa: **1** (Bizum de 300 € a Carlos, no enviado)

Para la demo hace falta que el backend tenga historial de los meses anteriores, o que el informe use estas cifras fijas marcadas como ejemplo.

---

## 5. Reserva (no hace falta para la demo)

- **Lucía**, 14 años, paga de 80 € al mes. Meta: **Bici, 0 € de 150 €, 10 € a la semana** (15 semanas). Ahora en `seed.json` tiene una "Consola"; cambiarla a Bici si se usa.
- **Documento sospechoso:** carta que pide la clave del banco.

---

## 6. Qué hay que cambiar en el código (lo hace quien lleve el backend)

En `backend/data/seed.json`:
1. Ingresos de Javi: una sola nómina de 980 € (quitar 780 + 290).
2. Gastos recurrentes y movimientos de noviembre: los de las tablas de arriba.
3. Huchas de gasto y metas: que "Mis cosas" sea 288 € y añadir las metas Viaje a Valencia y Móvil nuevo.
4. Círculo: Ana con nivel 3 ("Guardar"); quitar la fundación.
5. Lucía: meta Bici (solo si se usa la reserva).

Después, pasar los tests (`pytest`) porque algunos usan los números antiguos.

# Willo · Contrato de endpoints

Qué pide cada pantalla al backend y qué le devuelve. Sirve para que pantallas, backend y Noa (ElevenLabs) hablen el mismo idioma.
Revisado por Inés (8 nov). Cristina: echarle un vistazo. Fecha: 8 de noviembre de 2026.

Leyenda: ✅ ya existe · ✏️ existe pero hay que cambiarlo · 🆕 hay que crearlo.

Reglas para todos:
- Base: `http://localhost:8000`. Persona de la demo: `javi`.
- Las cuentas las hace el backend. La IA solo pone texto en lectura fácil.
- Cada respuesta para Javi trae `texto_lectura_facil` (lo que dice Noa) y, si toca, `pictograma`.
- No usamos `WILLO_TOOL_TOKEN` en la demo: si se define, las pantallas dejan de funcionar porque no mandan la cabecera `X-Willo-Token`.
- Ejemplos con los datos de `datos-ejemplo.md` (980 €/mes, 210 € para sus cosas).

---

## Resumen

| Pantalla | Endpoint | Estado |
|---|---|---|
| 1 Inicio | `GET /api/personas/javi/presupuesto` | ✅ |
| 1 Inicio | `GET /api/personas/javi/metas` | ✅ (faltan las metas de Javi en el seed) |
| 2 Hablar con Noa | `GET /api/voz/signed-url` | ✅ |
| 3 Respuesta | `POST /api/personas/javi/evaluar_compra` | ✅ |
| 4 Aviso de pago | `POST /api/personas/javi/decisiones` | ✅ |
| 5-6 Foto y "¿es correcto?" | `POST /api/personas/javi/documentos/leer` | 🆕 |
| 7 Noa explica | `POST /api/personas/javi/documentos/confirmar` | 🆕 |
| 8 Pausa para pensar | `POST /api/personas/javi/evaluar_riesgo` | ✏️ (un solo aviso) |
| 8 "Avisar a Ana" | `POST /api/personas/javi/avisos/{id}/pedir_hablar` | 🆕 |
| 9 Móvil de Ana | `GET /api/personas/javi/avisos?para=ana` | ✏️ (estado del aviso) |
| 10 Informe | `GET /api/personas/javi/informe_anual/resumen` | ✏️ (añadir avisos de estafa) |
| 10 PDF | `GET /api/personas/javi/informe_anual?preparado_por=ana` | ✅ |
| 11 Detalle estafas | `GET /api/personas/javi/avisos?tipo=posible_estafa` | ✏️ (filtro y resultado) |
| Demo | `POST /api/demo/reset` | ✅ |

---

## 1. Inicio de Javi

### ✅ `GET /api/personas/javi/presupuesto`
La pantalla usa la hucha `mis_cosas` para la cifra grande.
```json
{
  "persona": "Javi",
  "fecha": "2026-11-08",
  "huchas": [
    {"id": "mis_cosas", "nombre": "Mis cosas", "pictograma": "bolsa",
     "limite_mensual": 288.0, "gastado": 78.0, "quedan": 210.0}
  ],
  "texto_lectura_facil": "En mis cosas te quedan 210 €."
}
```

### ✅ `GET /api/personas/javi/metas`
```json
[
  {"id": "valencia", "nombre": "Viaje a Valencia", "importe": 300.0, "ahorrado": 120.0, "aporte_mensual": 40.0, "...": "..."},
  {"id": "movil", "nombre": "Móvil nuevo", "importe": 200.0, "ahorrado": 45.0, "aporte_mensual": 20.0, "...": "..."}
]
```
Pendiente: añadir estas dos metas a Javi en `seed.json`.

## 2-3. Hablar con Noa y respuesta

### ✅ `GET /api/voz/signed-url`
Devuelve la URL firmada de ElevenLabs para hablar con Noa sin enseñar la clave. Si faltan claves → `503` y la pantalla usa el modo sin voz.

### ✅ `POST /api/personas/javi/evaluar_compra` (herramienta de Noa)
Petición:
```json
{"importe": 45, "concepto": "la entrada del concierto"}
```
Respuesta:
```json
{
  "hucha": "mis_cosas", "quedan_antes": 210.0, "importe": 45.0,
  "quedan_despues": 165.0, "alcanza": true, "pausa_para_pensar": false,
  "pictograma": "bolsa", "frase_comida": "El dinero de la comida está aparte.",
  "texto_lectura_facil": "En la hucha de tus cosas te quedan 210 €. Si compras la entrada del concierto, te quedan 165 €. El dinero de la comida está aparte. Tú decides."
}
```

## 4. Aviso de pago

### ✅ `POST /api/personas/javi/decisiones`
La usa el botón escondido "simular pago" (y Noa si Javi dice que lo compra).
```json
{"concepto": "entrada del concierto", "importe": 45, "decision": "comprar", "compartir": true}
```
Respuesta:
```json
{"guardado": {"...": "..."}, "avisados": ["Ana"], "texto_lectura_facil": "Lo he apuntado. Es tu decisión."}
```
**Decidir no es pagar** (10 nov). Con `"decision": "comprar"`:
- sin `pagado` (lo que manda Noa): la compra se apunta en "Quiero comprar" y **el dinero no baja**. A Ana le llega: "Javi ha decidido comprar entrada del concierto. Lo decidió él." La respuesta trae `compra_pendiente`.
- con `"pagado": true` (el botón "simular pago" y "Enviar igualmente"): se apunta el gasto, **el dinero baja** y, si estaba en "Quiero comprar", sale de ahí. A Ana le llega: "Javi compró entrada del concierto. Lo decidió él."

### 🆕 Compras (pantalla 12 "Mis compras")
- `GET /api/personas/javi/compras` → `{"pendientes": [{"id": "co_1", "concepto": "...", "importe": 45, "caduca": "2026-11-17", "dias_restantes": 7}], "pagadas": [{"concepto": "...", "importe": 45, "fecha": "2026-11-10"}], "dias_caducidad": 7}`. `pagadas` son los gastos del mes de la hucha "Para tus cosas".
- `POST /api/personas/javi/compras/{id}/pagada` → Javi ya lo ha pagado: pasa a pagadas y el dinero baja. Willo no paga nada, solo lo apunta.
- `DELETE /api/personas/javi/compras/{id}` → "Ya no lo quiero": se quita. El dinero no cambia.
- Lo que está en "Quiero comprar" **se quita solo a los 7 días** si no se ha pagado.

## 5-7. Noa lee un documento 🆕

Dos pasos para cumplir la regla "confirmar antes de usar los datos".

### 🆕 `POST /api/personas/javi/documentos/leer`
- Entrada: `multipart/form-data` con `foto` (jpg/png).
- El backend manda la imagen a **Claude con visión** y le pide este JSON fijo. **No guarda la imagen.**
- Todavía no hace cuentas: solo lo que pone el documento.

Respuesta:
```json
{
  "tipo": "multa",
  "titulo": "Multa de aparcamiento",
  "remitente": "Ayuntamiento",
  "importe": 90.0,
  "fecha_limite": "2026-12-20",
  "accion": "pagar",
  "sospechoso": false,
  "motivo_sospecha": null,
  "pictograma": "coche",
  "texto_lectura_facil": "He leído: multa de aparcamiento. 90 €. Hay que pagar antes del 20 de diciembre. ¿Es correcto?"
}
```
Valores de `tipo`: `factura`, `recibo`, `ticket`, `nomina`, `multa`, `carta_banco`, `mensaje`, `otro`.
- `mensaje`: pantallazo de un WhatsApp, SMS, Instagram o correo. Trae además `texto_mensaje` (lo que escribe la otra persona) y `telefono` (si se ve el número). **Las reglas antiestafa (código) revisan el mensaje** igual que cuando Javi lo cuenta por voz: si ven riesgo medio o alto, `sospechoso` es `true` aunque Claude no lo vea. La respuesta trae `senales` (frases cortas). Ejemplo: "He leído: mensaje de Carlos. Te pide 300 €. ¿Es correcto?"
- `ticket`: el ticket de una compra que Javi ya ha hecho (tienda, bar, supermercado). `accion` suele ser `nada`: ya está pagado.
Valores de `accion`: `pagar`, `nada`, `contestar`, `revisar`.
Si Claude no puede leerlo → `422` con `"texto_lectura_facil": "No he podido leerlo bien. ¿Haces otra foto con más luz?"`.
Si `sospechoso` es `true`, Noa ya avisa al leerlo, antes de "¿Es correcto?": "He leído: carta de la Seguridad Social. Cuidado: puede ser un engaño. Te pide tu DNI y datos del banco. ¿Es correcto?". El motivo solo se lee si es corto (15 palabras o menos); entero sigue en `motivo_sospecha`.

### 🆕 `POST /api/personas/javi/documentos/confirmar`
Javi pulsó "Sí, es correcto" (o corrigió un dato). Se manda lo leído, ya confirmado. Aquí el **código** hace las cuentas.

Petición:
```json
{"tipo": "multa", "titulo": "Multa de aparcamiento", "remitente": "Ayuntamiento",
 "importe": 90.0, "fecha_limite": "2026-12-20", "sospechoso": false}
```
Respuesta:
```json
{
  "en_plan": false,
  "quedan_antes": 165.0,
  "quedan_despues": 75.0,
  "alcanza": true,
  "pictograma": "coche",
  "texto_lectura_facil": "No estaba en tu plan. Si la pagas, te quedan 75 € para tus cosas. Tienes hasta el 20 de diciembre. ¿Quieres hablarlo con Ana?"
}
```
- Si `tipo` es `ticket`, no se resta otra vez: el pago con tarjeta ya está en sus movimientos. Solo se explica: "Es el ticket de la tienda de ropa. Pagaste 30 €. Ya está apuntado. Te quedan 210 € para tus cosas." Si el gasto no aparece en sus movimientos (pagó en efectivo), se apunta como gasto de "Para tus cosas".
- `en_plan` es `true` si el importe y el remitente coinciden con un gasto recurrente (por ejemplo, la luz). Entonces: "Ya estaba en tu plan. No tienes que hacer nada."
- Si es un `mensaje`, se manda también `texto_mensaje` y `telefono`. Las reglas lo revisan otra vez; si el riesgo es alto y Javi dio permiso, se crea **el mismo aviso para Ana** que en la pantalla 8 y se devuelve `aviso_id`. Noa: "Cuidado. Este mensaje puede ser un engaño. No tienes guardado este número. … Tú decides qué hacer. Como acordaste, he avisado a Ana."
- Si `sospechoso` es `true` (pantalla de reserva R1), no se hacen cuentas: "Cuidado. Este documento te pide tu clave del banco. Los bancos nunca piden eso..."
- **No paga nada.** "Hablar con Ana" usa `POST /decisiones` con `"decision": "hablarlo"`.

## 8-9. Estafa y aviso a Ana

### ✏️ `POST /api/personas/javi/evaluar_riesgo` (herramienta de Noa)
Petición:
```json
{"destinatario": "Carlos", "importe": 300,
 "contexto": "Un chico de Instagram me pide 300 euros por Bizum ahora, que mañana me los devuelve"}
```
Respuesta (campos reales de `risk.py`, más `aviso_id` nuevo):
```json
{
  "nivel_riesgo": "alto",
  "puntos": 6,
  "senales": [
    {"id": "destinatario_nuevo", "peso": 2, "explicacion": "Nunca has enviado dinero a Carlos."},
    {"id": "urgencia", "peso": 2, "explicacion": "Te pide prisa."},
    {"id": "importe_alto", "peso": 2, "explicacion": "Son 300 €. Es más de lo que te queda este mes para tus cosas."}
  ],
  "preguntas": ["..."],
  "bloquea": false,
  "sugerir_aviso_apoyo": true,
  "aviso_id": "av_7",
  "avisados": ["Ana"],
  "texto_lectura_facil": "Espera un momento. ... ¿Quieres hablar con Ana antes?"
}
```
La pantalla 8 enseña la pausa cuando `nivel_riesgo` no es `bajo`, y las razones salen de `senales[].explicacion`.

Cambios (decidido el 8 de noviembre):
- Crea **un solo aviso** para Ana, al momento, si Javi dio permiso (modo Apoyar o superior), y devuelve su `aviso_id`.
- **Nunca bloquea.** Los botones "Enviar igualmente" y "No enviar" los pulsa Javi.
- `bloquea` siempre es `false`.

### 🆕 `POST /api/personas/javi/avisos/{aviso_id}/pedir_hablar`
Javi pulsó "Avisar a Ana". No crea otro aviso: cambia el que ya hay.
Respuesta:
```json
{"id": "av_7", "estado": "javi_pide_hablar",
 "texto": "Javi ha pedido hablar contigo.",
 "texto_lectura_facil": "Se lo he dicho a Ana. Te llamará."}
```

### 🆕 `POST /api/personas/javi/avisos/pedir_hablar` (sin id: riesgo medio)
Con riesgo **medio** no se avisa a nadie solo, así que `evaluar_riesgo` no devuelve `aviso_id`. Si Javi pulsa "Avisar a Ana", la pantalla llama a esta ruta con los datos del envío (los mismos que `evaluar_riesgo`):
```json
{"destinatario": "Carlos", "importe": 300, "contexto": ""}
```
Si ya había un aviso de ese envío, lo usa (`"creado": false`). Si no, lo crea en ese momento, ya con `estado: "javi_pide_hablar"` (`"creado": true`). Respuesta igual que la de arriba, más `creado`. `409` si no hay nadie en el círculo que pueda ver sus decisiones.

Regla para la pantalla 8: si `aviso_id` existe → `/avisos/{aviso_id}/pedir_hablar`; si no → `/avisos/pedir_hablar` con el envío.

### 🆕 Resultado del envío
Cuando Javi pulsa "No enviar" o "Enviar igualmente", se guarda en el mismo aviso:
`POST /api/personas/javi/avisos/{aviso_id}/resultado` con `{"enviado": false}`.
Lo usa la pantalla 11 ("Dinero no enviado").

### ✏️ `GET /api/personas/javi/avisos?para=ana`
Cada aviso trae ahora `id`, `estado` y `resultado`:
```json
[
  {"id": "av_7", "tipo": "posible_estafa", "para": "ana", "fecha": "2026-11-08T19:10:00",
   "estado": "javi_pide_hablar", "resultado": {"enviado": false},
   "destinatario": "Carlos", "importe": 300.0,
   "senales": ["Carlos es una persona nueva.", "Te pide prisa.", "300 € es mucho para ti este mes."],
   "texto": "Javi quiere enviar 300 € a Carlos."},
  {"id": "av_6", "tipo": "decision", "para": "ana", "fecha": "2026-11-08T19:02:00",
   "texto": "Javi compró entrada del concierto. Lo decidió él."}
]
```
Valores de `estado`: `nuevo`, `javi_pide_hablar`.

### 🆕 Contactos del móvil
`evaluar_riesgo` admite también `"telefono"`. Si el número no está en los contactos de Javi → señal `numero_desconocido` ("No tienes guardado este número."). Si dice ser alguien conocido desde otro número → "Dice que es Ana, pero no tienes guardado este número." (la estafa de "este es mi número nuevo").

Los contactos los **elige Javi** en su agenda (Contact Picker del navegador: Chrome en Android; Safari en iPhone todavía no). Se guarda solo nombre y número. Nunca se mandan a la IA.
- `GET /api/personas/javi/contactos`
- `POST /api/personas/javi/contactos` con `{"contactos": [{"nombre": "Ana", "telefono": "+34 600 000 101"}]}` → `{"nuevos": 1, "total": 3, "texto_lectura_facil": "..."}`
- `DELETE /api/personas/javi/contactos` (todos) y `DELETE /api/personas/javi/contactos/{telefono}` (uno)

## 10-11. Informe

### ✏️ `GET /api/personas/javi/informe_anual/resumen`
Ya devuelve (`report.py`): `anio`, `saldo_inicial`, `ingresos` (por concepto), `gastos_por_hucha`, `total_ingresos`, `total_gastos`, `traspasado_a_ahorro`, `saldo_final`, `decisiones`, `registrados_por_apoyo`, `hasta`.
Cambio: añadir `avisos_estafa` para no tener que contarlos en la pantalla:
```json
{"anio": 2026, "total_ingresos": 11760.0, "total_gastos": 10950.0, "traspasado_a_ahorro": 810.0,
 "decisiones": ["..."], "avisos_estafa": 1, "...": "..."}
```
La pantalla 10 enseña: Dinero que entró = `total_ingresos`, Dinero que gastó = `total_gastos`, Ahorro en huchas = `traspasado_a_ahorro`, Decisiones importantes = nº de `decisiones`.

### ✅ `GET /api/personas/javi/informe_anual?preparado_por=ana`
Devuelve el PDF. Ana está en "Guardar" (nivel 3), así que tiene permiso. Con "Apoyar" devuelve `403`.

### ✏️ `GET /api/personas/javi/avisos?tipo=posible_estafa`
Pantalla 11: añadir el filtro `tipo`. Cada aviso trae `senales` y `resultado`, como arriba.

---

## Modos del círculo de apoyo

En la API van como número; en pantalla siempre el nombre.

| Número | Nombre | Quién lo da |
|---|---|---|
| 0 | Solo yo | Javi |
| 1 | Ver | Javi |
| 2 | Apoyar | Javi |
| 3 | Guardar | Situación legal (guarda de hecho) |
| 4 | Representar | Juez o notario |

`PUT /api/personas/javi/circulo/{miembro}` solo deja a Javi poner 0, 1 o 2.

---

## Decidido (Inés, 8 de noviembre de 2026)

1. **Leer documento en dos pasos** (`/documentos/leer` y luego `/documentos/confirmar`). Javi comprueba lo leído antes de que se hagan cuentas, porque la IA puede leer mal una cifra. Pantallas 5, 6 y 7.
2. **Modelo: Claude Haiku** (con visión), con la clave de la fase 1. Antes, probarlo con 5 fotos reales: factura, ticket, multa, carta del banco y una foto mala. Si falla con las buenas, cambiar a Sonnet (una línea de código).
3. **Guardar el resultado del envío** con `POST /avisos/{aviso_id}/resultado`. Se apunta igual si Javi no lo envía o si lo envía, sin juzgarle. Lo usan la pantalla 11 y el informe para el juzgado.

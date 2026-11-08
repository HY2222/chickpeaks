# Willo · Cómo integrar las pantallas en Claude Code

Todo lo que necesita Claude Code para convertir el diseño de Figma en las pantallas de la app.
Fecha: 8 de noviembre de 2026. Diseño: fase 0.

---

## 1. Qué hay que construir

- **Demo (construir sí o sí): pantallas 1 a 11.**
- **RESERVA (NO construir para la demo): R1 "Documento sospechoso" y R2 "Lucía y su hucha".** Son las dos últimas. Solo se hacen si sobra tiempo al final; si no, se enseñan en el pitch con la imagen de Figma.

Figma: https://www.figma.com/design/ZXcREoHSq2OEq8h1YKHJKQ
(Las pantallas de reserva están en la página "Reserva" o en la fila de abajo, con nombre "R1" y "R2".)

## 2. Antes de empezar

1. **Acceso a Figma.** Inés comparte el archivo: botón **Share** → escribir el correo del compañero (o "Anyone with the link can view").
2. **(Opcional) Conectar Figma a Claude Code.** En la terminal:
   `claude mcp add --transport http figma https://mcp.figma.com/mcp`
   Luego, dentro de Claude Code, escribir `/mcp` e iniciar sesión en Figma.
   Ojo: con el plan gratuito de Figma hay muy pocos usos al mes. **Por eso este documento trae todo el diseño escrito y no hace falta Figma para programar.**
3. **Rama nueva:** `git checkout main && git pull && git checkout -b pantallas-demo`

## 3. Dónde va en el repo

Las pantallas ya existen en versión simple en `backend/app/static/`:
- `persona.html` → **móvil de Javi** (pantallas 1-8)
- `apoyo.html` → **móvil de Ana** (pantallas 9-11)
- `willo.css` → estilos. **Sustituir los colores azules actuales por los de abajo.**

Las sirve el backend en `/demo` (Javi) y `/demo/apoyo` (Ana). Es una PWA, no app nativa.

## 4. Estilo (copiar tal cual en willo.css)

```css
:root {
  --fondo: #F5F7F0;        /* fondo de pantalla */
  --salvia: #D3DFC8;       /* tarjetas destacadas, círculos de pictograma, fondo de barras */
  --salvia-media: #A3B18F;
  --verde-oscuro: #3E5A34; /* botón principal, cifras importantes */
  --texto: #1E2A1B;
  --texto-suave: #4A5745;  /* textos secundarios */
  --blanco: #FFFFFF;       /* tarjetas normales */
  --aviso-fondo: #FBEFD0;  /* estafa y alertas (ámbar, no rojo, para no asustar) */
  --aviso-borde: #C98A00;
  --aviso-texto: #5C3D00;
}
body { font-family: Helvetica, Arial, sans-serif; background: var(--fondo); color: var(--texto); }
```

Reglas de lectura fácil (obligatorias):
- Letra **Helvetica** (en Figma sale Arimo porque Figma no tiene Helvetica; es la misma forma).
- Textos de **18 px o más**. Títulos 28-34 px en negrita. Cifras grandes hasta 56 px.
- **Una idea por frase**, frases cortas, cada una en su línea.
- Botones de **72 px de alto**, ancho completo, esquinas de 20 px, texto 22 px negrita.
- Tarjetas con esquinas de 20 px y 20 px de margen interior. Pantalla con 24 px a los lados.
- Cada respuesta de Noa va con **voz + texto + pictograma** (dibujo en un círculo salvia).
- Pantalla de móvil de referencia: 390 × 844.

## 5. Piezas que se repiten

| Pieza | Cómo es |
|---|---|
| Botón principal | Fondo `--verde-oscuro`, texto blanco |
| Botón secundario | Fondo blanco, borde 3 px `--verde-oscuro`, texto `--verde-oscuro` |
| Botón aviso | Fondo `--aviso-borde`, texto blanco |
| Tarjeta normal | Fondo blanco |
| Tarjeta destacada | Fondo `--salvia` |
| Caja de aviso | Fondo `--aviso-fondo`, borde 3 px `--aviso-borde`, texto `--aviso-texto`, icono de triángulo |
| Barra de progreso | 20 px de alto, redondeada, fondo `--salvia` (o blanco dentro de tarjeta salvia), relleno `--verde-oscuro` |
| Pictograma | Círculo `--salvia` de 56-64 px con icono verde oscuro dentro. Para la demo valen iconos Lucide; en la versión final, pictogramas ARASAAC |
| Etiqueta gris | "Noa ha oído:", "Noa dice:", "Qué hacer:" en 16-18 px `--texto-suave` encima del texto importante |

## 6. Pantallas de la demo (1 a 11), en orden

### Parte 1 · Javi pregunta y compra (0:20 – 1:20) · móvil de Javi

**1 · Inicio de Javi**
- Arriba: pictograma de persona + "Hola, Javi" + fecha en gris.
- Tarjeta salvia: "Este mes te quedan" / **210 €** (grande, verde) / "Hasta el día 30" / barra.
- "Tus huchas": dos tarjetas blancas con pictograma de hucha, nombre, "120 € de 300 €" y barra (Viaje a Valencia; Móvil nuevo 45 € de 200 €).
- Abajo: botón principal **"Hablar con Noa"** → pantalla 2.

**2 · Hablando con Noa**
- Título centrado "Noa te escucha".
- Círculo grande salvia con círculo verde oscuro dentro y micrófono blanco (animarlo mientras escucha).
- Tarjeta blanca abajo: "Noa ha oído:" + la transcripción en directo en negrita (Scribe de ElevenLabs): «¿Puedo comprar la entrada del concierto? Cuesta 45 euros.»
- Botón secundario "Parar".

**3 · Respuesta de Noa**
- Tarjeta blanca: pictograma de entrada + "Entrada del concierto" / "Cuesta 45 €".
- "Noa dice:" y tres frases, una por línea: "Este mes te quedan 210 €." / "Si compras la entrada, te quedan 165 €." / "Con 165 € tienes para comida hasta el día 30."
- Tarjeta salvia "Ahora: 210 €" con barra y "Después: 165 €" con barra más corta.
- "Tú decides." en verde, grande.
- Botones: secundario "Escuchar otra vez", principal "Entendido".
- Las cuentas las hace el backend, nunca la IA. Noa explica, no recomienda.

**4 · Aviso de pago**
- Javi paga en la taquilla con su tarjeta. En la demo: **botón escondido "simular pago"** que crea el gasto en el backend.
- Pictograma de check grande, "Has pagado 45 €", "en Entradas Concierto".
- Tarjeta salvia: "Te quedan" / **165 € este mes** / barra.
- Nota blanca: "Ana ve este pago porque tú lo elegiste."
- Botón principal "Vale".

### Parte 2 · Noa lee un documento (1:20 – 2:00) · móvil de Javi

**5 · Hacer foto a un documento**
- Título "Enséñale el documento a Noa".
- Recuadro oscuro de cámara con marco blanco discontinuo.
- "Pon el documento dentro del recuadro." y en gris "Willo no guarda la foto. Solo guarda lo que pone."
- Botones: principal "Hacer foto", secundario "Subir desde la galería".
- La foto la lee **Claude con visión** (no ElevenLabs). Devuelve siempre el mismo formato: tipo, quién lo envía, importe, fecha, qué hay que hacer, si parece sospechoso. **No se guarda la imagen**, solo esos datos.

**6 · ¿Es correcto?**
- "Noa ha leído:" + tarjeta blanca con pictograma de coche y "Multa de aparcamiento", y filas: Cuánto es **90 €** / Hay que pagar antes del **20 de diciembre** / La envía **Ayuntamiento**.
- "¿Es correcto?" grande en verde + "Mira el número en el documento. A veces Noa lee mal."
- Botones: principal "Sí, es correcto", secundario "No, está mal".
- Regla: **no se usan los datos hasta que Javi confirma.**

**7 · Noa explica el documento**
- Tarjeta: pictograma coche + "Multa de aparcamiento" / "90 €".
- "Noa dice:" "No estaba en tu plan." / "Si la pagas, te quedan 120 € para tus cosas." / "Tienes hasta el 20 de diciembre."
- Tarjeta salvia "Ahora: 210 €" / "Si pagas: 120 €" con barras.
- "¿Quieres hablarlo con Ana?"
- Botones: principal "Hablar con Ana", secundario "Ahora no". **Noa no paga nada.**

### Parte 3 · Intento de estafa (2:00 – 2:35)

**8 · Pausa para pensar** · móvil de Javi
- Javi intenta mandar 300 € por Bizum a "Carlos de Instagram".
- Tarjeta blanca: pictograma de enviar + "Enviar 300 €" / "a Carlos, por Bizum".
- Caja de aviso: "Pausa para pensar" / "Espera un momento." / "1. Carlos es una persona nueva." / "2. Te pide prisa." / "3. 300 € es mucho para ti este mes." / "Esto pasa a veces en las estafas."
- "¿Quieres hablar con Ana antes?"
- Botones: principal "Avisar a Ana", secundario "No enviar", secundario "Enviar igualmente".
- La pausa la activan **reglas fijas del código** (persona nueva, prisa, cantidad alta), no la IA. **Willo nunca bloquea**: Javi siempre puede "Enviar igualmente".

**9 · Móvil de Ana** · móvil de Ana
- Pictograma persona + "Hola, Ana" + en gris "Ayudas a Javi como: Guardar".
- Caja de aviso: "Posible estafa" / "Javi quería enviar 300 € a Carlos y ha pedido hablar contigo." / "• Carlos es nuevo • Pide prisa • Cantidad alta" / botón aviso "Llamar a Javi".
- Tarjeta blanca con campana: "Javi ha pagado una entrada de 45 €." / "Lo decidió él. · Hoy, 19:02".
- Gris: "Tú no puedes bloquear pagos. Javi decide y tú le apoyas."
- Botón secundario "Informe anual" → pantalla 10.

### Parte 4 · Informe para el juzgado (2:35 – 2:50) · móvil de Ana

**10 · Informe anual**
- "Informe anual 2026" / "De Javi, para el juzgado. En lectura fácil."
- Tarjeta blanca con borde salvia, "Resumen del año" y filas: Dinero que entró / Dinero que gastó / Ahorro en huchas / Decisiones importantes / Avisos de estafa **1** + enlace **"Mostrar más ›"** → pantalla 11.
- Botones: principal "Descargar PDF", secundario "Compartir".
- Las cifras salen del backend (no copiar las de Figma, son de ejemplo).

**11 · Detalle de estafas**
- "‹ Volver al informe", título "Avisos de estafa", "Lo que pasó cada vez que Willo hizo una pausa para pensar."
- Por cada aviso, tarjeta: fecha / "Bizum de 300 € a Carlos" / "Por qué hubo pausa:" + 3 razones / "Qué decidió Javi:" "Avisó a Ana y no envió el dinero." / recuadro salvia **"✓ Dinero no enviado"** (o "Dinero enviado: 300 €" si lo envió; no se esconde ni se juzga).

## 7. Pantallas de RESERVA (no construir para la demo)

**R1 · Documento sospechoso** (móvil de Javi). Caja de aviso "Cuidado" / "Este documento te pide tu clave del banco." / "Los bancos nunca piden eso." / "Puede ser una estafa." + tarjeta "Qué hacer: No contestes. Díselo a alguien de confianza." + botones aviso "Avisar a Ana" y secundario "Vale".

**R2 · Lucía y su hucha** (modo menores, 14 años). "Hola, Lucía" / "Noa ha oído: «Quiero ahorrar para una bici de 150 euros.»" / tarjeta salvia "Noa dice: Si guardas 10 € cada semana, tienes la bici en 15 semanas." / hucha "Bici 0 € de 150 €" / botones "Crear hucha Bici" y "Ahora no".

## 8. Reglas que no se pueden romper

1. La voz y la IA **explican**; los botones los **pulsa la persona**. Willo nunca compra ni paga.
2. Las cuentas las hace el **código**, no la IA.
3. La pausa para pensar sale de **reglas fijas**, solo en Bizum y transferencias. Nunca bloquea.
4. Ana ve lo que Javi ha elegido compartir. Círculo de apoyo con nombres, no números: Solo yo, Ver, Apoyar, Guardar, Representar.
5. Documentos: confirmar antes de usar los datos y no guardar la foto.

## 9. Pendiente (lo hacemos en la fase 0, no lo inventes)

- **Datos de ejemplo:** el `backend/data/seed.json` actual tiene otros números (Javi cobra 780 € + 290 €). Los vamos a cuadrar con el diseño (980 € al mes, 210 € para sus cosas). Hasta entonces, usa lo que devuelva el backend.
- **Endpoint para leer documentos** (pantallas 5-7): todavía no existe. Lo definimos en el contrato de endpoints. Mientras, usa datos falsos fijos (la multa de 90 €).
- Endpoints que ya existen y sirven: `GET /api/personas/{id}/presupuesto`, `GET .../metas`, `POST .../evaluar_compra`, `POST .../gastos`, `POST .../evaluar_riesgo`, `POST .../pausa`, `GET .../avisos`, `GET .../informe_anual/resumen`, `GET .../informe_anual`. Compruébalos en `backend/app/main.py`.

## 10. Prompt para pegar en Claude Code

```
Lee docs/diseno/integrar-pantallas.md y docs/diseno/guion-demo.md.
Quiero rehacer las pantallas de la demo de Willo en backend/app/static/
(persona.html para Javi, apoyo.html para Ana, willo.css) siguiendo ese documento.

- Construye SOLO las pantallas 1 a 11. Las R1 y R2 son de reserva: NO las hagas.
- Usa exactamente los colores, tamaños y textos del documento. Letra Helvetica.
- No cambies la lógica del backend. Conecta las pantallas a los endpoints que ya
  existen; donde falte uno (leer documentos), usa datos falsos fijos y márcalo con TODO.
- Ve pantalla por pantalla y explícame qué haces en cada paso, en español sencillo,
  porque quiero entenderlo. Después de cada pantalla, dime cómo verla en /demo.
```

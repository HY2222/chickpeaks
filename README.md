# Willo · *your will, your money*

Willo es una app con asistente de voz en **lectura fácil** para que las personas con discapacidad intelectual decidan sobre su propio dinero, con los apoyos que ellas eligen (Ley 8/2021). La asistente se llama **Noa** y funciona con **ElevenLabs**.

- **La persona** pregunta a Noa por voz: «¿Puedo comprarme las zapatillas?». Noa responde: «En tu hucha de mis cosas te quedan 120 €. Si compras las zapatillas, te quedan 40 €. Tú decides.» La IA explica y nunca recomienda. **Las cuentas las hace el código, no el modelo.**
- **Su decisión queda registrada** como constancia de su voluntad, y solo se comparte si ella quiere.
- **Escudo antiestafas** con reglas explicables. Noa avisa y la persona elige si llama a su persona de apoyo. **Nunca bloquea**: Willo avisa, la persona decide.
- **Círculo de apoyo** en 3 niveles (Solo yo, Acompañar y Medida judicial) en vez de «control parental».
- **Persona de apoyo**: registra gastos dictando (ElevenLabs Scribe) y descarga en un clic el **informe anual para el juzgado** en PDF.
- **Perfil de menores** (ejemplo: Lucía, 14 años) con metas de ahorro sobre el mismo motor.

> Demo con datos inventados. No se conecta a ningún banco.

## Probar Willo (jurado)

**Sin instalar nada:** https://willo-sfh4.onrender.com. Tiene la voz de Noa y la lectura de fotos con Claude. Si nadie la ha usado en un rato, la primera vez tarda **hasta 1 minuto** en arrancar; después va normal.

**En tu ordenador** (si la web no responde): mira [Instalación](#instalación-y-ejecución), son 5 comandos. Sin claves funciona todo menos la voz de Noa (se usa una pregunta de ejemplo) y la lectura de fotos con Claude (se usa una multa de ejemplo).

Recorrido de la demo (3 minutos). Abre cada enlace en una pestaña; con la ventana estrecha se ve como un móvil:

| Paso | Enlace | Qué ver |
|---|---|---|
| 1 | `/demo/banco` | La app del banco con Willo dentro |
| 2 | `/demo` → «Hablar con Noa» | Javi pregunta si puede comprar una entrada de 45 €. Noa da las cifras y dice «Tú decides» |
| 3 | `/demo#5` → «Subir desde la galería» | Noa lee un documento. Javi confirma los datos antes de que se usen |
| 4 | `/demo#8` | Posible estafa por Bizum: Willo explica las señales y **no bloquea**. Pulsa «Avisar a Ana» |
| 5 | `/demo/apoyo` | El móvil de Ana: el aviso de estafa y el informe anual para el juzgado en PDF |

Ajustes (icono de engranaje arriba a la derecha del inicio): velocidad de Noa y volver al banco. Se guarda en el móvil de quien lo usa. Solo hay una voz (femenina) para gastar pocos créditos de ElevenLabs; el backend admite una voz masculina con `ELEVENLABS_VOICE_ID_MASCULINA`, pero la app no la ofrece.

Para empezar de cero: `POST /api/demo/reset` en `/docs`. Si varias personas usan la web a la vez, comparten los mismos datos.

## Requisitos

- Python 3.11 o superior (o Docker)
- Opcional: claves de ElevenLabs (voz de Noa) y de Anthropic (leer fotos). Sin ellas la demo funciona con ejemplos.

## Instalación y ejecución

Desde la carpeta del repositorio. En **Windows**:

```bash
copy .env.example .env
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app
```

En **Mac o Linux**:

```bash
cp .env.example .env
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app
```

O con Docker, desde la raíz: `docker compose up --build`

Después abre http://localhost:8000. Las claves (opcionales) van en `.env`, y la fecha de la demo está fijada en `WILLO_HOY=2026-11-08` para que los datos sean los del guion.

- http://localhost:8000/demo · móvil de Javi (huchas, «¿Puedo comprarlo?», botón para hablar con Noa)
- http://localhost:8000/demo/apoyo · móvil de Ana y panel de la curadora (avisos, gasto dictado, informe PDF)
- http://localhost:8000/docs · todas las rutas de la API

### Instalar Willo en el móvil (PWA)

Willo es una **app web instalable (PWA)**: se instala desde el navegador, aparece con su icono y se abre a pantalla completa.

1. El móvil tiene que abrir la app por **https** (en local, con un túnel como ngrok o desplegada en Vercel/Render).
2. Android (Chrome): menú ⋮ → **Instalar aplicación**. iPhone (Safari): botón compartir → **Añadir a pantalla de inicio**.
3. `/demo` se instala como «Willo» (Javi) y `/demo/apoyo` como «Willo Apoyo» (Ana).

Para que la demo empiece siempre igual: `POST /api/demo/reset` antes de presentar.

## Tests

```bash
cd backend && python -m pytest -q
```

## Configurar a Noa en ElevenLabs

1. Crear un agente en ElevenLabs Agents y pegar el prompt de [`agent/noa_prompt.md`](agent/noa_prompt.md).
2. Crear la voz con Voice Design (cálida, clara, ritmo pausado). No clonamos voces reales.
3. Añadir las 4 herramientas webhook de [`agent/tools.json`](agent/tools.json), con la URL pública del backend (en local, con un túnel como ngrok).
4. Poner `ELEVENLABS_API_KEY` y `ELEVENLABS_AGENT_ID` en `.env`. El navegador pide una URL firmada a `/api/voz/signed-url`, así la clave nunca sale del servidor.

## Productos de ElevenLabs que usamos

| Producto | Para qué |
|---|---|
| Agents | Noa: conversación por voz con herramientas e interrupciones |
| Voice Design | La voz de Noa, diseñada para lectura fácil |
| Scribe (speech to text) | Gastos dictados por la persona de apoyo (`/api/gastos/transcribir`) |
| Sound Effects | Sonidos de confirmación de la app (pendiente) |

## Círculo de apoyo

Para la persona solo hay una pregunta: **¿quieres que alguien te acompañe con tu dinero?**

| Nivel | Qué significa | Quién lo da |
|---|---|---|
| Solo yo | Nadie más ve el dinero de la persona. | — |
| Acompañar | La persona de apoyo ve los pagos, y la persona puede llamarla con un toque cuando Noa detecta algo raro. Se puede retirar cuando quiera. | La persona |
| Medida judicial | Solo aparece si hay una sentencia. Hace lo que diga la sentencia y genera el informe de cuentas para el juez. | Resolución judicial |

«Acompañar» junta los antiguos «Ver» y «Apoyar»; «Medida judicial» junta «Guardar» y «Representar». En el código (`support.py`) los niveles siguen siendo N0 a N4: Solo yo = N0, Acompañar = N1-N2 y Medida judicial = N3-N4.

### Cuando Noa ve algo raro

> Noa: «Cuidado. Este pago se parece a un engaño. ¿Quieres hablar con Ana antes de pagar?»
> **[Llamar a Ana]** **[Sigo yo]**

- **Llamar a Ana**: se abre la llamada y Ana ve el pago para poder ayudar.
- **Sigo yo**: Ana no se entera y la persona decide sola. Para que un estafador no la presione, Noa le explica en lectura fácil por qué parece una estafa («Nadie del banco te pide dinero por teléfono») y le propone esperar: «¿Esperamos 10 minutos antes de pagar?». Se lo puede saltar: **el pago nunca se bloquea**.

Willo avisa, la persona decide.

## API principal

| Ruta | Qué hace |
|---|---|
| `GET /api/personas/{id}/presupuesto` | Lo que queda en cada hucha (herramienta de Noa) |
| `POST /api/personas/{id}/evaluar_compra` | ¿Puedo comprarlo? Cifras y texto en lectura fácil |
| `POST /api/personas/{id}/decisiones` | Guarda la decisión y avisa al círculo si ella quiere |
| `POST /api/personas/{id}/evaluar_riesgo` | Escudo antiestafas |
| `GET/PUT /api/personas/{id}/circulo` | Ver o cambiar el círculo de apoyo |
| `GET /api/personas/{id}/avisos` | Avisos recibidos por el círculo |
| `POST /api/personas/{id}/gastos` | Gasto dictado por la persona de apoyo (N3+) |
| `GET /api/personas/{id}/informe_anual?preparado_por=` | PDF para el juzgado (N3+) |
| `GET /api/personas/{id}/metas` | Metas de ahorro (perfil de menores) |
| `POST /api/lectura_facil/comprobar` | Índice Fernández-Huerta y reglas de lectura fácil |

## Estructura

```
agent/            prompt y herramientas de Noa (ElevenLabs)
backend/app/      API FastAPI
  budget.py       cuentas de las huchas (nunca el modelo)
  easyread.py     cifras y comprobador de lectura fácil
  risk.py         escudo antiestafas
  support.py      círculo de apoyo N0-N4
  expenses.py     gastos dictados
  report.py       informe anual en PDF
  static/         pantallas de demo (el frontend definitivo es de P4)
backend/data/     datos inventados de Javi y Lucía
backend/tests/    tests
```

## Principios

- Apoyo, no sustitución: la app nunca decide por la persona. Willo avisa, la persona decide.
- Límites del dinero (`backend/app/limites.py`): ninguna hucha puede quedar en negativo; más de 1.000 € en un día (gastado o recibido) se avisa siempre al círculo de apoyo; más de 1.000.000 € es un error y no se apunta.
- No detectamos emociones por la voz y la voz nunca sirve como firma.
- Pictogramas de [ARASAAC](https://arasaac.org) solo para la demo (licencia no comercial), citando la fuente.

# Willo · *your will, your money*

Willo es una app con asistente de voz en **lectura fácil** para que las personas con discapacidad intelectual decidan sobre su propio dinero, con los apoyos que ellas eligen (Ley 8/2021). La asistente se llama **Noa** y funciona con **ElevenLabs**.

- **La persona** pregunta a Noa por voz o por texto: «¿Puedo comprarme las zapatillas?». Noa responde: «En tu hucha de mis cosas te quedan 120 €. Si compras las zapatillas, te quedan 40 €. Tú decides.» La IA explica y nunca recomienda. **Las cuentas las hace el código, no el modelo.**
- **Su decisión queda registrada** como constancia de su voluntad, y solo se comparte si ella quiere.
- **Escudo antiestafas** con reglas explicables. Avisa al círculo de apoyo (con consentimiento previo) y **nunca bloquea**.
- **Círculo de apoyo** en niveles N0 a N4 en vez de «control parental».
- **Persona de apoyo**: registra gastos dictando (ElevenLabs Scribe) y descarga en un clic el **informe anual para el juzgado** en PDF.
- **Perfil de menores** (ejemplo: Lucía, 14 años) con metas de ahorro sobre el mismo motor.

> Demo con datos inventados. No se conecta a ningún banco.

## Requisitos

- Python 3.11 o superior (o Docker)
- Cuenta de ElevenLabs para la voz (la API y la demo en texto funcionan sin ella)

## Instalación y ejecución

```bash
cp .env.example .env        # rellenad las claves de ElevenLabs si queréis voz
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

O con Docker, desde la raíz: `docker compose up --build`

Después abrid:
- http://localhost:8000/demo · móvil de Javi (huchas, «¿Puedo comprarlo?», botón para hablar con Noa)
- http://localhost:8000/demo/apoyo · móvil de Ana y panel de la curadora (avisos, gasto dictado, informe PDF)
- http://localhost:8000/docs · todas las rutas de la API

### Instalar Willo en el móvil (PWA)

Willo es una **app web instalable (PWA)**: se instala desde el navegador, aparece con su icono y se abre a pantalla completa.

1. El móvil tiene que abrir la app por **https** (en local, con un túnel como ngrok o desplegada en Vercel/Render).
2. Android (Chrome): menú ⋮ → **Instalar aplicación**. iPhone (Safari): botón compartir → **Añadir a pantalla de inicio**.
3. `/demo` se instala como «Willo» (Javi) y `/demo/apoyo` como «Willo Apoyo» (Ana).

Para que la demo empiece siempre igual: `WILLO_HOY=2026-11-08` en `.env` y `POST /api/demo/reset` antes de presentar.

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

| Nivel | Qué permite | Quién lo da |
|---|---|---|
| N0 · Por defecto | Solo la persona usa la app y decide | — |
| N1 · Compartir | Ver las decisiones que ella comparte. Se puede retirar | La persona |
| N2 · Apoyo | Avisos de posible abuso (con consentimiento) y «pausa para pensar» que activa ella. Nunca bloqueo | La persona |
| N3 · Guardador de hecho | Registrar gastos y preparar la rendición de cuentas | La ley |
| N4 · Poder preventivo o curatela | Solo lo que diga el documento | Escritura o resolución judicial |

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

- Apoyo, no sustitución: la app nunca decide ni bloquea.
- No detectamos emociones por la voz y la voz nunca sirve como firma.
- Pictogramas de [ARASAAC](https://arasaac.org) solo para la demo (licencia no comercial), citando la fuente.

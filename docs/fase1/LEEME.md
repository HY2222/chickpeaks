# Willo · Fase 1: cómo seguir en tu ordenador

Fecha: 9 de noviembre de 2026. Este documento sirve para que cualquiera del equipo pueda seguir la fase 1 desde su ordenador sin preguntar a nadie.

**Objetivo de la fase 1:** cada pieza funciona sola. El backend responde, Noa habla, las pantallas se ven, y el medidor de lectura fácil da bien la nota.

---

## 1. Poner el proyecto en marcha (unos 10 minutos)

Necesitas **Git** y **Python 3.11 o superior**.

```bash
git clone https://github.com/HY2222/chickpeaks.git
cd chickpeaks
cp .env.example .env
cd backend
python -m venv .venv
```

Activa el entorno:
- Mac o Linux: `source .venv/bin/activate`
- Windows: `.venv\Scripts\activate`

Instala y arranca:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abre en el navegador:

| Dirección | Qué es |
|---|---|
| http://localhost:8000/demo/banco | Pantalla 0: la app del banco con Willo dentro |
| http://localhost:8000/demo | Móvil de Javi (pantallas 1 a 8) |
| http://localhost:8000/demo/apoyo | Móvil de Ana (pantallas 9 a 11) |
| http://localhost:8000/docs | Todas las rutas de la API, para probarlas a mano |

Para pasar los tests: `pip install pytest httpx` y luego `python -m pytest -q` dentro de `backend`. Ahora mismo pasan los 21.

### El archivo `.env`

Las claves van **solo** en `.env`. Nunca en el chat, en WhatsApp ni en el repo (`.env` ya está en `.gitignore`).

Variables que usamos (los valores os los pasáis en persona):
- `ELEVENLABS_API_KEY` y `ELEVENLABS_AGENT_ID`: para hablar con Noa. Sin ellas, la demo funciona en modo texto.
- `ANTHROPIC_API_KEY`: la clave de Claude de la **fase 1** (no la de la demo). Hace falta para leer documentos y para reescribir en lectura fácil. Todavía no está en `.env.example`: añádela tú.
- `WILLO_HOY=2026-11-08`: para que la demo siempre tenga la misma fecha.
- Opcionales: `WILLO_TOOL_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID_DEMO`.

En desarrollo usad siempre **Claude Haiku**, que es el más barato.

---

## 2. Dónde está cada cosa

| Carpeta o archivo | Qué hay |
|---|---|
| `docs/diseno/contrato-endpoints.md` | **Lo más importante.** Qué pide cada pantalla al backend y qué le devuelve. Es la referencia para todo lo que falta |
| `docs/diseno/datos-ejemplo.md` | Las cifras de la demo (980 € al mes, 210 € para sus cosas) |
| `docs/diseno/guion-demo.md` | El guion de 3 minutos |
| `docs/diseno/pantallas/` | Las imágenes de las pantallas 1 a 11 |
| `backend/app/main.py` | Todas las rutas de la API |
| `backend/app/easyread.py` | Medidor de lectura fácil (Fernández-Huerta) |
| `backend/app/risk.py` | Reglas antiestafa |
| `backend/app/report.py` | Informe anual para el juzgado (PDF) |
| `backend/data/seed.json` | Datos inventados de Javi, Ana y Lucía |
| `backend/app/static/` | Las pantallas (`banco.html`, `persona.html`, `apoyo.html`) y los estilos |
| `agent/` | Instrucciones y herramientas de Noa para ElevenLabs |

---

## 3. Qué está hecho

- **Backend:** presupuesto y huchas, metas de ahorro, "¿puedo comprarlo?" (`evaluar_compra`), guardar decisiones, URL de voz para Noa, informe PDF.
- **Pantallas:** de la 1 a la 11 están hechas, más la pantalla 0 del banco (PR #14).
- **Noa:** ya existe en ElevenLabs y ha tenido conversaciones de prueba.
- **Contrato de la fase 0:** cerrado. Se leen los documentos en dos pasos, con Haiku, y se guarda si Javi envió el Bizum o no.

---

## 4. Qué falta, por persona

### Backend (lo que llevaba Inés)
Todo está descrito con ejemplos en `docs/diseno/contrato-endpoints.md`. En este orden:

1. **`POST /api/personas/javi/documentos/leer`**: recibe una foto, se la manda a Claude Haiku con visión y devuelve los datos del documento en el JSON del contrato. No guarda la imagen. Si no se lee bien, devuelve `422`. Hay que añadir `anthropic` a `backend/requirements.txt`.
2. **`POST /api/personas/javi/documentos/confirmar`**: con los datos ya confirmados por Javi, el **código** (no la IA) hace las cuentas: cuánto le queda si paga, si ya estaba en su plan y si es un ticket ya pagado.
3. Probar la lectura con **5 fotos reales**: una factura, un ticket, una multa, una carta del banco y una foto mala. Si Haiku falla con las buenas, cambiar a Sonnet (es una línea).
4. **`evaluar_riesgo`**: que cree **un solo aviso** para Ana y devuelva su `aviso_id`.
5. **`POST /avisos/{aviso_id}/pedir_hablar`** y **`POST /avisos/{aviso_id}/resultado`**.
6. **`GET /avisos`**: que cada aviso traiga `id`, `estado` y `resultado`, y que se pueda filtrar con `?tipo=posible_estafa`.
7. **`GET /informe_anual/resumen`**: añadir `avisos_estafa`.
8. En `seed.json`, añadir el **teléfono de Javi** (el botón "Llamar" de Ana abre el marcador vacío).

Cuando esté el paso 1, hay que quitar los datos de prueba de las pantallas 5 a 7 (busca `TODO` en `persona.html`).

### Cristina
- **Fallo en el medidor Fernández-Huerta** (`easyread.py`, función `fernandez_huerta`). Ahora usa "frases por cada 100 palabras", pero la fórmula corregida usa "**palabras por frase**". Por eso puntúa al revés: "Tienes 210 euros. Si compras la entrada, te quedan 165 euros. Tú decides." saca 63, y la misma idea en una frase larguísima saca 84. Es cambiar una línea:
  `f = len(_frases(texto)) * 100 / n` → `f = n / len(_frases(texto))`.
  Después, comprobar que las frases de Noa sacan 80 o más y añadir un test que lo compruebe.
- **Reescritura con Claude:** una función que recibe un texto difícil, le pide a Claude que lo pase a lectura fácil y lo vuelve a medir.
- Luego, ajustar las **reglas antiestafa** de `risk.py` con las frases de ejemplo que reúna Anqi.

### Nolan
- Noa ya existe en ElevenLabs. Falta revisar que sus herramientas coinciden con `agent/tools.json` y con el contrato.

### Leo y Raúl
- Las pantallas están hechas. Cuando el backend tenga los endpoints nuevos, conectarlas (pantallas 5 a 8 y 10 a 11).

### Anqi
- Contacto con Plena Inclusión, cifras, frases de ejemplo (de estafa y de lectura fácil) y el contenido del informe para el juzgado.

---

## 5. PR abiertos que hay que revisar y fusionar

- **#13**: logo de Willo como icono de la app.
- **#14**: pantalla 0 (la app del banco con Willo dentro) y este documento.

Aviso: Vercel (`willo-pitch`) marca error en los PR. No es por el código: ese proyecto de Vercel no sabe construir este repo. Se puede ignorar o desconectar.

---

## 6. Siguiente paso

Empezar por **`documentos/leer`**, que es lo que tiene paradas las pantallas 5 a 7. Si usas Claude Code, puedes pegarle esto:

> Lee `docs/diseno/contrato-endpoints.md`, sección "5-7. Noa lee un documento". Añade a `backend/app/main.py` el endpoint `POST /api/personas/{persona_id}/documentos/leer` que recibe una foto (multipart, campo `foto`), la manda a Claude Haiku con visión usando la librería `anthropic` y la clave de `ANTHROPIC_API_KEY`, y devuelve exactamente el JSON del contrato. No guardes la imagen. Si no se puede leer, devuelve 422 con el texto del contrato. Añade un test que no llame a la API de verdad. Explícame cada paso en español sencillo.

Trabaja en una rama nueva, abre un PR y que lo revise otra persona antes de fusionarlo.

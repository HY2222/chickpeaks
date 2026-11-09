# Willo · Qué falta (para seguir en otro ordenador)

Fecha: 9 de noviembre de 2026, 18:00.

**Resumen:** el backend está terminado y probado con fotos reales en Render. Lo que falta es **conectar las pantallas al backend** y pulir detalles. Esto es la fase 2.

---

## 1. Antes de empezar (10 minutos)

```bash
git clone https://github.com/HY2222/chickpeaks.git     # o, si ya lo tienes: git checkout main && git pull
cd chickpeaks
cp .env.example .env
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt pytest httpx
python -m pytest -q              # tienen que pasar los 102
uvicorn app.main:app --reload
```

En el `.env` de la **raíz** del repo, no dentro de `backend`:

```
ANTHROPIC_API_KEY=la-clave-de-la-fase-1
WILLO_HOY=2026-11-08
```

- La clave **solo** va en `.env`. Nunca en un chat ni en el repo.
- Para probar sin instalar nada, la app ya está publicada: https://willo-sfh4.onrender.com (`/demo/banco`, `/demo`, `/demo/apoyo`, `/docs`).
- Render ya tiene `ANTHROPIC_API_KEY` y `WILLO_TELEFONO_JAVI` (el móvil del compañero que hace de Javi). Se actualiza solo cada vez que se fusiona un PR en `main`.

Si usas Claude Code, empieza pegándole esto:

> Somos el equipo de Willo (hackathon BEST UC3M). Willo es una PWA de finanzas por voz en lectura fácil para personas con discapacidad intelectual. La asistente de voz se llama Noa (ElevenLabs) y el backend es FastAPI (carpeta backend/). Las pantallas están en backend/app/static/. Lee docs/fase1/QUE-FALTA.md y docs/diseno/contrato-endpoints.md. Reglas: las cuentas las hace el código, no la IA. Noa explica, nunca recomienda y nunca bloquea. Las claves solo en .env. Habla en español sencillo y trabaja siempre en una rama nueva con PR.

---

## 2. Lo que está hecho

- **Backend completo** (PR #15 a #20, 102 tests): leer documentos con Claude Haiku, hacer las cuentas, avisos de estafa, reglas antiestafa, contactos, teléfono de Javi, cifras con punto de miles ("4.800 €").
- **Probado con fotos reales en Render:** una multa de Madrid, un ticket de Sephora, una factura de luz, dos estafas por WhatsApp ("hazme un bizum" y "hola mamá, he cambiado de número") y una carta falsa de la Seguridad Social. Todo bien con Haiku: no hace falta Sonnet.
- **Pantallas 0 a 11** hechas, pero las de la 5 a la 11 usan datos de prueba.
- **Noa** existe en ElevenLabs.

---

## 3. Lo que falta, por orden de importancia

### 3.1 Conectar las pantallas al backend (Leo y Raúl) · MÁS IMPORTANTE
Sin esto, la demo enseña siempre la misma multa falsa en vez de la foto que hace Javi.

**`backend/app/static/persona.html` (móvil de Javi):**
- [ ] **Pantallas 5-6:** quitar `DOCUMENTO_FALSO` (alrededor de la línea 577) y mandar la foto a `POST /api/personas/javi/documentos/leer` (campo `foto`). Ojo: el `TODO` dice `/leer_documento`, pero la ruta buena es **`/documentos/leer`**. Los campos se llaman como en el contrato: `titulo`, `remitente`, `importe`, `fecha_limite`, `accion`, `sospechoso`, `motivo_sospecha`, `senales`, `pictograma`, `texto_lectura_facil`.
- [ ] Si la respuesta es `422`, enseñar `texto_lectura_facil` ("No he podido leerlo bien. ¿Haces otra foto con más luz?").
- [ ] **Pantalla 7:** cuando Javi pulsa "Sí, es correcto", llamar a `POST /api/personas/javi/documentos/confirmar` con los datos leídos. Si `tipo` es `mensaje`, mandar también `texto_mensaje` y `telefono`.
- [ ] La línea 634 compara con `DOCUMENTO_FALSO.importe`: cambiarla para que use el documento leído.
- [ ] **Pantalla 8:** guardar el `aviso_id` que devuelve `evaluar_riesgo`. "Avisar a Ana" → `POST /avisos/{aviso_id}/pedir_hablar`. "Enviar igualmente" → `POST /avisos/{aviso_id}/resultado` con `{"enviado": true}`. "No enviar" → lo mismo con `{"enviado": false}`.
- [ ] Botón "Elegir contactos" (solo funciona en Chrome para Android):

```js
async function elegirContactos() {
  if (!("contacts" in navigator)) return alert("Tu móvil no deja elegir contactos desde aquí.");
  const elegidos = await navigator.contacts.select(["name", "tel"], {multiple: true});
  const contactos = elegidos.flatMap(c => (c.tel || []).map(tel =>
    ({nombre: c.name?.[0] || "Sin nombre", telefono: tel})));
  return post("contactos", {contactos});
}
```

**`backend/app/static/apoyo.html` (móvil de Ana):**
- [ ] **Pantalla 9:** la caja de estafa tiene que salir cuando el aviso tenga `estado === "javi_pide_hablar"`. Usar `destinatario`, `importe` y `senales` del aviso en vez de leer el texto largo con `leerAvisoEstafa` (línea 138).
- [ ] **Pantalla 10:** usar `avisos_estafa` del resumen (`GET /informe_anual/resumen`) en vez de `pausasDeEstafa()` (línea 219).
- [ ] **Pantalla 11:** usar `GET /api/personas/javi/avisos?tipo=posible_estafa`.

Todo está explicado con ejemplos en `docs/diseno/contrato-endpoints.md`.

### 3.2 Noa en ElevenLabs (Nolan)
- [ ] Comprobar que las herramientas de Noa coinciden con `agent/tools.json` y con el contrato. `evaluar_riesgo` ahora acepta `telefono` y devuelve `aviso_id`.
- [ ] Comprobar que las herramientas apuntan a `https://willo-sfh4.onrender.com`.

### 3.3 Medidor de lectura fácil (Cristina)
- [ ] **Arreglar Fernández-Huerta** en `backend/app/easyread.py`, línea 55. Ahora usa "frases por cada 100 palabras" y tiene que usar "**palabras por frase**". Por eso las frases cortas de Noa sacan unos 65 cuando deberían sacar más de 80. Cambiar:
  `f = len(_frases(texto)) * 100 / n` → `f = n / len(_frases(texto))`
  Comprobado: con el cambio, "Tienes 210 euros. Si compras la entrada, te quedan 165 euros. Tú decides." pasa de 63 a 82.
- [ ] Añadir un test que compruebe que las frases de Noa (`documents.py`) sacan 80 o más.
- [ ] Sacar las cifras para el pitch: la nota de un documento original frente a la de lo que dice Noa (por ejemplo, la carta de la Seguridad Social frente a la frase de Noa).

### 3.4 Decidir en equipo
- [ ] **¿Se avisa a Ana con riesgo medio?** Ahora solo se le avisa con riesgo alto. Con riesgo medio, la pantalla 8 enseña la pausa, pero no hay `aviso_id`, así que el botón "Avisar a Ana" no tiene a qué llamar. Recomendación: no avisar a Ana sola. Que el aviso se cree cuando Javi pulse "Avisar a Ana". Así no le llegan falsas alarmas y decide Javi.

### 3.5 Otras cosas
- [ ] (Opcional) Probar una **foto borrosa**: tiene que dar `422`.
- [ ] (Opcional) Desconectar el proyecto de Vercel `willo-pitch` del repo, porque falla en todos los PR. Lo tiene que hacer HY2222, el dueño.
- [ ] **Ensayar la demo completa** en dos móviles con Render, siguiendo `docs/diseno/guion-demo.md`.
- [ ] Antes de presentar: `POST /api/demo/reset` para que la demo empiece siempre igual.

---

## 4. Reglas que no se pueden romper

- Las cuentas las hace el **código**, no la IA.
- Noa **explica**. Nunca recomienda y nunca bloquea: los botones los pulsa Javi.
- Las claves van **solo** en `.env` y en Render.
- Los números de teléfono reales no van en el repo, porque será público.
- Trabaja siempre en una **rama nueva**, abre un PR y que lo revise otra persona antes de fusionarlo.

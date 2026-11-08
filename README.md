# Willo · Presentación del pitch (React + Tailwind + Motion)

## Arrancar

```bash
cd willo-pitch
npm install        # instala react, motion, vite y tailwind
npm run dev        # abre http://localhost:5173
```

Para el día del pitch: `npm run build` genera `dist/`, que se puede abrir con `npm run preview` o subir a cualquier hosting.

## Controles

| Tecla | Acción |
|---|---|
| → · espacio · Enter | Siguiente diapositiva |
| ← | Diapositiva anterior |
| Inicio / Fin | Primera / última |
| F | Pantalla completa |
| N | Notas del ponente |

También se avanza con un clic (y se retrocede con un clic en el tercio izquierdo). La URL guarda la diapositiva: `#portada`, `#javi`, `#cierre`…

## `<ParticleText />`

`src/components/ParticleText.tsx`. En esta presentación es **una sola capa** que monta `App.tsx` encima de todas las diapositivas (función `particlesFor`), así que los puntos viajan de una diapositiva a otra:

- Diapositiva 1: forman "willo" en grande.
- Al pasar a la 2: se desmontan (la mayoría se dispersan y se desvanecen) y el resto forma el logo arriba a la derecha.
- Diapositivas 2-9: el logo se queda ahí (en crema sobre fondo oscuro).
- Última diapositiva: el logo se deshace y vuelven a formar "willo".

```tsx
<ParticleText text="willo" />                                   // una palabra
<ParticleText text="Willo" src={LOGO_MASCARA} box={{ x: 1768, y: 32, w: 112, h: 112 }} dotScale={0.5} />  // el logo
```

El logo está en `src/logoMascara.ts` (y en `public/logo-willo-mascara.png`): el cuadrado redondeado es opaco y la figura de la W con el punto, transparente, así que los puntos rellenan el cuadrado y la figura queda en negativo.

| Prop | Por defecto | Qué hace |
|---|---|---|
| `text` | — | Palabra que forman las partículas. Si cambia, los puntos viajan a la nueva palabra (morphing). |
| `src` | — | Imagen con transparencia: los puntos forman sus zonas opacas en vez del texto. |
| `box` | — | Rectángulo `{x, y, w, h}` (px del lienzo de 1920 × 1080) donde va la forma. |
| `renderer` | `"auto"` | `"canvas"` fuerza el lienzo; `"auto"` usa SVG hasta 700 puntos. |
| `dotScale` | `1` | Multiplica el tamaño de los puntos (y su respiración). Cambia con transición. |
| `color` | `#3E5A34` | Color de los puntos (verde de acento de Willo). |
| `gap` | `3` | Rejilla de muestreo, en píxeles del canvas de referencia. Cuanto menor, más densas las letras. Sube sola si salen más de `maxPoints`. |
| `dotSize` | `2` | Radio medio; cada punto varía ±20 % (1,6-2,4 px). |
| `duration` | `1.6` | Duración aproximada del stagger en modo SVG (0,002-0,004 s por punto). En canvas, el stagger lo marca el progreso único. |
| `autoplay` | `true` | La palabra se forma sola al entrar. |
| `active` | `true` | Si pasa a `false`, los puntos se vuelven a dispersar. |
| `maxPoints` | `3500` | Límite de puntos. Por encima de 700 se pinta en `<canvas>` ("willo" sale con unos 3.000). |
| `startDelay` | `0.6` | Segundos que los puntos flotan dispersos antes de condensarse. |
| `fitWidth` / `fitHeight` / `centerY` | `0.6` / `0.45` / `0.5` | Tamaño y posición de la palabra dentro del contenedor. |
| `interactive` | `true` | Los puntos a menos de 80 px del ratón se apartan y vuelven con un spring. |

Cómo funciona:

1. Dibuja el texto en un `<canvas>` oculto con Arimo en negrita a 200 px, lee los píxeles con `getImageData` y guarda los puntos de la rejilla con alfa > 128. Escala las coordenadas al contenedor y las recalcula con un `ResizeObserver`.
2. Hasta 700 puntos: un `<svg>` con un `<motion.circle>` por punto. Más de 700: `<canvas>`, con un único progreso 0→1 animado por Motion y cada punto interpolado en `requestAnimationFrame`.
3. Secuencia: los puntos flotan dispersos con una deriva lenta; luego cada uno viaja a su letra con un spring (stiffness 60, damping 14, mass aleatoria 0,8-1,2), escalonado desde el centro; ya formada, la palabra "respira" 1-2 px.
4. Con "reducir movimiento" activado en el sistema, la palabra aparece ya formada y no hay animaciones (`MotionConfig reducedMotion="user"`).

## Otras animaciones (`src/components/Anim.tsx`)

- **Títulos** (`<Words>`): palabra a palabra, de 20 px a 0 y de opacidad 0 a 1, 0,06 s entre palabras, easeOut.
- **Cifras clave** (`<Count>`): `useMotionValue` + `animate()`, de 0 a su valor en 1,5 s con easeOut y puntos de miles.
- **Gráficos** (`<BarH>`, `<BarV>`, `<DrawArrow>`): se dibujan con `pathLength` 0 → 1. El dato importante en el acento; el resto en gris.
- **Transición entre diapositivas**: desplazamiento lateral de 40 px + fade, 0,4 s. La marca "Willo" del pie lleva `layoutId`.
- **Demo** (`<MockupIn>`): el móvil entra con un spring suave y escala de 0,96 a 1.
- Todo dura menos de 1,5 s, solo anima transform y opacity (los gráficos, `pathLength`) y se repite al volver a la diapositiva.
- Con "reducir movimiento" en el sistema, nada se desplaza y las partículas aparecen ya formadas.

## Estructura

```
src/
  App.tsx                    navegación, escala 1920×1080, transiciones, notas
  slides.tsx                 las 10 diapositivas y sus notas
  components/ParticleText.tsx
  components/Anim.tsx        Rise, Fade, Emphasis, MockupIn, Words, Count, BarH, BarV, DrawArrow
  index.css                  Tailwind v4 + paleta de Willo
public/screens/              pantallas de la app (Figma)
```

## Pendiente de rellenar

- Nombres del equipo y enlace a la demo (diapositiva de cierre).
- Enlace al vídeo de respaldo (notas de la diapositiva 5).
- Estado de la validación con Plena inclusión (notas de la diapositiva 9).

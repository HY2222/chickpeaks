import { useCallback, useEffect, useRef, useState } from "react";
import { animate, motion, motionValue, useReducedMotion } from "motion/react";
import type { MotionValue } from "motion/react";

/**
 * <ParticleText text="WILLO" />
 *
 * Partículas que se condensan para formar una palabra.
 * 1. Los puntos de las letras salen de dibujar el texto en un <canvas> oculto y leer sus píxeles.
 * 2. Al principio flotan dispersos por todo el contenedor.
 * 3. Al activarse, cada punto viaja a su letra con un spring (stagger desde el centro).
 * 4. Ya formada, la palabra "respira". El ratón aparta los puntos cercanos.
 * 5. Si cambia `text`, los puntos viajan de una palabra a otra (morphing).
 *
 * Con `src` (una imagen con transparencia) los puntos forman la imagen en vez de un texto,
 * y con `box` se colocan en un rectángulo concreto del contenedor (p. ej. un logo en una esquina).
 *
 * Hasta 700 puntos: SVG con un <motion.circle> por punto.
 * Más de 700: <canvas>; Motion anima un único progreso 0→1 y cada punto se interpola en requestAnimationFrame.
 */
export type Box = { x: number; y: number; w: number; h: number };

export type ParticleTextProps = {
  /** Palabra que forman los puntos (y texto accesible). */
  text: string;
  /** Imagen con transparencia: si se indica, los puntos forman sus zonas opacas en lugar del texto. */
  src?: string;
  /** Rectángulo del contenedor donde va la forma (en px). Sin él, se centra con fitWidth/fitHeight/centerY. */
  box?: Box;
  /** "canvas" fuerza el lienzo; "auto" usa SVG hasta 700 puntos. */
  renderer?: "auto" | "svg" | "canvas";
  /** Multiplica el tamaño de los puntos (anima al cambiar). Útil para formas pequeñas como un logo. */
  dotScale?: number;
  /** Color de los puntos. Por defecto, el verde de acento de Willo. */
  color?: string;
  /** Rejilla de muestreo en píxeles del canvas de referencia (fuente a 200 px). Sube sola si salen demasiados puntos. */
  gap?: number;
  /** Radio medio de cada punto en px (cada punto varía ±20 %). */
  dotSize?: number;
  /** Duración aproximada del stagger completo, en segundos (0,002-0,004 s por punto). */
  duration?: number;
  /** Si es true, la palabra se forma sola cuando `active` es true. */
  autoplay?: boolean;
  /** La diapositiva está en pantalla. Si pasa a false, los puntos vuelven a dispersarse. */
  active?: boolean;
  /** Límite de puntos. Más puntos = letras más densas. Por encima de 700 se pinta en <canvas>. */
  maxPoints?: number;
  /** Retraso antes de empezar a formar la palabra, en segundos. */
  startDelay?: number;
  fontFamily?: string;
  fontWeight?: number;
  /** Ancho máximo de la palabra respecto al contenedor (0-1). */
  fitWidth?: number;
  /** Alto máximo de la palabra respecto al contenedor (0-1). */
  fitHeight?: number;
  /** Centro vertical de la palabra respecto al contenedor (0-1). */
  centerY?: number;
  /** Los puntos se apartan al pasar el ratón. */
  interactive?: boolean;
  className?: string;
};

type Pt = { x: number; y: number };

type Particle = {
  id: number;
  /** Posición base (la que mueven los springs). */
  bx: MotionValue<number>;
  by: MotionValue<number>;
  /** Desplazamiento por el ratón. */
  rx: MotionValue<number>;
  ry: MotionValue<number>;
  /** Posición final pintada = base + ratón + ruido. */
  cx: MotionValue<number>;
  cy: MotionValue<number>;
  op: MotionValue<number>;
  r: number;
  baseOpacity: number;
  mass: number;
  ph: [number, number, number, number];
  fd: [number, number];
  fb: number;
  target: Pt | null;
  dying: boolean;
  repelled: boolean;
  pushX: number;
  pushY: number;
  // Solo modo canvas: origen y orden dentro del stagger.
  sx: number;
  sy: number;
  rank: number;
};

const SVG_LIMIT = 700;
const REF_FONT = 200;
const REPEL_RADIUS = 80;
const TAU = Math.PI * 2;

const rand = (a: number, b: number) => a + Math.random() * (b - a);
const clamp = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v));
const sortXY = (a: Pt, b: Pt) => a.x - b.x || a.y - b.y;
const dist = (a: Pt, b: Pt) => Math.hypot(a.x - b.x, a.y - b.y);

let nextId = 0;

function makeParticle(x: number, y: number, dotSize: number): Particle {
  return {
    id: nextId++,
    bx: motionValue(x),
    by: motionValue(y),
    rx: motionValue(0),
    ry: motionValue(0),
    cx: motionValue(x),
    cy: motionValue(y),
    op: motionValue(0),
    r: dotSize * rand(0.8, 1.2),
    baseOpacity: rand(0.7, 1),
    mass: rand(0.8, 1.2),
    ph: [rand(0, TAU), rand(0, TAU), rand(0, TAU), rand(0, TAU)],
    fd: [rand(0.15, 0.35) * TAU, rand(0.08, 0.2) * TAU],
    fb: rand(0.9, 1.6),
    target: null,
    dying: false,
    repelled: false,
    pushX: 0,
    pushY: 0,
    sx: x,
    sy: y,
    rank: 0,
  };
}

function scatterPoint(w: number, h: number): Pt {
  return { x: rand(w * 0.03, w * 0.97), y: rand(h * 0.04, h * 0.96) };
}

/** Dibuja una imagen en un canvas oculto, a su tamaño final, y devuelve los puntos opacos. */
function sampleImage(
  img: HTMLImageElement,
  w: number,
  h: number,
  o: { gap: number; maxPoints: number; box?: Box; fitWidth: number; fitHeight: number; centerY: number },
): Pt[] {
  const aspect = img.naturalWidth / img.naturalHeight || 1;
  let r = o.box;
  if (!r) {
    const bw = Math.min(w * o.fitWidth, h * o.fitHeight * aspect);
    const bh = bw / aspect;
    r = { x: (w - bw) / 2, y: h * o.centerY - bh / 2, w: bw, h: bh };
  }
  const cw = Math.max(1, Math.round(r.w));
  const ch = Math.max(1, Math.round(r.h));
  const canvas = document.createElement("canvas");
  canvas.width = cw;
  canvas.height = ch;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (!ctx) return [];
  ctx.drawImage(img, 0, 0, cw, ch);
  let data: Uint8ClampedArray;
  try {
    data = ctx.getImageData(0, 0, cw, ch).data;
  } catch {
    return []; // imagen de otro origen sin CORS
  }
  let g = Math.max(2, Math.round(o.gap));
  let pts: Pt[] = [];
  for (let tries = 0; tries < 60; tries++) {
    pts = [];
    const off = Math.floor(g / 2);
    for (let y = off; y < ch; y += g) {
      for (let x = off; x < cw; x += g) {
        if (data[(y * cw + x) * 4 + 3] > 128) pts.push({ x: r.x + x, y: r.y + y });
      }
    }
    if (pts.length <= o.maxPoints) break;
    g += 1;
  }
  return pts;
}

/** Dibuja el texto en un canvas oculto y devuelve los puntos opacos, ya escalados al contenedor. */
function sampleText(
  text: string,
  w: number,
  h: number,
  o: { gap: number; maxPoints: number; fontFamily: string; fontWeight: number; fitWidth: number; fitHeight: number; centerY: number },
): Pt[] {
  if (!text.trim()) return [];
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (!ctx) return [];
  const font = `${o.fontWeight} ${REF_FONT}px ${o.fontFamily}`;
  ctx.font = font;
  const m = ctx.measureText(text);
  const left = m.actualBoundingBoxLeft || 0;
  const tw = Math.ceil(left + (m.actualBoundingBoxRight || m.width));
  const asc = m.actualBoundingBoxAscent || REF_FONT * 0.75;
  const th = Math.ceil(asc + (m.actualBoundingBoxDescent || 0));
  const pad = 4;
  canvas.width = tw + pad * 2;
  canvas.height = th + pad * 2;
  ctx.font = font; // cambiar el tamaño del canvas reinicia el contexto
  ctx.fillStyle = "#000";
  ctx.textBaseline = "alphabetic";
  ctx.fillText(text, pad + left, pad + asc);
  const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);

  // Escala del canvas de referencia al tamaño real del contenedor.
  const s = Math.min((w * o.fitWidth) / canvas.width, (h * o.fitHeight) / canvas.height);
  const ox = (w - canvas.width * s) / 2;
  const oy = h * o.centerY - (canvas.height * s) / 2;

  // Rejilla cada `gap` píxeles; si salen demasiados puntos, la rejilla se abre sola.
  let g = Math.max(2, Math.round(o.gap));
  let pts: Pt[] = [];
  for (let tries = 0; tries < 60; tries++) {
    pts = [];
    const off = Math.floor(g / 2);
    for (let y = off; y < canvas.height; y += g) {
      for (let x = off; x < canvas.width; x += g) {
        if (data[(y * canvas.width + x) * 4 + 3] > 128) pts.push({ x: ox + x * s, y: oy + y * s });
      }
    }
    if (pts.length <= o.maxPoints) break;
    g += 1;
  }
  return pts;
}

export default function ParticleText({
  text,
  src,
  box,
  renderer = "auto",
  dotScale: dotScaleProp = 1,
  color = "#3E5A34",
  gap = 3,
  dotSize = 2,
  duration = 1.6,
  autoplay = true,
  active = true,
  maxPoints = 3500,
  startDelay = 0.6,
  fontFamily = "Arimo, Helvetica, Arial, sans-serif",
  fontWeight = 700,
  fitWidth = 0.6,
  fitHeight = 0.45,
  centerY = 0.5,
  interactive = true,
  className = "",
}: ParticleTextProps) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particles = useRef<Particle[]>([]);
  const calm = useRef(motionValue(0)).current; // 0 = flotando disperso · 1 = palabra formada
  const progress = useRef(motionValue(0)).current; // progreso único del modo canvas
  const formed = useRef(false);
  const lastShape = useRef<string | null>(null);
  const wantFormed = useRef(false);
  const spreadRef = useRef(0.35); // cuánto se escalona la llegada en modo canvas (0-1)
  const chorTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => {
    if (chorTimer.current) clearTimeout(chorTimer.current);
  }, []);
  const colorMV = useRef(motionValue(color)).current;
  const scaleMV = useRef(motionValue(dotScaleProp)).current;
  const [img, setImg] = useState<HTMLImageElement | null>(null);
  const boxKey = box ? `${box.x},${box.y},${box.w},${box.h}` : "";
  const center = useRef<Pt>({ x: 0, y: 0 });
  const sizeRef = useRef({ w: 0, h: 0 });
  const modeRef = useRef<"svg" | "canvas">("svg");
  const [mode, setMode] = useState<"svg" | "canvas">("svg");
  const [size, setSize] = useState({ w: 0, h: 0 });
  const [fontKey, setFontKey] = useState(0);
  const [, setVersion] = useState(0);
  const reduced = useReducedMotion();

  // Tamaño real del contenedor (sin contar transformaciones de escala).
  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      const w = Math.round(entry.contentRect.width);
      const h = Math.round(entry.contentRect.height);
      setSize((s) => (s.w === w && s.h === h ? s : { w, h }));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Color y tamaño de punto cambian con una transición suave.
  useEffect(() => {
    const c = animate(colorMV, color, { duration: 0.6, ease: "easeOut" });
    return () => c.stop();
  }, [color, colorMV]);
  useEffect(() => {
    // Si los puntos encogen (palabra → logo), esperan a llegar antes de hacerse pequeños.
    const shrinking = dotScaleProp < scaleMV.get();
    const c = animate(scaleMV, dotScaleProp, { duration: 0.8, ease: "easeOut", delay: shrinking ? 1.2 : 0 });
    return () => c.stop();
  }, [dotScaleProp, scaleMV]);

  // Carga la imagen (si la forma es una imagen).
  useEffect(() => {
    if (!src) return; // se conserva la última imagen cargada, por si se vuelve a ella
    let alive = true;
    const im = new Image();
    im.onload = () => alive && setImg(im);
    im.src = src;
    return () => {
      alive = false;
    };
  }, [src]);

  // Espera a la fuente de la presentación antes de muestrear las letras.
  useEffect(() => {
    let alive = true;
    const font = `${fontWeight} ${REF_FONT}px ${fontFamily}`;
    const fallback = setTimeout(() => alive && setFontKey((k) => k || 1), 1200);
    const fonts = (document as Document & { fonts?: FontFaceSet }).fonts;
    if (fonts) {
      fonts
        .load(font)
        .then((loaded) => alive && setFontKey((k) => (loaded.length ? k + 1 : k || 1)))
        .catch(() => alive && setFontKey((k) => k || 1));
    } else {
      setFontKey(1);
    }
    return () => {
      alive = false;
      clearTimeout(fallback);
    };
  }, [fontFamily, fontWeight]);

  /** Lleva cada punto a su letra. stagger=true: escalonado desde el centro. */
  const form = useCallback(
    (stagger: boolean, spread = 0.35, spring = { stiffness: 60, damping: 14 }) => {
      const list = particles.current.filter((p) => !p.dying && p.target);
      if (!list.length) return;
      formed.current = true;
      const c = center.current;
      const order = [...list].sort((a, b) => dist(a.target!, c) - dist(b.target!, c));
      const per = stagger ? clamp(duration / order.length, 0.002, 0.004) : 0;

      if (modeRef.current === "canvas") {
        order.forEach((p, i) => {
          p.bx.stop(); // por si venía de moverse libre (la separación de la palabra)
          p.by.stop();
          p.sx = p.bx.get();
          p.sy = p.by.get();
          p.rank = stagger ? clamp((i / Math.max(1, order.length - 1)) * 0.9 + rand(0, 0.1), 0, 1) : 0;
          animate(p.op, p.baseOpacity, { duration: 0.6 });
        });
        spreadRef.current = spread;
        progress.stop();
        progress.set(0);
        animate(progress, 1, { type: "spring", ...spring });
      } else {
        order.forEach((p, i) => {
          const delay = i * per;
          const spring = { type: "spring" as const, stiffness: 60, damping: 14, mass: p.mass, delay };
          animate(p.bx, p.target!.x, spring);
          animate(p.by, p.target!.y, spring);
          if (p.op.get() < p.baseOpacity) animate(p.op, p.baseOpacity, { duration: 0.6, delay });
        });
      }
      animate(calm, 1, { duration: clamp(order.length * per + 0.4, 0.6, 1.5), ease: "easeInOut" });
    },
    [calm, progress, duration],
  );

  /** Vuelve a dispersar los puntos (al salir de la diapositiva). */
  const scatter = useCallback(() => {
    formed.current = false;
    wantFormed.current = false;
    calm.stop();
    calm.set(0);
    progress.stop();
    progress.set(0);
    const { w, h } = sizeRef.current;
    for (const p of particles.current) {
      p.bx.stop();
      p.by.stop();
      const s = scatterPoint(w, h);
      p.bx.set(s.x);
      p.by.set(s.y);
      p.sx = s.x;
      p.sy = s.y;
    }
  }, [calm, progress]);

  // Muestrea el texto y empareja puntos viejos con destinos nuevos (resize y morphing).
  useEffect(() => {
    if (!size.w || !size.h || !fontKey) return;
    if (src && (!img || img.src !== new URL(src, document.baseURI).href)) return; // espera a que cargue la imagen
    sizeRef.current = size;
    const prevCenter = { ...center.current };

    // ¿Ha cambiado la forma (otra palabra, o de palabra a imagen)? Entonces es un morphing con stagger.
    const shape = src ? `img:${src}:${boxKey}` : `txt:${text}`;
    const prevShape = lastShape.current;
    const shapeChanged = prevShape !== null && prevShape !== shape;
    if (chorTimer.current) {
      if (!shapeChanged) return; // la coreografía palabra → logo sigue en marcha: no la interrumpas
      clearTimeout(chorTimer.current); // se ha cambiado de diapositiva a mitad: manda la nueva forma
      chorTimer.current = null;
    }
    const kindChanged = shapeChanged && prevShape!.slice(0, 4) !== shape.slice(0, 4);
    lastShape.current = shape;
    // De la palabra al logo (diapositiva 1 → 2): coreografía en dos tiempos, separarse y formarse.
    const wordToLogo = kindChanged && shape.startsWith("img:") && formed.current && !reduced;

    const targets = (
      src && img
        ? sampleImage(img, size.w, size.h, { gap, maxPoints, box, fitWidth, fitHeight, centerY })
        : sampleText(text, size.w, size.h, { gap, maxPoints, fontFamily, fontWeight, fitWidth, fitHeight, centerY })
    ).sort(sortXY);
    if (targets.length) {
      center.current = {
        x: targets.reduce((a, p) => a + p.x, 0) / targets.length,
        y: targets.reduce((a, p) => a + p.y, 0) / targets.length,
      };
    }

    const alive = particles.current.filter((p) => !p.dying);
    const pos = (p: Particle): Pt => p.target ?? { x: p.bx.get(), y: p.by.get() };
    alive.sort((a, b) => sortXY(pos(a), pos(b)));
    const firstTime = alive.length === 0;

    const next: Particle[] = targets.map((t, i) => {
      let p = alive[i];
      if (!p) {
        // Puntos que faltan: nacen en una posición aleatoria.
        const s = scatterPoint(size.w, size.h);
        p = makeParticle(s.x, s.y, dotSize);
        animate(p.op, p.baseOpacity, { duration: 0.8, delay: firstTime ? rand(0, 0.5) : 0 });
      }
      p.target = t;
      return p;
    });

    // Puntos que sobran: se dispersan, se desvanecen y desaparecen.
    const dying = alive.slice(targets.length);
    // Separación: cada punto sale despedido en la dirección opuesta al centro de la palabra.
    const burst = (p: Particle, extra = 0) => {
      const x = p.bx.get();
      const y = p.by.get();
      const ang = Math.atan2(y - prevCenter.y, x - prevCenter.x) + rand(-0.5, 0.5);
      const d = rand(140, 420) + extra;
      const t = { duration: 0.75, ease: [0.16, 1, 0.3, 1] as [number, number, number, number], delay: rand(0, 0.12) };
      animate(p.bx, x + Math.cos(ang) * d, t);
      animate(p.by, y + Math.sin(ang) * d, t);
    };
    for (const p of dying) {
      p.dying = true;
      p.target = null;
      let fade;
      if (wordToLogo) {
        burst(p, 220);
        fade = animate(p.op, 0, { duration: 1.0, delay: 0.55, ease: "easeIn" });
      } else {
        const s = scatterPoint(size.w, size.h);
        animate(p.bx, s.x, { type: "spring", stiffness: 40, damping: 12, mass: p.mass });
        animate(p.by, s.y, { type: "spring", stiffness: 40, damping: 12, mass: p.mass });
        fade = animate(p.op, 0, { duration: 0.9, ease: "easeOut" });
      }
      fade.then(() => {
        particles.current = particles.current.filter((q) => q !== p);
        if (modeRef.current === "svg") setVersion((v) => v + 1);
      });
    }

    particles.current = [...next, ...dying];
    modeRef.current = renderer === "auto" ? (particles.current.length > SVG_LIMIT ? "canvas" : "svg") : renderer;
    setMode(modeRef.current);
    setVersion((v) => v + 1);

    if (reduced) {
      // Movimiento reducido: la palabra aparece ya formada, sin viajes ni ruido.
      formed.current = true;
      calm.set(1);
      progress.set(1);
      for (const p of next) {
        p.bx.set(p.target!.x);
        p.by.set(p.target!.y);
        p.op.set(p.baseOpacity);
        p.rank = 0;
      }
      return;
    }
    if (wordToLogo) {
      // 1) Separarse: todos los puntos de la palabra salen despedidos hacia fuera (≈0,75 s).
      // 2) Formarse: a los 0,65 s, los que se quedan viajan en cascada a su sitio en el logo.
      formed.current = false; // durante la separación los puntos se mueven libres
      for (const p of next) burst(p);
      chorTimer.current = setTimeout(() => {
        chorTimer.current = null;
        wantFormed.current = true;
        form(true, 0.55, { stiffness: 30, damping: 11 }); // viaje más lento y en cascada, para que se vea
      }, 650);
      return;
    }
    if (kindChanged && formed.current) {
      // De logo a palabra (o al revés): un pequeño "estallido" para que la forma se desmonte antes de viajar.
      for (const p of next) {
        const kick = { duration: 0.8, ease: "easeOut" as const };
        animate(p.rx, [0, rand(-40, 40), 0], kick);
        animate(p.ry, [0, rand(-40, 40), 0], kick);
      }
    }
    if (formed.current || wantFormed.current) form(shapeChanged || !formed.current); // en un resize, sin stagger
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [size, text, src, img, boxKey, fontKey, gap, maxPoints, fontFamily, fontWeight, fitWidth, fitHeight, centerY, dotSize, renderer, reduced, form, calm, progress]);

  // Al entrar en la diapositiva: forma la palabra. Al salir: dispersa.
  const ready = size.w > 0 && fontKey > 0;
  useEffect(() => {
    if (!ready || reduced) return;
    if (active && autoplay) {
      const t = setTimeout(() => {
        wantFormed.current = true;
        form(true);
      }, startDelay * 1000);
      return () => clearTimeout(t);
    }
    scatter();
  }, [active, autoplay, ready, reduced, startDelay, form, scatter]);

  // Canvas con la densidad de píxeles de la pantalla.
  useEffect(() => {
    const c = canvasRef.current;
    if (mode !== "canvas" || !c || !size.w) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    c.width = size.w * dpr;
    c.height = size.h * dpr;
    c.getContext("2d")?.setTransform(dpr, 0, 0, dpr, 0, 0);
  }, [mode, size]);

  // Bucle de animación: deriva cuando está disperso, respiración cuando está formado.
  // Solo corre con la diapositiva en pantalla (y el navegador lo pausa si la pestaña está oculta).
  useEffect(() => {
    if (!active) return;
    let raf = 0;
    const tick = (now: number) => {
      const t = now / 1000;
      const k = calm.get();
      const isCanvas = modeRef.current === "canvas";
      const pr = progress.get();
      const spread = spreadRef.current;
      const ctx = isCanvas ? canvasRef.current?.getContext("2d") : null;
      if (ctx) {
        const { w, h } = sizeRef.current;
        ctx.clearRect(0, 0, w, h);
        ctx.fillStyle = colorMV.get();
      }
      for (const p of particles.current) {
        if (isCanvas && formed.current && p.target && !p.dying) {
          // Cada punto arranca un poco más tarde según su distancia al centro (rank) y llega a 1 a la vez.
          const local = clamp((Math.min(pr, 1) - p.rank * spread) / (1 - spread), 0, 1) + Math.max(0, pr - 1);
          p.bx.set(p.sx + (p.target.x - p.sx) * local);
          p.by.set(p.sy + (p.target.y - p.sy) * local);
        }
        let nx = 0;
        let ny = 0;
        if (!reduced) {
          // Deriva lenta tipo ruido (pocos píxeles) mientras está disperso…
          const drift = 1 - k;
          if (drift > 0.001) {
            nx += drift * 5 * (0.7 * Math.sin(t * p.fd[0] + p.ph[0]) + 0.3 * Math.sin(t * p.fd[1] + p.ph[1]));
            ny += drift * 5 * (0.7 * Math.sin(t * p.fd[1] * 1.3 + p.ph[2]) + 0.3 * Math.sin(t * p.fd[0] * 0.8 + p.ph[3]));
          }
          // …y respiración de 1-2 px, con fases distintas, cuando está formada.
          if (k > 0.001) {
            const amp = 1.3 * Math.min(1, scaleMV.get()); // en formas pequeñas (logo) respira menos
            nx += k * amp * Math.sin(t * p.fb + p.ph[0]);
            ny += k * amp * Math.cos(t * p.fb * 0.9 + p.ph[2]);
          }
        }
        const x = p.bx.get() + p.rx.get() + nx;
        const y = p.by.get() + p.ry.get() + ny;
        if (ctx) {
          ctx.globalAlpha = p.op.get();
          ctx.beginPath();
          ctx.arc(x, y, p.r * scaleMV.get(), 0, TAU);
          ctx.fill();
        } else {
          p.cx.set(x);
          p.cy.set(y);
        }
      }
      if (ctx) ctx.globalAlpha = 1;
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [calm, progress, colorMV, scaleMV, reduced, active]);

  // Interacción: los puntos a menos de 80 px del ratón se apartan y vuelven con un spring.
  const release = (p: Particle) => {
    p.repelled = false;
    p.pushX = 0;
    p.pushY = 0;
    const back = { type: "spring" as const, stiffness: 80, damping: 9, mass: p.mass };
    animate(p.rx, 0, back);
    animate(p.ry, 0, back);
  };

  const onPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!interactive || reduced || !wrapRef.current) return;
    const rect = wrapRef.current.getBoundingClientRect();
    const { w, h } = sizeRef.current;
    const mx = ((e.clientX - rect.left) * w) / rect.width;
    const my = ((e.clientY - rect.top) * h) / rect.height;
    for (const p of particles.current) {
      if (p.dying) continue;
      const dx = p.bx.get() - mx;
      const dy = p.by.get() - my;
      const d = Math.hypot(dx, dy);
      if (d < REPEL_RADIUS) {
        const f = 1 - d / REPEL_RADIUS;
        const push = 8 + 36 * f * f;
        const ux = d > 0.5 ? dx / d : rand(-1, 1);
        const uy = d > 0.5 ? dy / d : rand(-1, 1);
        const tx = ux * push;
        const ty = uy * push;
        if (!p.repelled || Math.abs(tx - p.pushX) + Math.abs(ty - p.pushY) > 4) {
          p.repelled = true;
          p.pushX = tx;
          p.pushY = ty;
          const out = { type: "spring" as const, stiffness: 260, damping: 20 };
          animate(p.rx, tx, out);
          animate(p.ry, ty, out);
        }
      } else if (p.repelled) {
        release(p);
      }
    }
  };

  const onPointerLeave = () => {
    for (const p of particles.current) if (p.repelled) release(p);
  };

  return (
    <div
      ref={wrapRef}
      className={`absolute inset-0 ${className}`}
      onPointerMove={onPointerMove}
      onPointerLeave={onPointerLeave}
      role="img"
      aria-label={text}
    >
      {mode === "svg" ? (
        <svg width={size.w} height={size.h} className="absolute inset-0 overflow-visible" aria-hidden="true">
          {particles.current.map((p) => (
            <motion.circle key={p.id} cx={p.cx} cy={p.cy} r={p.r} fill={color} style={{ opacity: p.op }} />
          ))}
        </svg>
      ) : (
        <canvas ref={canvasRef} className="absolute inset-0" style={{ width: size.w, height: size.h }} aria-hidden="true" />
      )}
    </div>
  );
}

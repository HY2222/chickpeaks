import { useCallback, useEffect, useState } from "react";
import { AnimatePresence, LayoutGroup, MotionConfig, motion } from "motion/react";
import { slides } from "./slides";
import ParticleText from "./components/ParticleText";
import type { ParticleTextProps } from "./components/ParticleText";
import { LOGO_MASCARA } from "./logoMascara";

const W = 1920;
const H = 1080;

/*
 * Capa de partículas que acompaña toda la presentación:
 * - diapositiva 1: forman "willo" en grande;
 * - diapositivas 2-9: se desmontan y forman el logo arriba a la derecha;
 * - última diapositiva: vuelven a formar "willo".
 */
const ACENTO = "#3E5A34";
const CREMA = "#F5F7F0";
const LOGO_BOX = { x: 1768, y: 32, w: 112, h: 112 };

function particlesFor(index: number): Omit<ParticleTextProps, "active"> {
  const last = slides.length - 1;
  if (index === 0) {
    return { text: "willo", color: ACENTO, fitWidth: 0.5, fitHeight: 0.38, centerY: 0.42, dotScale: 1, interactive: true };
  }
  if (index === last) {
    return { text: "willo", color: CREMA, fitWidth: 0.46, fitHeight: 0.34, centerY: 0.36, dotScale: 1, interactive: true };
  }
  return { text: "Willo", src: LOGO_MASCARA, box: LOGO_BOX, color: slides[index].dark ? CREMA : ACENTO, dotScale: 0.5, interactive: false };
}

const indexFromHash = () => {
  const i = slides.findIndex((s) => `#${s.id}` === window.location.hash);
  return i >= 0 ? i : 0;
};

// Transición entre diapositivas: desplazamiento lateral corto + fade, 0,4 s.
// Sin mode="wait": la saliente y la entrante conviven 0,4 s, y así los elementos con
// el mismo layoutId (la marca del pie) viajan de una diapositiva a la otra.
const variants = {
  enter: (dir: number) => ({ opacity: 0, x: dir * 40 }),
  center: { opacity: 1, x: 0 },
  exit: (dir: number) => ({ opacity: 0, x: dir * -40 }),
};
const slideTransition = { duration: 0.4, ease: "easeOut" } as const;

export default function App() {
  const [[index, dir], setState] = useState<[number, number]>(() => [indexFromHash(), 1]);
  const [scale, setScale] = useState(1);
  const [showNotes, setShowNotes] = useState(false);
  const [showHint, setShowHint] = useState(true);

  const go = useCallback((to: number) => {
    setState(([cur]) => {
      const next = Math.max(0, Math.min(slides.length - 1, to));
      return next === cur ? [cur, 1] : [next, next > cur ? 1 : -1];
    });
  }, []);

  // Escala el lienzo de 1920 × 1080 a la ventana.
  useEffect(() => {
    const fit = () => {
      const w = window.innerWidth || document.documentElement.clientWidth;
      const h = window.innerHeight || document.documentElement.clientHeight;
      if (w > 0 && h > 0) setScale(Math.min(w / W, h / H));
    };
    fit();
    window.addEventListener("resize", fit);
    // Por si la página se abre dentro de un marco que aún no tiene tamaño.
    const ro = new ResizeObserver(fit);
    ro.observe(document.documentElement);
    return () => {
      window.removeEventListener("resize", fit);
      ro.disconnect();
    };
  }, []);

  // Navegación con teclado.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (["ArrowRight", "ArrowDown", "PageDown", " ", "Enter"].includes(e.key)) {
        e.preventDefault();
        go(index + 1);
      } else if (["ArrowLeft", "ArrowUp", "PageUp", "Backspace"].includes(e.key)) {
        e.preventDefault();
        go(index - 1);
      } else if (e.key === "Home") go(0);
      else if (e.key === "End") go(slides.length - 1);
      else if (e.key === "f" || e.key === "F") {
        if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
        else document.documentElement.requestFullscreen?.().catch(() => {});
      } else if (e.key === "n" || e.key === "N") setShowNotes((v) => !v);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [index, go]);

  // La URL recuerda la diapositiva (#portada, #javi…).
  useEffect(() => {
    const id = `#${slides[index].id}`;
    if (window.location.hash !== id) {
      try {
        history.replaceState(null, "", id);
      } catch {
        // En algunos marcos aislados no se puede tocar el historial; la presentación sigue igual.
      }
    }
  }, [index]);
  useEffect(() => {
    const onHash = () => go(indexFromHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, [go]);

  useEffect(() => {
    const t = setTimeout(() => setShowHint(false), 3500);
    return () => clearTimeout(t);
  }, []);

  const slide = slides[index];

  return (
    <MotionConfig reducedMotion="user">
      <div
        className="fixed inset-0 overflow-hidden bg-texto"
        onClick={(e) => go(e.clientX < window.innerWidth / 3 ? index - 1 : index + 1)}
      >
        <div
          className="absolute left-1/2 top-1/2 overflow-hidden"
          style={{ width: W, height: H, transform: `translate(-50%, -50%) scale(${scale})` }}
        >
          <LayoutGroup>
          <AnimatePresence custom={dir} initial={false}>
            <motion.section
              key={slide.id}
              custom={dir}
              variants={variants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={slideTransition}
              className="absolute inset-0 overflow-hidden"
            >
              {slide.render()}
            </motion.section>
          </AnimatePresence>
          </LayoutGroup>
          {/* Encima de las diapositivas y sin desmontarse nunca: así los puntos viajan de una a otra. */}
          <ParticleText renderer="canvas" {...particlesFor(index)} />
        </div>

        {/* Barra de progreso */}
        <motion.div
          className="fixed bottom-0 left-0 h-[4px] bg-salvia-media"
          animate={{ width: `${((index + 1) / slides.length) * 100}%` }}
          transition={{ type: "spring", visualDuration: 0.4, bounce: 0 }}
        />

        <AnimatePresence>
          {showHint && (
            <motion.div
              className="pointer-events-none fixed bottom-5 left-1/2 -translate-x-1/2 rounded-full bg-texto/85 px-4 py-2 text-sm text-fondo"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
            >
              ← → para avanzar · F pantalla completa · N notas
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {showNotes && (
            <motion.div
              className="fixed inset-x-0 bottom-0 max-h-[40vh] overflow-auto bg-texto/95 px-7 pb-7 pt-5 text-lg leading-relaxed text-fondo"
              initial={{ y: "100%" }}
              animate={{ y: 0 }}
              exit={{ y: "100%" }}
              transition={{ type: "spring", visualDuration: 0.35, bounce: 0.1 }}
              onClick={(e) => e.stopPropagation()}
            >
              <b className="text-salvia">
                {index + 1} / {slides.length}
              </b>{" "}
              · {slide.notes}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </MotionConfig>
  );
}

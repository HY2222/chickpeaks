import { useEffect, useRef } from "react";
import type { CSSProperties, ReactNode } from "react";
import { animate, motion, useMotionValue, useReducedMotion } from "motion/react";

/*
 * Animaciones de apoyo. Reglas:
 * - Cada una dura menos de 1,5 s y dirige la mirada a la idea o al dato principal.
 * - Solo se anima transform y opacity (los gráficos, con pathLength).
 * - Se lanzan al montar la diapositiva, así que se repiten al volver a ella.
 * - Con "reducir movimiento", MotionConfig (en App) quita los desplazamientos y
 *   contadores y gráficos aparecen ya terminados.
 */

/** Retraso según el orden de entrada dentro de la diapositiva. */
export const at = (order = 1, base = 0.15) => base + (order - 1) * 0.14;

type Base = { o?: number; delay?: number; className?: string; style?: CSSProperties; children?: ReactNode };
const d = (o?: number, delay?: number) => delay ?? at(o);

/** Sube 24 px mientras aparece. */
export function Rise({ o, delay, className, style, children }: Base) {
  return (
    <motion.div
      className={className}
      style={style}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: d(o, delay), ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}

/** Aparece suavemente. */
export function Fade({ o, delay, className, style, children }: Base) {
  return (
    <motion.div className={className} style={style} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, delay: d(o, delay), ease: "easeOut" }}>
      {children}
    </motion.div>
  );
}

/** Para la frase clave de una diapositiva: crece un poco (0,92 → 1) mientras aparece. Sin rebote. */
export function Emphasis({ o, delay, className, style, children }: Base) {
  return (
    <motion.div
      className={className}
      style={style}
      initial={{ opacity: 0, scale: 0.92 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.7, delay: d(o, delay), ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}

/** Mockup del producto en la demo: spring suave y escala de 0,96 a 1. */
export function MockupIn({ o, delay, className, style, children }: Base) {
  return (
    <motion.div
      className={className}
      style={style}
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: "spring", visualDuration: 0.8, bounce: 0.15, delay: d(o, delay) }}
    >
      {children}
    </motion.div>
  );
}

/** Título palabra a palabra: cada palabra sube de 20 px a 0 y pasa de opacidad 0 a 1, con 0,06 s entre palabras. */
export function Words({ text, o, delay }: { text: string; o?: number; delay?: number }) {
  const words = text.split(" ");
  return (
    <motion.span
      initial="hidden"
      animate="show"
      variants={{ show: { transition: { staggerChildren: 0.06, delayChildren: d(o, delay) } } }}
    >
      {words.map((w, i) => (
        <motion.span
          key={i}
          className="inline-block whitespace-pre"
          variants={{
            hidden: { opacity: 0, y: 20 },
            show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
          }}
        >
          {w + (i < words.length - 1 ? " " : "")}
        </motion.span>
      ))}
    </motion.span>
  );
}

/** Cifra clave que sube de 0 a su valor en 1,5 s, con formato español (55.789). */
export function Count({ to, from = 0, prefix = "", suffix = "", o, delay }: { to: number; from?: number; prefix?: string; suffix?: string; o?: number; delay?: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const value = useMotionValue(from);
  const reduced = useReducedMotion();
  const fmt = (v: number) => prefix + new Intl.NumberFormat("es-ES", { useGrouping: "always" } as Intl.NumberFormatOptions).format(Math.round(v)) + suffix;

  useEffect(() => {
    const unsubscribe = value.on("change", (v) => {
      if (ref.current) ref.current.textContent = fmt(v);
    });
    if (reduced) {
      value.set(to);
      return unsubscribe;
    }
    value.set(from);
    const controls = animate(value, to, { duration: 1.5, ease: "easeOut", delay: d(o, delay) });
    return () => {
      controls.stop();
      unsubscribe();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [to, from, reduced]);

  return <span ref={ref}>{fmt(reduced ? to : from)}</span>;
}

/** Barra horizontal que se dibuja de izquierda a derecha (pathLength 0 → 1). */
export function BarH({ width, height, color, o, delay, className, style, round = false }: Base & { width: number; height: number; color: string; round?: boolean }) {
  const reduced = useReducedMotion();
  const r = round ? height / 2 : 0;
  return (
    <svg className={className} style={style} width={width} height={height} viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
      <motion.path
        d={`M${r} ${height / 2} H${width - r}`}
        stroke={color}
        strokeWidth={height}
        strokeLinecap={round ? "round" : "butt"}
        fill="none"
        initial={reduced ? false : { pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.9, delay: d(o, delay), ease: "easeOut" }}
      />
    </svg>
  );
}

/** Barra vertical que se dibuja de abajo arriba (pathLength 0 → 1). */
export function BarV({ width, height, color, o, delay, className, style }: Base & { width: number; height: number; color: string }) {
  const reduced = useReducedMotion();
  return (
    <svg className={className} style={style} width={width} height={height} viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
      <motion.path
        d={`M${width / 2} ${height} V0`}
        stroke={color}
        strokeWidth={width}
        fill="none"
        initial={reduced ? false : { pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.7, delay: d(o, delay), ease: "easeOut" }}
      />
    </svg>
  );
}

/** Flecha que se dibuja (pathLength 0 → 1). */
export function DrawArrow({ o, delay, className, style }: Base) {
  const reduced = useReducedMotion();
  const t = { duration: 0.4, delay: d(o, delay), ease: "easeOut" as const };
  const from = reduced ? false : { pathLength: 0 };
  return (
    <svg className={className} style={style} width="48" height="28" viewBox="0 0 48 28" aria-hidden="true">
      <motion.path d="M3 14 H43" stroke="#A3B18F" strokeWidth="5" strokeLinecap="round" fill="none" initial={from} animate={{ pathLength: 1 }} transition={t} />
      <motion.path
        d="M31 4 L44 14 L31 24"
        stroke="#A3B18F"
        strokeWidth="5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
        initial={from}
        animate={{ pathLength: 1 }}
        transition={{ ...t, delay: t.delay + 0.25 }}
      />
    </svg>
  );
}

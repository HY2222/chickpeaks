import type { ReactNode } from "react";
import { motion } from "motion/react";
import { at, BarH, Count, DrawArrow, Emphasis, Fade, MockupIn, Rise, Words } from "./components/Anim";

const img = (name: string) => `${import.meta.env.BASE_URL}screens/${name}`;

/** dark: fondo oscuro (las partículas se pintan en crema). */
export type Slide = { id: string; notes: string; dark?: boolean; render: () => ReactNode };

/* Color de acento: solo para el dato o la idea importante. El resto, en gris salvia. */
const ACCENT = "#3E5A34";
const GREY = "#CDD5C6";

/* ---------- Piezas comunes ---------- */
const Label = ({ children, dark = false }: { children: ReactNode; dark?: boolean }) => (
  <p className={`text-[28px] font-bold ${dark ? "text-crema/62" : "text-verde"}`}>{children}</p>
);

/**
 * Pie de página. La marca "Willo" lleva layoutId: está en todas las diapositivas,
 * así que no se desvanece con la transición, sino que pasa de una a otra.
 */
const Foot = ({ children, n, dark = false, center = false }: { children?: ReactNode; n?: string; dark?: boolean; center?: boolean }) => (
  <p className={`absolute bottom-[64px] left-[128px] w-[1664px] text-[24px] ${dark ? "text-crema/60" : "text-suave"} ${center ? "text-center" : ""}`}>
    {n && (
      <>
        <motion.b layoutId="marca" className="inline-block">
          Willo
        </motion.b>{" "}
        · {n}
      </>
    )}
    {children && n ? " · " : ""}
    {children}
  </p>
);
const Panel = () => <div className="absolute left-[1200px] top-0 h-[1080px] w-[720px] bg-salvia" />;
/* Titulares en Fraunces (clase .titular, ver index.css). El resto del texto, en Figtree. */
const T72 = "titular text-[72px] font-semibold leading-[1.1]";
const T80 = "titular text-[80px] font-semibold leading-[1.08]";

/* ---------- Diapositivas ---------- */
export const slides: Slide[] = [
  {
    id: "portada",
    notes:
      "Hola. Somos el equipo de Willo. Willo es el modo fácil de tu banco, para personas con discapacidad intelectual. Se usa hablando, en lectura fácil. Su lema: tu voluntad, tu dinero.",
    render: () => (
      <div className="absolute inset-0 bg-fondo text-texto">
        {/* "willo" en partículas: lo pinta la capa de App, que acompaña toda la presentación. */}
        <Fade o={1} className="absolute left-[128px] top-[128px]">
          <Label>El modo fácil de tu banco, por voz</Label>
        </Fade>
        <Rise delay={1.6} className="absolute left-[128px] top-[700px] w-[1664px] text-center">
          <p className="titular text-[64px] italic leading-[1.1] text-suave">Tu voluntad, tu dinero.</p>
        </Rise>
        <Fade delay={2} className="absolute left-[128px] top-[860px] w-[1664px] text-center">
          <p className="text-[32px] leading-[1.35] text-suave">Para personas con discapacidad intelectual. Su asistente se llama Noa.</p>
        </Fade>
        <Fade delay={2.4} className="absolute bottom-[64px] left-[128px] w-[1664px] text-center">
          <p className="text-[24px] text-suave">Equipo ChickPEAKS</p>
        </Fade>
      </div>
    ),
  },
  {
    id: "javi",
    notes:
      "Este es Javi. Tiene 34 años, trabaja en una lavandería y cobra 980 euros al mes. Quiere decidir sobre su dinero, como cualquiera. Pero la app de su banco no está hecha para él. Así que pregunta a su familia para todo, o se arriesga a que le engañen.",
    render: () => (
      <div className="absolute inset-0 bg-fondo text-texto">
        <Panel />
        <div className="absolute left-[128px] top-[128px] flex w-[960px] flex-col gap-[40px]">
          <Label>Os presentamos a Javi</Label>
          <h2 className={T80}>
            <Words text="Javi tiene 34 años, trabaja en una lavandería y cobra 980 € al mes." />
          </h2>
        </div>
        <Rise o={7} className="absolute left-[128px] top-[510px] w-[900px]">
          <p className="text-[36px] leading-[1.3] text-suave">La app de su banco usa palabras técnicas y mucho texto.</p>
        </Rise>
        <Rise o={8} className="absolute left-[128px] top-[640px] w-[900px]">
          <p className="text-[36px] leading-[1.3] text-suave">Por eso depende de su familia para todo. Y está más expuesto a las estafas.</p>
        </Rise>
        <Rise o={3} className="absolute left-[1366px] top-[120px]">
          <img src={img("01-inicio.png")} alt="Pantalla de inicio de Javi en Willo, con sus huchas" className="h-[840px] w-[388px] rounded-[31px] object-contain" />
        </Rise>
        <Foot n="02">Javi es el protagonista de la demo. Sus datos son inventados.</Foot>
      </div>
    ),
  },
  {
    id: "problema",
    notes:
      "Y Javi no es un caso aislado. Según el INE, solo una de cada tres personas con discapacidad intelectual usa internet de forma habitual. En la población general es el 84 por ciento. La banca digital deja fuera justo a quien más apoyo necesita. Y aquí está la oportunidad: desde junio de 2025, la ley obliga a los bancos a ser accesibles.",
    render: () => (
      <div className="absolute inset-0 bg-fondo text-texto">
        <div className="absolute left-[128px] top-[128px] flex w-[1500px] flex-col gap-[40px]">
          <Label>El problema</Label>
          <h2 className={T72}>
            <Words text="Solo 1 de cada 3 personas con discapacidad intelectual usa internet de forma habitual." />
          </h2>
        </div>
        <Fade o={12} className="absolute left-[128px] top-[470px] w-[1664px]">
          <p className="text-[30px] leading-[1.3]">
            <b className="text-verde">La oportunidad:</b> desde junio de 2025, la ley obliga a los bancos a ser accesibles.
          </p>
        </Fade>
        {/* El dato importante en acento; la comparación en gris. */}
        <Fade o={6} className="absolute left-[128px] top-[600px]">
          <p className="text-[32px] font-bold">Personas con discapacidad intelectual</p>
        </Fade>
        <BarH o={6} round width={491} height={96} color={ACCENT} className="absolute left-[128px] top-[654px]" />
        <Fade o={10} className="absolute left-[651px] top-[668px]">
          <p className="titular whitespace-nowrap text-[56px] font-semibold text-verde">1 de cada 3</p>
        </Fade>
        <Fade o={7} className="absolute left-[128px] top-[790px]">
          <p className="text-[32px] text-suave">Población general</p>
        </Fade>
        <BarH o={7} round width={1250} height={96} color={GREY} className="absolute left-[128px] top-[844px]" />
        <p className="absolute left-[1410px] top-[858px] titular whitespace-nowrap text-[56px] font-semibold tabular-nums text-suave">
          <Count to={84} suffix=" %" o={7} />
        </p>
        <Foot n="03">Fuente: INE, datos de 2022, citados por Plena inclusión.</Foot>
      </div>
    ),
  },
  {
    id: "solucion",
    notes:
      'Por eso hemos creado Willo. Es una app de dinero que se usa hablando, con frases cortas y cifras en euros. Su asistente se llama Noa. Noa hace la cuenta y la explica. Pero nunca decide por la persona: siempre termina con "Tú decides".',
    render: () => (
      <div className="absolute inset-0 bg-fondo text-texto">
        <Panel />
        <div className="absolute left-[128px] top-[128px] flex w-[960px] flex-col gap-[40px]">
          <Label>La solución</Label>
          <h2 className={T72}>
            <Words text="Willo es una app de dinero que se usa hablando y en lectura fácil." />
          </h2>
          <Fade o={8}>
            <p className="w-[860px] text-[36px] leading-[1.3] text-suave">Su asistente, Noa, hace las cuentas en voz alta. Y siempre termina igual:</p>
          </Fade>
        </div>
        <div className="absolute left-[1280px] top-[128px] flex w-[560px] flex-col gap-[40px]">
          <Fade o={3}>
            <Label>Lo que gana Javi</Label>
          </Fade>
          {[
            { t: "Más autonomía", d: "Decide sobre su dinero sin pedir permiso." },
            { t: "Menos estafas", d: "Willo le avisa y le explica por qué." },
            { t: "Menos dependencia", d: "Su familia apoya, pero no decide por él." },
          ].map((b, i) => (
            <Rise key={b.t} o={i + 4} className="border-t-2 border-salvia-media pt-[24px]">
              <h3 className="text-[40px] font-bold leading-[1.15]">{b.t}</h3>
              <p className="mt-[8px] text-[28px] leading-[1.3]">{b.d}</p>
            </Rise>
          ))}
        </div>
        <Emphasis o={10} className="absolute left-[128px] top-[670px] origin-left">
          <p className="titular text-[120px] font-semibold leading-[1.05] text-verde">Tú decides.</p>
        </Emphasis>
        <Foot n="04" />
      </div>
    ),
  },
  {
    id: "mercado",
    notes:
      "Nuestro mercado. TAM, Europa: hay casi 7 millones de personas con discapacidad intelectual, y la directiva europea de accesibilidad obliga a todos los bancos de la UE. Son unos 200 millones de euros al año. SAM, España: según el IMSERSO, 157.895 personas con discapacidad intelectual o del desarrollo reconocida; unos 4,5 millones al año. SOM: empezamos por las personas que ya están en asociaciones y organizaciones como AMAS o Plena inclusión. Plena inclusión apoya a 150.000 personas; queremos llegar a 13.816, menos de 1 de cada 10. Eso son unos 416.000 euros al año.",
    render: () => {
      const rows = [
        { k: "TAM", t: "Europa", n: "≈ 7 millones", d: "de personas con discapacidad intelectual. La misma ley en toda la UE.", e: "≈ 200 M€ al año" },
        { k: "SAM", t: "España", n: "157.895", d: "personas con discapacidad intelectual o del desarrollo reconocida.", e: "≈ 4,5 M€ al año" },
        { k: "SOM", t: "Organizaciones", n: "13.816", d: "personas que ya van a asociaciones (Plena inclusión apoya a 150.000).", e: "≈ 416.000 € al año", accent: true },
      ];
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1664px] flex-col gap-[32px]">
            <Label>El mercado</Label>
            <h2 className={T72}>
              <Words text="7 millones en Europa. Empezamos por 13.816." />
            </h2>
          </div>
          {/* Rectángulos uno dentro de otro, como en la plantilla de START. */}
          <Rise o={3} className="absolute left-[128px] top-[400px] h-[520px] w-[760px] rounded-[32px] bg-salvia">
            <p className="absolute left-[40px] top-[32px] text-[40px] font-bold text-verde">TAM</p>
          </Rise>
          <Rise o={4} className="absolute left-[288px] top-[490px] h-[400px] w-[570px] rounded-[28px] bg-salvia-media">
            <p className="absolute left-[36px] top-[28px] text-[40px] font-bold text-verde">SAM</p>
          </Rise>
          <Rise o={5} className="absolute left-[478px] top-[580px] h-[280px] w-[350px] rounded-[24px] bg-verde">
            <p className="absolute left-[32px] top-[24px] text-[40px] font-bold text-fondo">SOM</p>
          </Rise>
          <div className="absolute left-[968px] top-[390px] flex w-[824px] flex-col gap-[22px]">
            {rows.map((r, i) => (
              <Rise key={r.k} o={i + 6} className={i ? "border-t-2 border-salvia pt-[24px]" : ""}>
                <p className={`text-[24px] font-bold ${r.accent ? "text-verde" : "text-suave"}`}>
                  {r.k} · {r.t}
                </p>
                <p className="mt-[4px] flex items-baseline justify-between gap-[24px]">
                  <span className={`titular whitespace-nowrap text-[56px] font-semibold leading-[1.05] ${r.accent ? "text-verde" : ""}`}>{r.n}</span>
                  <span className="whitespace-nowrap text-[28px] font-bold text-verde">{r.e}</span>
                </p>
                <p className="mt-[4px] text-[26px] leading-[1.3] text-suave">{r.d}</p>
              </Rise>
            ))}
          </div>
          <Foot n="05">Fuentes: European Psychiatry (2020); IMSERSO (2024); Plena inclusión. SOM: hipótesis del equipo. Ingresos sin IVA, a 2,40 € por usuario (el SOM incluye la cuota base).</Foot>
        </div>
      );
    },
  },
  {
    id: "competencia",
    notes:
      "Ya hay empresas trabajando en esto. CaixaBank tiene una cuenta con persona de apoyo y una guía en lectura fácil, pero la app no te habla ni te explica cada pago. SpendAble, en Australia, es una tarjeta con app para personas con discapacidad intelectual, pero los presupuestos los pone la persona de apoyo. True Link, en Estados Unidos, protege de estafas bloqueando: decide el cuidador. Y Blue, de BBVA, habla con IA, pero no en lectura fácil ni con apoyos. Willo es el único que junta todo y deja decidir a la persona.",
    render: () => {
      type V = 1 | 0.5 | 0;
      const cols = [
        { n: "CaixaBank", c: "Cuenta con apoyo" },
        { n: "SpendAble", c: "Australia" },
        { n: "True Link", c: "EE. UU." },
        { n: "BBVA Blue", c: "Asistente con IA" },
        { n: "Willo", c: "España", willo: true },
      ];
      const rows: { t: string; v: V[]; nota?: (string | undefined)[] }[] = [
        { t: "Se usa hablando", v: [0, 0, 0, 1, 1] },
        { t: "Explica en lectura fácil", v: [0.5, 0.5, 0, 0, 1], nota: ["Solo una guía", "Con dibujos"] },
        { t: "Hace la cuenta antes de pagar", v: [0, 0.5, 0, 0, 1], nota: [undefined, "Presupuestos"] },
        { t: "Avisa de estafas sin bloquear", v: [0, 0, 0.5, 0, 1], nota: [undefined, undefined, "Bloquea"] },
        { t: "Persona de apoyo con permisos", v: [1, 1, 1, 0, 1] },
        { t: "Decide la persona, no el apoyo", v: [1, 0.5, 0, 1, 1], nota: [undefined, "Pone límites", "Decide el cuidador"] },
      ];
      const X0 = 720, CW = 214, TOP = 436, RH = 84;
      const Icon = ({ v, on }: { v: V; on: boolean }) => {
        const fill = on ? "#F5F7F0" : ACCENT;
        const ink = on ? ACCENT : "#F5F7F0";
        if (v === 1)
          return (
            <svg width="40" height="40" viewBox="0 0 48 48" aria-label="Sí">
              <circle cx="24" cy="24" r="24" fill={fill} />
              <path d="M14 24.5l7 7 13-14" stroke={ink} strokeWidth="4.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          );
        if (v === 0.5)
          return (
            <svg width="40" height="40" viewBox="0 0 48 48" aria-label="En parte">
              <circle cx="24" cy="24" r="22.5" fill="none" stroke={ACCENT} strokeWidth="3" />
              <path d="M24 1.5a22.5 22.5 0 0 1 0 45z" fill={ACCENT} />
            </svg>
          );
        return (
          <svg width="40" height="40" viewBox="0 0 48 48" aria-label="No">
            <circle cx="24" cy="24" r="22.5" fill="none" stroke={GREY} strokeWidth="3" />
            <path d="M16.5 16.5l15 15M31.5 16.5l-15 15" stroke="#8C9A7C" strokeWidth="4.5" strokeLinecap="round" />
          </svg>
        );
      };
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1664px] flex-col gap-[32px]">
            <Label>La competencia</Label>
            <h2 className={T72}>
              <Words text="Ya hay empresas aquí. Ninguna lo junta todo." />
            </h2>
          </div>
          {/* Columna de Willo resaltada, la última: primero se ven los competidores. */}
          <Rise o={3} className="absolute rounded-[20px] bg-verde" style={{ left: X0 + 4 * CW, top: 336, width: CW, height: TOP - 336 + rows.length * RH + 12 }} />
          {cols.map((c, i) => (
            <Fade key={c.n} o={3} className="absolute flex h-[88px] flex-col items-center justify-center text-center" style={{ left: X0 + i * CW, top: 340, width: CW }}>
              <p className={`text-[28px] font-bold leading-[1.15] ${c.willo ? "text-fondo" : ""}`}>{c.n}</p>
              <p className={`text-[20px] leading-[1.3] ${c.willo ? "text-salvia" : "text-suave"}`}>{c.c}</p>
            </Fade>
          ))}
          {rows.map((r, i) => (
            <Rise key={r.t} o={i + 4} className="absolute left-[128px] w-[1664px]" style={{ top: TOP + i * RH, height: RH }}>
              {/* Franja de la fila hasta la columna de Willo, que va encima en verde. */}
              <div className={`absolute inset-y-[6px] left-0 w-[1448px] rounded-l-[16px] ${i % 2 ? "" : "bg-white"}`} />
              <p className="absolute left-[28px] top-1/2 -translate-y-1/2 text-[28px] font-bold leading-[1.15]">{r.t}</p>
              {r.v.map((v, j) => (
                <div key={j} className="absolute top-0 flex h-full flex-col items-center justify-center gap-[2px]" style={{ left: X0 - 128 + j * CW, width: CW }}>
                  <Icon v={v} on={j === 4} />
                  {r.nota?.[j] && <p className="text-[17px] leading-none text-suave">{r.nota[j]}</p>}
                </div>
              ))}
            </Rise>
          ))}
          <Foot n="06" />
        </div>
      );
    },
  },
  {
    id: "demo",
    dark: true,
    notes:
      "Vamos a verlo en directo con los móviles de Javi y de su hermana Ana. Empezamos en la app de MyInvestor: Willo es un botón más, el modo fácil. Seguid el guion de la demo: entrada del concierto, multa de aparcamiento, Bizum de Carlos e informe anual. Si falla la conexión, pasad al vídeo de respaldo: [enlace al vídeo].",
    render: () => (
      <div className="absolute inset-0 bg-noche text-crema">
        <div className="absolute left-[128px] top-[128px] flex w-[1040px] flex-col gap-[40px]">
          <Label dark>Demo en directo · 3 minutos</Label>
          <h2 className={T80}>
            <Words text="Un mes de Javi: una entrada, una multa y un Bizum sospechoso." />
          </h2>
        </div>
        <MockupIn o={2} className="absolute left-[1305px] top-[100px]">
          <img src={img("02-escucha.png")} alt="Pantalla Noa te escucha, con el botón del micrófono" className="h-[880px] w-[407px] rounded-[32px] object-contain" />
        </MockupIn>
        <Rise o={7} className="absolute left-[128px] top-[600px]">
          <a
            href="https://willo-sfh4.onrender.com/demo/banco"
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="inline-flex items-center gap-[16px] rounded-full bg-crema px-[44px] py-[22px] text-[34px] font-bold text-noche no-underline"
          >
            Abrir la demo <span aria-hidden="true">↗</span>
          </a>
        </Rise>
        <Fade o={9} className="absolute left-[128px] top-[800px] w-[960px]">
          <p className="text-[40px] leading-[1.3] text-crema/70">Fijaos en una cosa: Noa explica, pero <span className="text-crema">los botones los pulsa Javi.</span></p>
        </Fade>
        <Foot n="07" dark />
      </div>
    ),
  },
  {
    id: "momentos",
    notes:
      'Resumen de lo que acabáis de ver. Uno: Noa hace la cuenta y dice "Tú decides". Dos: Noa lee una multa; Javi confirma los datos y la foto no se guarda. Tres: ante un Bizum raro, Willo hace una pausa y explica por qué parece una estafa, pero no bloquea nada. Cuatro: el informe para el juez sale en un clic.',
    render: () => {
      const cols = [
        { left: 128, src: "03-respuesta.png", alt: "Noa hace la cuenta de la entrada: de 210 a 165 euros", t: "¿Me lo puedo comprar?", d: "210 € → 165 €. Tú decides." },
        { left: 552, src: "07-documento.png", alt: "Noa explica una multa de aparcamiento de 90 euros", t: "Noa lee tus documentos", d: "Javi confirma los datos. La foto no se guarda." },
        { left: 976, src: "08-pausa.png", alt: "Pausa para pensar ante un Bizum de 300 euros a una persona nueva", t: "Pausa para pensar", d: "Explica por qué parece una estafa. No bloquea." },
        { left: 1400, src: "10-informe.png", alt: "Informe anual 2026 para el juzgado, en lectura fácil", t: "Informe para el juez", d: "Ingresos, gastos, ahorro y avisos. En un clic." },
      ];
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <h2 className={`absolute left-[128px] top-[128px] w-[1664px] ${T72}`}>
            <Words text="Noa explica. Javi decide. Siempre." />
          </h2>
          {cols.map((c, i) => (
            <Rise key={c.src} o={i + 3} className="absolute top-[248px] flex w-[392px] flex-col gap-[24px]" style={{ left: c.left }}>
              <div className="flex justify-center rounded-[24px] bg-salvia p-[32px]">
                <img src={img(c.src)} alt={c.alt} className="h-[460px] w-[213px] rounded-[17px] object-contain" />
              </div>
              <div>
                <h3 className="text-[30px] font-bold leading-[1.2]">{c.t}</h3>
                <p className="mt-[8px] text-[26px] leading-[1.3] text-suave">{c.d}</p>
              </div>
            </Rise>
          ))}
          <Foot n="08" />
        </div>
      );
    },
  },
  {
    id: "circulo",
    notes:
      "En vez de un control parental, Willo tiene un círculo de apoyo, y para Javi solo hay una pregunta: ¿quieres que alguien te acompañe con tu dinero? Hay tres niveles. Solo yo: nadie más ve su dinero. Acompañar: su hermana Ana ve los pagos, y Javi puede llamarla con un toque cuando Noa detecta algo raro. Y Medida judicial, que solo aparece si hay una sentencia: hace lo que diga la sentencia y genera el informe de cuentas para el juez. Cuando algo parece un engaño, Noa avisa y Javi elige: llamar a Ana, o seguir él solo. Si sigue solo, Ana no se entera; Noa le explica por qué parece una estafa y le propone esperar 10 minutos, pero puede saltárselo. El pago nunca se bloquea. Willo avisa, Javi decide. Esto sigue la Ley 8/2021: apoyar a la persona, no sustituirla.",
    render: () => {
      const niveles = [
        { t: "Solo yo", d: "Nadie más ve el dinero de Javi." },
        { t: "Acompañar", d: "Ana ve los pagos, y Javi la llama con un toque si Noa ve algo raro.", ana: true },
        { t: "Medida judicial", d: "Solo si hay una sentencia. Hace lo que diga y genera el informe para el juez." },
      ];
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1664px] flex-col gap-[28px]">
            <Label>El círculo de apoyo</Label>
            <h2 className={T80}>
              <Words text="Willo avisa, Javi decide." />
            </h2>
            <Fade o={3}>
              <p className="text-[30px] leading-[1.3] text-suave">Para Javi solo hay una pregunta: ¿quieres que alguien te acompañe con tu dinero?</p>
            </Fade>
          </div>
          {/* Los tres niveles */}
          <div className="absolute left-[128px] top-[430px] flex w-[860px] flex-col gap-[18px]">
            {niveles.map((n, i) => (
              <Rise key={n.t} o={i + 4}
                className={`flex items-center gap-[28px] rounded-[20px] px-[32px] py-[26px] ${n.ana ? "bg-verde text-fondo" : "bg-white"}`}>
                <span className={`grid h-[56px] w-[56px] flex-none place-items-center rounded-full text-[26px] font-bold ${n.ana ? "bg-fondo text-verde" : "bg-salvia text-verde"}`}>{i + 1}</span>
                <div className="flex-1">
                  <h3 className="flex items-center gap-[14px] text-[34px] font-bold leading-[1.15]">
                    {n.t}
                    {n.ana && <span className="rounded-full bg-fondo px-[14px] py-[2px] text-[20px] font-bold text-verde">Ana</span>}
                  </h3>
                  <p className={`mt-[6px] text-[24px] leading-[1.3] ${n.ana ? "text-salvia" : "text-suave"}`}>{n.d}</p>
                </div>
              </Rise>
            ))}
          </div>
          {/* El aviso: Javi decide si llama a Ana */}
          <Rise o={7} className="absolute left-[1060px] top-[430px] w-[732px] rounded-[28px] bg-white p-[36px] shadow-[0_2px_10px_rgba(30,42,27,0.08)]">
            <div className="flex items-start gap-[18px]">
              <span className="grid h-[56px] w-[56px] flex-none place-items-center rounded-full bg-verde text-[24px] font-bold text-fondo">N</span>
              <p className="rounded-[20px] rounded-tl-[6px] bg-salvia px-[24px] py-[18px] text-[28px] leading-[1.3]">
                Cuidado. Este pago se parece a un engaño. ¿Quieres hablar con Ana antes de pagar?
              </p>
            </div>
            <div className="mt-[28px] grid grid-cols-2 gap-[16px]">
              <span className="flex items-center justify-center gap-[10px] rounded-full bg-verde py-[18px] text-[26px] font-bold text-fondo">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2" />
                </svg>
                Llamar a Ana
              </span>
              <span className="flex items-center justify-center rounded-full border-[3px] border-verde py-[15px] text-[26px] font-bold text-verde">Sigo yo</span>
            </div>
            <div className="mt-[20px] grid grid-cols-2 gap-[16px] text-[21px] leading-[1.35] text-suave">
              <Fade o={9}><p>Se abre la llamada y Ana ve el pago para poder ayudarle.</p></Fade>
              <Fade o={10}><p>Ana no se entera. Noa explica por qué parece un engaño y propone esperar 10 minutos.</p></Fade>
            </div>
          </Rise>
          <Foot n="09">El pago nunca se bloquea. Basado en la Ley 8/2021: apoyar a la persona, no sustituirla.</Foot>
        </div>
      );
    },
  },
  {
    id: "tecnologia",
    notes:
      "La clave técnica: la IA nunca calcula ni decide. ElevenLabs da la voz y la conversación de Noa, y el dictado con Scribe. Nuestro backend en FastAPI hace todas las cuentas y las reglas antiestafa. Claude lee los documentos y lo escribe en lectura fácil. Y al final decide Javi. Es una PWA desplegada en Render, sin tienda de apps.",
    render: () => {
      const card = "absolute top-[450px] flex h-[350px] w-[356px] flex-col gap-[12px] rounded-[20px] p-[36px]";
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1400px] flex-col gap-[32px]">
            <Label>Cómo funciona</Label>
            <h2 className={T72}>
              <Words text="La IA explica. Las cuentas las hace nuestro código." />
            </h2>
          </div>
          <Rise o={5} className={`${card} left-[128px] bg-white`}>
            <p className="text-[24px] font-bold text-suave">ElevenLabs</p>
            <h3 className="text-[36px] font-bold leading-[1.15]">Noa escucha y habla</h3>
            <p className="text-[26px] leading-[1.3] text-suave">La voz, la conversación y el dictado (Scribe).</p>
          </Rise>
          <DrawArrow o={6} className="absolute left-[500px] top-[611px]" />
          <Rise o={7} className={`${card} left-[564px] bg-verde text-fondo`}>
            <p className="text-[24px] font-bold text-salvia">Nuestro código</p>
            <h3 className="text-[36px] font-bold leading-[1.15]">El código hace la cuenta</h3>
            <p className="text-[26px] leading-[1.3] text-salvia">
              210 € − 45 € = <Count from={210} to={165} suffix=" €" o={8} />. Sin IA.
            </p>
          </Rise>
          <DrawArrow o={8} className="absolute left-[936px] top-[611px]" />
          <Rise o={9} className={`${card} left-[1000px] bg-white`}>
            <p className="text-[24px] font-bold text-suave">Claude</p>
            <h3 className="text-[36px] font-bold leading-[1.15]">Lo explica en lectura fácil</h3>
            <p className="text-[26px] leading-[1.3] text-suave">Y lee las fotos de multas y facturas.</p>
          </Rise>
          <DrawArrow o={10} className="absolute left-[1372px] top-[611px]" />
          <Rise o={11} className={`${card} left-[1436px] bg-salvia`}>
            <p className="text-[24px] font-bold text-verde">La persona</p>
            <h3 className="text-[36px] font-bold leading-[1.15]">Javi decide</h3>
            <p className="text-[26px] leading-[1.3]">Willo nunca compra, nunca paga y nunca bloquea.</p>
          </Rise>
          <Fade o={12} className="absolute left-[128px] top-[860px] w-[1664px]">
            <p className="text-[28px] leading-[1.3] text-suave">Se instala desde el navegador, sin tienda de apps. Se guardan los datos, nunca las fotos.</p>
          </Fade>
          <Foot n="10" />
        </div>
      );
    },
  },
  {
    id: "lectura-facil",
    notes:
      "¿Cómo sabemos que Noa explica fácil? Lo medimos. El índice Fernández-Huerta mide lo fácil que es leer un texto en español, de 0 a 100; de 80 para arriba es fácil. En nuestros tres ejemplos, una carta falsa de la Seguridad Social pasa de 22, muy difícil, a 98 con Noa. La multa, de 44 a 87. Y la factura de la luz, de 26 a 100. Son papeles escritos por el equipo al estilo de los reales, y lo hemos medido con nuestros propios scripts.",
    render: () => {
      const X0 = 700, X1 = 1792, x = (v: number) => X0 + ((X1 - X0) * v) / 100;
      const rows = [
        { t: "Carta falsa de la Seguridad Social", a: 22, b: 98 },
        { t: "Multa de aparcamiento", a: 44, b: 87 },
        { t: "Factura de la luz", a: 26, b: 100 },
      ];
      const Y = (i: number) => 540 + i * 120;
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1664px] flex-col gap-[28px]">
            <Label>Lectura fácil, medida</Label>
            <h2 className={T72}>
              <Words text="Con Noa, papeles difíciles se vuelven fáciles de leer." />
            </h2>
            <Fade o={4}>
              <p className="text-[28px] leading-[1.3] text-suave">
                Índice Fernández-Huerta: mide lo fácil que es leer un texto en español, de 0 a 100. <b className="text-verde">De 80 para arriba, es fácil.</b>
              </p>
            </Fade>
          </div>
          <svg className="absolute inset-0" width="1920" height="1080" viewBox="0 0 1920 1080" aria-hidden="true">
            {/* Zona «fácil»: de 80 a 100 */}
            <motion.rect x={x(80)} y={470} width={x(100) - x(80)} height={380} rx={16} fill="#D3DFC8"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4, delay: at(5) }} />
            <motion.text x={(x(80) + x(100)) / 2} y={834} textAnchor="middle" fontSize="22" fontWeight="700" fill={ACCENT}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4, delay: at(5) }}>Fácil (80+)</motion.text>
            {/* Eje */}
            <line x1={X0} x2={X1} y1={880} y2={880} stroke="#C4CEBB" strokeWidth="2" />
            {[0, 25, 50, 80, 100].map((v) => (
              <g key={v}>
                <line x1={x(v)} x2={x(v)} y1={872} y2={888} stroke="#A3B18F" strokeWidth="2" />
                <text x={x(v)} y={918} textAnchor="middle" fontSize="22" fill="#4A5745">{v}</text>
              </g>
            ))}
            {rows.map((r, i) => (
              <g key={r.t}>
                <line x1={X0} x2={X1} y1={Y(i)} y2={Y(i)} stroke="#E3E9DC" strokeWidth="2" />
                <motion.line x1={x(r.a)} x2={x(r.b)} y1={Y(i)} y2={Y(i)} stroke={ACCENT} strokeWidth="6" strokeLinecap="round"
                  initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.8, delay: at(7 + i * 2), ease: "easeOut" }} />
                <motion.circle cx={x(r.a)} cy={Y(i)} r={14} fill="#A3B18F" style={{ transformBox: "fill-box", transformOrigin: "center" }}
                  initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ duration: 0.3, delay: at(6 + i * 2) }} />
                <motion.text x={x(r.a)} y={Y(i) - 28} textAnchor="middle" fontSize="28" fontWeight="700" fill="#4A5745"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3, delay: at(6 + i * 2) }}>{r.a}</motion.text>
                <motion.circle cx={x(r.b)} cy={Y(i)} r={20} fill={ACCENT} style={{ transformBox: "fill-box", transformOrigin: "center" }}
                  initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ duration: 0.3, delay: at(8 + i * 2) }} />
                <motion.text x={x(r.b)} y={Y(i) - 34} textAnchor="middle" fontSize="36" fontWeight="800" fill={ACCENT}
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3, delay: at(8 + i * 2) }}>{r.b}</motion.text>
              </g>
            ))}
          </svg>
          {rows.map((r, i) => (
            <Fade key={r.t} o={6 + i * 2} className="absolute left-[128px] w-[540px]" style={{ top: Y(i) - 18 }}>
              <p className="whitespace-nowrap text-[28px] font-bold leading-[1.15]">{r.t}</p>
            </Fade>
          ))}
          <Fade o={12} className="absolute left-[128px] top-[860px] flex w-[460px] flex-col gap-[10px] text-[22px] text-suave">
            <span className="flex items-center gap-[10px]"><i className="inline-block h-[20px] w-[20px] rounded-full bg-salvia-media" /> El papel original</span>
            <span className="flex items-center gap-[10px]"><i className="inline-block h-[20px] w-[20px] rounded-full bg-verde" /> Lo que dice Noa</span>
          </Fade>
          <Foot n="11">En nuestros 3 ejemplos: papeles escritos por el equipo al estilo de los reales. Medido con nuestros scripts.</Foot>
        </div>
      );
    },
  },
  {
    id: "negocio",
    notes:
      "¿Quién paga? El banco, no la persona. Es un SaaS B2B2C: el banco se lo da gratis a sus clientes con discapacidad intelectual. ¿Por qué paga? Porque la Ley 11/2023 ya le obliga a ser accesible. Cobramos en tres partes. Una implantación de 15.000 euros, una sola vez: integrar Willo en su app, con su marca, y formar a su equipo. Una cuota base de 1.500 euros al mes, que cubre la plataforma y el soporte. Y 2,40 euros al mes por cada usuario activo: solo cuenta quien usa Willo ese mes. Así el banco paga según el uso real. Por ejemplo, un banco con 13.816 usuarios paga unos 34.700 euros al mes.",
    render: () => {
      const parts = [
        { t: "Cuota base", d: "Plataforma, soporte y mantenimiento", p: "1.500 €", u: "al mes" },
        { t: "Por usuario activo", d: "Solo cuenta quien usa Willo ese mes", p: "2,40 €", u: "al mes", accent: true },
        { t: "Implantación", d: "Integración, marca y formación", p: "15.000 €", u: "una vez" },
      ];
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1500px] flex-col gap-[32px]">
            <Label>Modelo de negocio · B2B2C · SaaS por suscripción</Label>
            <h2 className={T72}>
              <Words text="Paga el banco, porque la ley ya le pide ser accesible." />
            </h2>
          </div>
          <div className="absolute left-[128px] top-[420px] flex w-[784px] flex-col">
            <Fade o={5}>
              <p className="pb-[12px] text-[28px] font-bold text-verde">Lo que paga el banco</p>
            </Fade>
            {parts.map((it, i) => (
              <Rise key={it.t} o={i + 6} className={`flex items-center justify-between py-[20px] ${i ? "border-t-2 border-salvia" : ""}`}>
                <p className="flex flex-col">
                  <span className={`text-[36px] font-bold leading-[1.15] ${it.accent ? "text-verde" : ""}`}>{it.t}</span>
                  <span className="text-[24px] leading-[1.3] text-suave">{it.d}</span>
                </p>
                <p className="flex flex-col items-end">
                  <span className={`titular whitespace-nowrap text-[52px] font-semibold leading-none ${it.accent ? "text-verde" : ""}`}>{it.p}</span>
                  <span className="mt-[6px] text-[22px] text-suave">{it.u}</span>
                </p>
              </Rise>
            ))}
          </div>
          <div className="absolute left-[1008px] top-[440px] flex h-[480px] w-[784px] flex-col justify-center gap-[16px]">
            <p className="text-[28px] font-bold text-verde">Ejemplo: un banco con 13.816 usuarios</p>
            <Emphasis o={9} className="origin-left">
              <p className="titular whitespace-nowrap text-[128px] font-semibold leading-none tracking-normal tabular-nums text-verde">34.658 €</p>
            </Emphasis>
            <Fade o={10}>
              <p className="text-[32px] leading-[1.3]">al mes: 1.500 € de base + 13.816 × 2,40 €.</p>
            </Fade>
            <Fade o={11}>
              <p className="text-[26px] leading-[1.3] text-suave">La persona no paga nada. El banco paga según el uso real.</p>
            </Fade>
          </div>
          <Foot n="12">Precios sin IVA, pendientes de validar con bancos. Mismo modelo que FinCell y Crassula: alta + cuota base + uso.</Foot>
        </div>
      );
    },
  },
  {
    id: "numeros",
    notes:
      "Y los números salen. Con nuestro SOM, un banco con 13.816 usuarios nos paga 1.500 euros de base y 2,40 euros por usuario: unos 34.700 euros al mes. Los costes: la IA es el más grande, unos 15.100 euros al mes, contando 3 conversaciones al día por usuario a poco más de 1 céntimo cada una. Mantenimiento: 30 horas al mes a 40 euros la hora, 1.200 euros. Y el alojamiento en Vercel y Render, unos 24 euros. En total, unos 16.340 euros. Nos quedan unos 18.320 euros al mes: un margen operativo del 53 por ciento. Y la cuota base ya cubre nuestros costes fijos: cada usuario nuevo nos deja 1,31 euros de margen al mes.",
    render: () => {
      const rows = [
        { t: "Ingresos sin IVA", d: "Base 1.500 € + 13.816 usuarios × 2,40 €", v: "34.658 €" },
        { t: "IA para conversar", d: "3 conversaciones al día · 0,0136 $ cada una", v: "− 15.117 €" },
        { t: "Mantenimiento", d: "30 horas al mes a 40 €/hora", v: "− 1.200 €" },
        { t: "Infraestructura", d: "Vercel y Render", v: "− 24 €" },
        { t: "Resultado operativo", d: "Lo que nos queda cada mes", v: "18.318 €", accent: true },
      ];
      const W = 1664, ia = Math.round((W * 15116.55) / 34658.4), otros = Math.round((W * 1224.14) / 34658.4);
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1664px] flex-col gap-[32px]">
            <Label>Ingresos y costes · al mes, con el SOM</Label>
            <h2 className={T72}>
              <Words text="Nos quedan 53 céntimos de cada euro." />
            </h2>
          </div>
          {/* Una barra = los ingresos. Gris: costes. Verde: lo que queda. */}
          <BarH o={4} width={ia} height={64} color={GREY} className="absolute left-[128px] top-[330px]" />
          <BarH o={5} width={otros} height={64} color="#A3B18F" className="absolute top-[330px]" style={{ left: 128 + ia }} />
          <BarH o={6} width={W - ia - otros} height={64} color={ACCENT} className="absolute top-[330px]" style={{ left: 128 + ia + otros }} />
          <Fade o={6} className="absolute left-[128px] top-[406px]">
            <p className="flex items-center gap-[10px] text-[24px] font-bold text-suave"><i className="inline-block h-[18px] w-[18px] rounded-full" style={{ background: GREY }} />IA · 44 %</p>
          </Fade>
          <Fade o={7} className="absolute top-[406px]" style={{ left: 128 + ia }}>
            <p className="flex items-center gap-[10px] whitespace-nowrap text-[24px] font-bold text-suave"><i className="inline-block h-[18px] w-[18px] rounded-full bg-[#A3B18F]" />Mantenimiento e infraestructura · 3,5 %</p>
          </Fade>
          <Fade o={8} className="absolute top-[406px] flex justify-end" style={{ left: 128 + ia + otros, width: W - ia - otros }}>
            <p className="flex items-center gap-[10px] text-[24px] font-bold text-verde"><i className="inline-block h-[18px] w-[18px] rounded-full" style={{ background: ACCENT }} />Resultado · 53 %</p>
          </Fade>
          <div className="absolute left-[128px] top-[470px] flex w-[1040px] flex-col">
            {rows.map((r, i) => (
              <Rise key={r.t} o={i + 7} className={`flex items-baseline justify-between gap-[24px] py-[10px] ${i ? "border-t-2 border-salvia" : ""}`}>
                <p className="flex flex-col">
                  <span className={`text-[28px] font-bold leading-[1.15] ${r.accent ? "text-verde" : ""}`}>{r.t}</span>
                  <span className="text-[20px] leading-[1.3] text-suave">{r.d}</span>
                </p>
                <span className={`titular whitespace-nowrap text-[40px] font-semibold tabular-nums ${r.accent ? "text-verde" : ""}`}>{r.v}</span>
              </Rise>
            ))}
          </div>
          <Rise o={12} className="absolute left-[1248px] top-[480px] flex h-[190px] w-[544px] flex-col justify-center gap-[6px] rounded-[20px] bg-verde px-[36px] text-fondo">
            <p className="text-[22px] font-bold text-salvia">Margen operativo</p>
            <p className="titular text-[72px] font-semibold leading-none">53 %</p>
          </Rise>
          <Rise o={13} className="absolute left-[1248px] top-[694px] flex h-[190px] w-[544px] flex-col justify-center gap-[6px] rounded-[20px] bg-salvia px-[36px]">
            <p className="text-[22px] font-bold text-verde">Cada usuario nuevo nos deja</p>
            <p className="titular text-[56px] font-semibold leading-none text-verde">+ 1,31 € al mes</p>
          </Rise>
          <Foot n="13">Estimación del equipo, sin datos reales. Precios pendientes de validar con bancos. IA: 1 $ ≈ 0,89 €.</Foot>
        </div>
      );
    },
  },
  {
    id: "go-to-market",
    notes:
      "¿Cómo llegamos? Paso 1: entramos por las asociaciones. AMAS ya ha validado Willo y quiere que sus usuarios prueben la demo. Y ese es nuestro canal: Plena inclusión agrupa unas 950 asociaciones que apoyan a 150.000 personas. Paso 2: un piloto con un banco, con Willo dentro de su app; esa pantalla ya está hecha. Paso 3: más bancos y Europa, porque la ley viene de una directiva europea. En números: cada banco paga 15.000 euros al empezar, 1.500 euros al mes de base y 2,40 euros por usuario activo. Y captar usuarios nos cuesta casi cero, porque nos llegan por las asociaciones.",
    render: () => {
      const card = "absolute top-[400px] flex h-[270px] w-[480px] flex-col gap-[10px] rounded-[20px] p-[36px]";
      const metrics = [
        { k: "Implantación", v: "15.000 €", d: "una vez, por banco" },
        { k: "Cuota base", v: "1.500 €", d: "al mes, por banco" },
        { k: "Por usuario", v: "2,40 €", d: "al mes, por usuario" },
        { k: "Captar usuarios", v: "≈ 0 €", d: "entramos por las asociaciones" },
      ];
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1664px] flex-col gap-[32px]">
            <Label>Go to market</Label>
            <h2 className={T72}>
              <Words text="Entramos por las asociaciones. Vendemos a los bancos." />
            </h2>
          </div>
          <Rise o={4} className={`${card} left-[128px] bg-white`}>
            <p className="text-[22px] font-bold text-suave">Paso 1 · Validar</p>
            <h3 className="text-[36px] font-bold leading-[1.15]">Con las asociaciones</h3>
            <p className="text-[24px] leading-[1.3] text-suave">AMAS ya ha validado Willo y quiere colaborar para que personas con discapacidad intelectual prueben la demo.</p>
          </Rise>
          <DrawArrow o={5} className="absolute left-[624px] top-[521px]" />
          <Rise o={6} className={`${card} left-[720px] bg-verde text-fondo`}>
            <p className="text-[22px] font-bold text-salvia">Paso 2 · Piloto</p>
            <h3 className="text-[36px] font-bold leading-[1.15]">Con un banco</h3>
            <p className="text-[24px] leading-[1.3] text-salvia">Willo va dentro de la app del banco. Esa pantalla ya está hecha.</p>
          </Rise>
          <DrawArrow o={7} className="absolute left-[1216px] top-[521px]" />
          <Rise o={8} className={`${card} left-[1312px] bg-salvia`}>
            <p className="text-[22px] font-bold text-verde">Paso 3 · Crecer</p>
            <h3 className="text-[36px] font-bold leading-[1.15]">Más bancos y Europa</h3>
            <p className="text-[24px] leading-[1.3]">La ley viene de una directiva europea: toda la UE tiene la misma obligación.</p>
          </Rise>
          <Rise o={9} className="absolute left-[128px] top-[700px] flex h-[220px] w-[560px] flex-col justify-center gap-[10px] rounded-[20px] border-2 border-verde p-[32px]">
            <p className="text-[22px] font-bold text-verde">Nuestro canal</p>
            <p className="titular text-[38px] font-semibold leading-[1.1]">950 asociaciones<br />150.000 personas</p>
            <p className="text-[24px] leading-[1.3] text-suave">Las que agrupa Plena inclusión en España.</p>
          </Rise>
          {metrics.map((m, i) => (
            <Rise key={m.k} o={i + 10} className="absolute top-[700px] flex h-[220px] w-[254px] flex-col justify-center gap-[6px] rounded-[20px] bg-white p-[28px]" style={{ left: 720 + i * 270 }}>
              <p className="text-[22px] font-bold text-suave">{m.k}</p>
              <p className="titular whitespace-nowrap text-[44px] font-semibold leading-none text-verde">{m.v}</p>
              <p className="text-[22px] leading-[1.25] text-suave">{m.d}</p>
            </Rise>
          ))}
          <Foot n="14">Precios: propuesta del equipo, pendiente de validar con bancos. Fuentes: Plena inclusión España; Directiva (UE) 2019/882.</Foot>
        </div>
      );
    },
  },
  {
    id: "equipo",
    notes:
      "Somos seis y nos complementamos: Inés, nuestra arquitecta de machine learning; Jiawen, analista de datos; He Ye, de Informática y ADE; Nolan, de Empresa y Tecnología; XingYi, de Telecomunicación; y Anqi, de Economía.",
    render: () => {
      const team = [
        { n: "Inés", r: "Arquitecta de ML" },
        { n: "Jiawen", r: "Analista de Datos" },
        { n: "He Ye", r: "Informática y ADE" },
        { n: "Nolan", r: "Empresa y Tecnología" },
        { n: "XingYi", r: "Telecomunicación" },
        { n: "Anqi", r: "Economía" },
      ];
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1664px] flex-col gap-[32px]">
            <Label>El equipo</Label>
            <h2 className={T72}>
              <Words text="Somos seis, y nos complementamos." />
            </h2>
          </div>
          <div className="absolute left-[128px] top-[470px] grid w-[1664px] grid-cols-3 gap-x-[64px] gap-y-[64px]">
            {team.map((p, i) => (
              <Rise key={p.n} o={i + 4} className="border-t-2 border-salvia pt-[20px]">
                <h3 className="text-[44px] font-bold leading-[1.15]">{p.n}</h3>
                <p className="mt-[8px] text-[30px] leading-[1.3] text-suave">{p.r}</p>
              </Rise>
            ))}
          </div>
          <Foot n="15" />
        </div>
      );
    },
  },
  {
    id: "objetivo",
    notes:
      "Nuestro objetivo: un piloto con un banco en 2027. Para llegar, hoy os pedimos dos cosas: contactos en bancos y mentoría para preparar ese piloto. Esto es lo que viene: ya tenemos la demo; en los próximos meses, los primeros usuarios con AMAS y Plena inclusión; en 2027, el piloto con un banco; y después, más bancos y Europa.",
    render: () => {
      const steps = [
        { w: "Hoy", t: "Demo que funciona" },
        { w: "Próximos meses", t: "Primeros usuarios con AMAS y Plena inclusión" },
        { w: "2027", t: "Piloto con un banco", accent: true },
        { w: "Después", t: "Más bancos y Europa" },
      ];
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1664px] flex-col gap-[32px]">
            <Label>Nuestro objetivo</Label>
            <h2 className={T80}>
              <Words text="Un piloto con un banco en 2027." />
            </h2>
          </div>
          <Rise o={4} className="absolute left-[128px] top-[380px] flex w-[1664px] items-center gap-[48px] rounded-[24px] bg-verde px-[48px] py-[36px] text-fondo">
            <p className="w-[360px] text-[28px] font-bold leading-[1.2] text-salvia">Lo que os pedimos hoy</p>
            <p className="titular text-[52px] font-semibold leading-[1.1]">Contactos en bancos y mentoría para el piloto.</p>
          </Rise>
          <Fade o={6} className="absolute left-[128px] top-[640px]">
            <p className="text-[28px] font-bold text-verde">Qué pasa después</p>
          </Fade>
          <BarH o={7} round width={1664} height={8} color={GREY} className="absolute left-[128px] top-[716px]" />
          {steps.map((st, i) => (
            <Rise key={st.w} o={i + 8} className="absolute top-[700px] flex w-[400px] flex-col gap-[16px]" style={{ left: 128 + i * 421 }}>
              <span className={`block h-[40px] w-[40px] rounded-full border-[6px] border-fondo ${st.accent ? "bg-verde" : "bg-salvia-media"}`} />
              <p className={`text-[26px] font-bold ${st.accent ? "text-verde" : "text-suave"}`}>{st.w}</p>
              <p className={`text-[32px] font-bold leading-[1.2] ${st.accent ? "text-verde" : ""}`}>{st.t}</p>
            </Rise>
          ))}
          <Foot n="16" />
        </div>
      );
    },
  },
  {
    id: "cierre",
    dark: true,
    notes: "Willo no decide por nadie. Explica, avisa y deja decidir. Willo: tu voluntad, tu dinero. Gracias.",
    render: () => (
      <div className="absolute inset-0 bg-noche text-crema">
        {/* "willo" vuelve a formarse aquí con las partículas de la capa de App. */}
        <h1 className="absolute left-[128px] top-[640px] w-[1664px] titular text-center text-[96px] italic font-semibold leading-[1.05]">
          <Words text="Tu voluntad, tu dinero." delay={1.6} />
        </h1>
        <p className="absolute left-[128px] top-[790px] w-[1664px] text-center text-[40px] leading-[1.3] text-crema/75">
          <Words text="Nunca compra. Nunca paga. Nunca bloquea." delay={2.1} />
        </p>
        <Foot dark center>
          Equipo ChickPEAKS · [correo de contacto]
        </Foot>
      </div>
    ),
  },
];

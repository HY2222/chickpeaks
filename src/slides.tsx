import type { ReactNode } from "react";
import { motion } from "motion/react";
import { at, BarH, BarV, Count, DrawArrow, Emphasis, Fade, MockupIn, Rise, Words } from "./components/Anim";

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
      "Nuestro mercado. TAM: según el IMSERSO, en España hay 157.895 personas con discapacidad intelectual o trastorno del desarrollo reconocida. SAM: calculamos que al principio podemos llegar a un 35 %, unas 55.263 personas, a través de bancos españoles. SOM: en los primeros años esperamos captar un 25 % de esas, unas 13.816 personas. A 2 euros al mes por usuario, eso son unos 330.000 euros al año.",
    render: () => {
      const rows = [
        { k: "TAM", t: "Mercado total", n: "157.895", d: "personas con discapacidad intelectual o del desarrollo reconocida.", e: "≈ 3,8 M€ al año" },
        { k: "SAM", t: "Lo que podemos atacar", n: "55.263", d: "a las que llegamos al principio con bancos (35\u00a0% del TAM).", e: "≈ 1,3 M€ al año" },
        { k: "SOM", t: "Primer mercado", n: "13.816", d: "que esperamos captar los primeros años (25\u00a0% del SAM).", e: "≈ 330.000 € al año", accent: true },
      ];
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1664px] flex-col gap-[32px]">
            <Label>El mercado</Label>
            <h2 className={T72}>
              <Words text="Casi 158.000 personas. Empezamos por 13.816." />
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
          <Foot n="05">Fuente del TAM: IMSERSO (2024). SAM y SOM: hipótesis del equipo. Ingresos a 2 € al mes por usuario.</Foot>
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
      "En vez de un control parental, Willo tiene un círculo de apoyo. Javi elige quién le apoya y cuánto, con nombres fáciles: Solo yo, Ver, Apoyar, Guardar y Representar. Ver y Apoyar los da y los quita Javi. Ana, su hermana, está en Guardar: recibe avisos de estafa al momento y saca el informe anual para el juez. Esto sigue la Ley 8/2021: apoyar a la persona, no sustituirla.",
    render: () => {
      const steps = [
        { name: "Solo yo", d: "Nadie más ve su dinero.", h: 60 },
        { name: "Ver", d: "Ve sus pagos.", h: 110 },
        { name: "Apoyar", d: "Recibe avisos de estafa.", h: 160 },
        { name: "Guardar", d: "Lleva las cuentas para el juez.", h: 210, ana: true },
        { name: "Representar", d: "Solo lo que diga la sentencia.", h: 260 },
      ];
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1300px] flex-col gap-[32px]">
            <Label>El círculo de apoyo</Label>
            <h2 className={T72}>
              <Words text="Javi elige quién le apoya, y hasta dónde." />
            </h2>
          </div>
          {steps.map((s, i) => (
            <div key={s.name} className="absolute top-[480px] flex h-[440px] w-[320px] flex-col justify-end gap-[24px]" style={{ left: 128 + i * 336 }}>
              {/* Escalones como barras: el nivel de Ana en acento, el resto en gris. */}
              <div className="relative" style={{ height: s.h }}>
                <BarV o={i + 4} width={320} height={s.h} color={s.ana ? ACCENT : "#DDE3D6"} className="absolute inset-0" />
                {s.ana && (
                  <Fade delay={at(10)} className="absolute left-[24px] top-[24px]">
                    <p className="text-[32px] font-bold text-fondo">Ana</p>
                  </Fade>
                )}
              </div>
              <Fade o={i + 4} className="h-[124px]">
                <h3 className={`text-[36px] font-bold ${s.ana ? "text-verde" : ""}`}>{s.name}</h3>
                <p className="mt-[8px] text-[26px] leading-[1.3] text-suave">{s.d}</p>
              </Fade>
            </div>
          ))}
          <Foot n="09">Cada nivel incluye el anterior. Ninguno puede bloquear un pago. Basado en la Ley 8/2021.</Foot>
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
    id: "negocio",
    notes:
      "¿Quién paga? El banco. Es un modelo B2B2C basado en SaaS: el banco paga una suscripción mensual, por tramos según el número de usuarios, y ofrece Willo gratis a sus clientes con discapacidad intelectual. Así quitamos la barrera económica a quien más lo necesita. La Ley 11/2023 le da el motivo: sus servicios tienen que ser accesibles. Precio objetivo: unos 2 euros al mes por usuario; con nuestro SOM, unos 330.000 euros al año. En el futuro, servicios extra: personalización, integración con sus sistemas y analítica agregada.",
    render: () => {
      const items = [
        { t: "Ahora: suscripción del banco", d: "Cuota mensual por tramos de usuarios. Para la persona, gratis.", accent: true },
        { t: "Por qué paga", d: "La Ley 11/2023 obliga a que sus servicios sean accesibles." },
        { t: "Después: servicios extra", d: "Personalización, integración y analítica agregada." },
      ];
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1500px] flex-col gap-[32px]">
            <Label>Modelo de negocio · B2B2C · SaaS por suscripción</Label>
            <h2 className={T72}>
              <Words text="Paga el banco, porque la ley ya le pide ser accesible." />
            </h2>
          </div>
          <div className="absolute left-[128px] top-[440px] flex w-[784px] flex-col gap-[24px]">
            {items.map((it, i) => (
              <Rise key={it.t} o={i + 6} className={i ? "border-t-2 border-salvia pt-[28px]" : ""}>
                <h3 className={`text-[40px] font-bold ${it.accent ? "text-verde" : ""}`}>{it.t}</h3>
                <p className="mt-[8px] text-[28px] leading-[1.3] text-suave">{it.d}</p>
              </Rise>
            ))}
          </div>
          <div className="absolute left-[1008px] top-[470px] flex h-[450px] w-[784px] flex-col justify-center gap-[16px]">
            <p className="text-[28px] font-bold text-verde">Precio objetivo</p>
            <p className="titular whitespace-nowrap text-[160px] font-semibold leading-none tracking-normal tabular-nums text-verde">
              <Count to={2} suffix=" €" o={6} />
            </p>
            <Fade o={10}>
              <p className="text-[32px] leading-[1.3]">al mes por usuario, dentro del tramo que elige el banco. La persona no paga nada.</p>
            </Fade>
            <Fade o={11}>
              <p className="text-[26px] leading-[1.3] text-suave">Con el SOM (13.816 usuarios): ≈ 330.000 € al año.</p>
            </Fade>
          </div>
          <Foot n="11">Precio: propuesta del equipo, pendiente de validar con bancos.</Foot>
        </div>
      );
    },
  },
  {
    id: "go-to-market",
    notes:
      "¿Cómo llegamos? Paso 1: entramos por las asociaciones. Organizaciones como AMAS ya han validado Willo y quieren colaborar con nosotros para que personas con discapacidad intelectual prueben la demo. Y Plena inclusión agrupa unas 950 asociaciones. Así conseguimos los 100 primeros usuarios: 10 asociaciones, 10 personas cada una. Paso 2: un piloto con un banco, con Willo dentro de su app; esa pantalla ya está hecha. Paso 3: más bancos y Europa, porque la ley viene de una directiva europea. Las métricas aún son objetivos: 2 euros al mes por usuario, coste de captación casi cero porque entramos por las asociaciones, y que menos del 3 % lo deje cada mes.",
    render: () => {
      const card = "absolute top-[400px] flex h-[270px] w-[480px] flex-col gap-[10px] rounded-[20px] p-[36px]";
      const metrics = [
        { k: "ARPU", v: "2 €", d: "al mes por usuario" },
        { k: "CAC", v: "≈ 0 €", d: "entramos por las asociaciones" },
        { k: "Churn", v: "< 3 %", d: "lo dejan al mes" },
        { k: "LTV", v: "≈ 67 €", d: "por usuario (2\u00a0€\u00a0÷\u00a03\u00a0%)" },
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
            <p className="text-[22px] font-bold text-verde">Los 100 primeros usuarios</p>
            <p className="titular text-[38px] font-semibold leading-[1.1]">10 asociaciones × 10 personas</p>
            <p className="text-[24px] leading-[1.3] text-suave">Con AMAS y Plena inclusión, antes del piloto.</p>
          </Rise>
          {metrics.map((m, i) => (
            <Rise key={m.k} o={i + 10} className="absolute top-[700px] flex h-[220px] w-[254px] flex-col justify-center gap-[6px] rounded-[20px] bg-white p-[28px]" style={{ left: 720 + i * 270 }}>
              <p className="text-[22px] font-bold text-suave">{m.k}</p>
              <p className="titular whitespace-nowrap text-[52px] font-semibold leading-none text-verde">{m.v}</p>
              <p className="text-[22px] leading-[1.25] text-suave">{m.d}</p>
            </Rise>
          ))}
          <Foot n="12">Métricas: objetivos del equipo, aún sin datos reales. Fuentes: Plena inclusión España; Directiva (UE) 2019/882.</Foot>
        </div>
      );
    },
  },
  {
    id: "equipo",
    notes:
      "Somos seis y nos complementamos: Inés, nuestra arquitecta de machine learning; Jiawen, analista de datos; He Ye, de Informática y ADE; Nolan, de Empresa y Tecnología; XingYi, de Telecomunicación; y Anqi, de Economía. Cinco carreras distintas en un mismo equipo. ¿Por qué nosotros? Porque ya tenemos una demo que funciona, dentro de la app de MyInvestor, y hemos pensado Willo en lectura fácil desde el primer día.",
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
          <Panel />
          <div className="absolute left-[128px] top-[128px] flex w-[960px] flex-col gap-[32px]">
            <Label>El equipo</Label>
            <h2 className={T72}>
              <Words text="Somos seis, y nos complementamos." />
            </h2>
          </div>
          <div className="absolute left-[128px] top-[440px] grid w-[960px] grid-cols-2 gap-x-[48px] gap-y-[36px]">
            {team.map((p, i) => (
              <Rise key={p.n} o={i + 4} className="border-t-2 border-salvia pt-[20px]">
                <h3 className="text-[36px] font-bold leading-[1.15]">{p.n}</h3>
                <p className="mt-[6px] text-[26px] leading-[1.3] text-suave">{p.r}</p>
              </Rise>
            ))}
          </div>
          <div className="absolute left-[1280px] top-[128px] flex w-[560px] flex-col gap-[24px]">
            <Fade o={4}>
              <Label>¿Por qué nosotros?</Label>
            </Fade>
            {/* Tarjeta principal: cinco carreras distintas en un mismo equipo. */}
            <Rise o={6} className="rounded-[28px] bg-verde p-[36px] text-fondo">
              <div className="flex items-end gap-[24px]">
                <p className="titular text-[132px] font-semibold leading-[0.85] tabular-nums">
                  <Count to={5} o={7} />
                </p>
                <p className="pb-[6px] text-[32px] font-bold leading-[1.15]">carreras distintas en un mismo equipo</p>
              </div>
              <div className="mt-[28px] flex flex-wrap gap-[8px] whitespace-nowrap">
                {["Datos", "Informática y ADE", "Empresa y Tecnología", "Teleco", "Economía"].map((c) => (
                  <span key={c} className="rounded-full border-2 border-salvia/40 px-[11px] py-[4px] text-[19px] text-salvia">
                    {c}
                  </span>
                ))}
              </div>
            </Rise>
            {[
              {
                t: "Ya funciona",
                d: "Demo real dentro de la app de MyInvestor. La vais a ver en directo.",
                icon: <path d="M8 5l11 7-11 7z" fill="currentColor" />,
              },
              {
                t: "Pensado en lectura fácil",
                d: "Desde el primer día: no es un añadido, es cómo pensamos Willo.",
                icon: <path d="M5 6.5h14M5 12h14M5 17.5h9" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" fill="none" />,
              },
            ].map((b, i) => (
              <Rise key={b.t} o={i + 9} className="flex items-start gap-[24px] rounded-[24px] bg-white/80 p-[28px]">
                <span className="grid h-[64px] w-[64px] flex-none place-items-center rounded-full bg-verde text-fondo">
                  <svg width="30" height="30" viewBox="0 0 24 24" aria-hidden="true">{b.icon}</svg>
                </span>
                <div>
                  <h3 className="text-[32px] font-bold leading-[1.15]">{b.t}</h3>
                  <p className="mt-[6px] text-[24px] leading-[1.3] text-suave">{b.d}</p>
                </div>
              </Rise>
            ))}
          </div>
          <Foot n="13" />
        </div>
      );
    },
  },
  {
    id: "objetivo",
    notes:
      "Nuestro objetivo: un piloto con un banco en 2027. Para llegar, hoy os pedimos dos cosas: contactos en bancos y mentoría para preparar ese piloto. Esto es lo que viene: ya tenemos la demo; en los próximos meses, los 100 primeros usuarios con Plena inclusión; en 2027, el piloto con un banco; y después, más bancos y Europa.",
    render: () => {
      const steps = [
        { w: "Hoy", t: "Demo que funciona" },
        { w: "Próximos meses", t: "100 primeros usuarios con Plena inclusión" },
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
          <Foot n="14" />
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

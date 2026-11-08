import type { ReactNode } from "react";
import { motion } from "motion/react";
import { at, BarH, BarV, Count, DrawArrow, Emphasis, Fade, MockupIn, Rise, Words } from "./components/Anim";

const img = (name: string) => `${import.meta.env.BASE_URL}screens/${name}`;

/** dark: fondo oscuro (las partículas se pintan en crema). */
export type Slide = { id: string; notes: string; dark?: boolean; render: () => ReactNode };

/* Color de acento: solo para el dato o la idea importante. El resto, en gris salvia. */
const ACCENT = "#3E5A34";
const GREY = "#C4CEBB";

/* ---------- Piezas comunes ---------- */
const Label = ({ children, dark = false }: { children: ReactNode; dark?: boolean }) => (
  <p className={`text-[28px] font-bold ${dark ? "text-salvia" : "text-verde"}`}>{children}</p>
);

/**
 * Pie de página. La marca "Willo" lleva layoutId: está en todas las diapositivas,
 * así que no se desvanece con la transición, sino que pasa de una a otra.
 */
const Foot = ({ children, n, dark = false, center = false }: { children?: ReactNode; n?: string; dark?: boolean; center?: boolean }) => (
  <p className={`absolute bottom-[64px] left-[128px] w-[1664px] text-[24px] ${dark ? "text-salvia" : "text-suave"} ${center ? "text-center" : ""}`}>
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
const T72 = "text-[72px] font-bold leading-[1.1] tracking-[-1.2px]";
const T80 = "text-[80px] font-bold leading-[1.08] tracking-[-1.5px]";

/* ---------- Diapositivas ---------- */
export const slides: Slide[] = [
  {
    id: "portada",
    notes:
      "Hola. Somos el equipo de Willo. Willo es una app de dinero para personas con discapacidad intelectual. Se usa hablando, en lectura fácil. Su lema: tu voluntad, tu dinero.",
    render: () => (
      <div className="absolute inset-0 bg-fondo text-texto">
        {/* "willo" en partículas: lo pinta la capa de App, que acompaña toda la presentación. */}
        <Fade o={1} className="absolute left-[128px] top-[128px]">
          <Label>Una app de dinero accesible y por voz</Label>
        </Fade>
        <Rise delay={1.6} className="absolute left-[128px] top-[700px] w-[1664px] text-center">
          <p className="text-[64px] leading-[1.1] text-suave">Tu voluntad, tu dinero.</p>
        </Rise>
        <Fade delay={2} className="absolute left-[128px] top-[860px] w-[1664px] text-center">
          <p className="text-[32px] leading-[1.35] text-suave">Para personas con discapacidad intelectual. Su asistente se llama Noa.</p>
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
            <Words text="Javi tiene 34 años, trabaja en una lavandería y cobra 980 € al mes." />
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
      "Y Javi no es un caso aislado. Según el INE, solo una de cada tres personas con discapacidad intelectual usa internet de forma habitual. En la población general es el 84 por ciento. La banca digital deja fuera justo a quien más apoyo necesita.",
    render: () => (
      <div className="absolute inset-0 bg-fondo text-texto">
        <div className="absolute left-[128px] top-[128px] flex w-[1500px] flex-col gap-[40px]">
          <Label>El problema</Label>
          <h2 className={T72}>
            <Words text="Solo 1 de cada 3 personas con discapacidad intelectual usa internet de forma habitual." />
          </h2>
        </div>
        {/* El dato importante en acento; la comparación en gris. */}
        <Fade o={6} className="absolute left-[128px] top-[600px]">
          <p className="text-[32px] font-bold">Personas con discapacidad intelectual</p>
        </Fade>
        <BarH o={6} width={491} height={96} color={ACCENT} className="absolute left-[128px] top-[654px]" />
        <Fade o={10} className="absolute left-[651px] top-[668px]">
          <p className="whitespace-nowrap text-[56px] font-bold text-verde">1 de cada 3</p>
        </Fade>
        <Fade o={7} className="absolute left-[128px] top-[790px]">
          <p className="text-[32px] text-suave">Población general</p>
        </Fade>
        <BarH o={7} width={1250} height={96} color={GREY} className="absolute left-[128px] top-[844px]" />
        <p className="absolute left-[1410px] top-[858px] whitespace-nowrap text-[56px] font-bold tabular-nums text-suave">
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
        <Rise o={4} className="absolute left-[1366px] top-[120px]">
          <img src={img("03-respuesta.png")} alt="Noa responde: si compras la entrada, te quedan 165 euros. Tú decides." className="h-[840px] w-[388px] rounded-[31px] object-contain" />
        </Rise>
        <Emphasis o={10} className="absolute left-[128px] top-[670px] origin-left">
          <p className="text-[120px] font-bold leading-[1.05] tracking-[-3px] text-verde">Tú decides.</p>
        </Emphasis>
        <Foot n="04" />
      </div>
    ),
  },
  {
    id: "demo",
    dark: true,
    notes:
      "Vamos a verlo en directo con los móviles de Javi y de su hermana Ana. Seguid el guion de la demo: entrada del concierto, multa de aparcamiento, Bizum de Carlos e informe anual. Si falla la conexión, pasad al vídeo de respaldo: [enlace al vídeo].",
    render: () => (
      <div className="absolute inset-0 bg-verde text-fondo">
        <div className="absolute left-[128px] top-[128px] flex w-[1040px] flex-col gap-[40px]">
          <Label dark>Demo en directo · 3 minutos</Label>
          <h2 className={T80}>
            <Words text="Un mes de Javi: una entrada, una multa y un Bizum sospechoso." />
          </h2>
        </div>
        <MockupIn o={2} className="absolute left-[1305px] top-[100px]">
          <img src={img("02-escucha.png")} alt="Pantalla Noa te escucha, con el botón del micrófono" className="h-[880px] w-[407px] rounded-[32px] object-contain" />
        </MockupIn>
        <Fade o={9} className="absolute left-[128px] top-[800px] w-[960px]">
          <p className="text-[40px] leading-[1.3] text-salvia">Fijaos en una cosa: Noa explica, pero los botones los pulsa Javi.</p>
        </Fade>
        <Foot n="05" dark />
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
          <Foot n="06" />
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
          <Foot n="07">Cada nivel incluye el anterior. Ninguno puede bloquear un pago. Basado en la Ley 8/2021.</Foot>
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
            <p className="text-[24px] font-bold text-salvia">Backend propio · FastAPI</p>
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
            <p className="text-[28px] leading-[1.3] text-suave">App web instalable (PWA), sin tienda de apps · Desplegada en Render · Se guardan los datos, nunca las fotos.</p>
          </Fade>
          <Foot n="08" />
        </div>
      );
    },
  },
  {
    id: "negocio",
    notes:
      "¿Quién paga? El banco, por cada usuario activo. La Ley 11/2023 obliga a que los servicios bancarios sean accesibles, y Willo le ayuda a cumplirla. En España viven más de 400.000 personas con discapacidad intelectual y del desarrollo. [Contad aquí en qué punto está la validación con Plena inclusión y fundaciones.]",
    render: () => {
      const items = [
        { t: "Cuota por usuario activo", d: "El banco paga por cada persona que usa Willo.", accent: true },
        { t: "Ley 11/2023", d: "Los servicios bancarios tienen que ser accesibles." },
        { t: "Ley 8/2021", d: "Apoyar a la persona, sin decidir por ella." },
      ];
      return (
        <div className="absolute inset-0 bg-fondo text-texto">
          <div className="absolute left-[128px] top-[128px] flex w-[1500px] flex-col gap-[32px]">
            <Label>Modelo de negocio</Label>
            <h2 className={T72}>
              <Words text="Paga el banco, porque la ley ya le pide ser accesible." />
            </h2>
          </div>
          <div className="absolute left-[128px] top-[470px] flex w-[784px] flex-col gap-[28px]">
            {items.map((it, i) => (
              <Rise key={it.t} o={i + 6} className={i ? "border-t-2 border-salvia pt-[28px]" : ""}>
                <h3 className={`text-[40px] font-bold ${it.accent ? "text-verde" : ""}`}>{it.t}</h3>
                <p className="mt-[8px] text-[28px] leading-[1.3] text-suave">{it.d}</p>
              </Rise>
            ))}
          </div>
          <div className="absolute left-[1008px] top-[470px] flex h-[450px] w-[784px] flex-col justify-center gap-[16px]">
            <p className="whitespace-nowrap text-[160px] font-bold leading-none tracking-[-4px] tabular-nums text-verde">
              <Count to={400000} prefix="+" o={6} />
            </p>
            <Fade o={10}>
              <p className="text-[32px] leading-[1.3]">personas con discapacidad intelectual y del desarrollo viven en España.</p>
            </Fade>
            <Fade o={11}>
              <p className="text-[26px] leading-[1.3] text-suave">Validación con Plena inclusión y fundaciones.</p>
            </Fade>
          </div>
          <Foot n="09">Fuente de la cifra: Plena inclusión España.</Foot>
        </div>
      );
    },
  },
  {
    id: "cierre",
    dark: true,
    notes: "Willo no decide por nadie. Explica, avisa y deja decidir. Willo: tu voluntad, tu dinero. Gracias.",
    render: () => (
      <div className="absolute inset-0 bg-verde text-fondo">
        {/* "willo" vuelve a formarse aquí con las partículas de la capa de App. */}
        <h1 className="absolute left-[128px] top-[640px] w-[1664px] text-center text-[96px] font-bold leading-[1.05] tracking-[-3px]">
          <Words text="Tu voluntad, tu dinero." delay={1.6} />
        </h1>
        <p className="absolute left-[128px] top-[790px] w-[1664px] text-center text-[40px] leading-[1.3] text-salvia">
          <Words text="Nunca compra. Nunca paga. Nunca bloquea." delay={2.1} />
        </p>
        <Foot dark center>
          [Nombres del equipo] · [enlace a la demo]
        </Foot>
      </div>
    ),
  },
];

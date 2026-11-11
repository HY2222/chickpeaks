# Willo · Guion del pitch (actualizado 11 nov 2026)

Es el mismo texto que las notas del ponente (tecla **N** en la presentación). Tiempos a ritmo tranquilo, unas 145 palabras por minuto.

**Duración total: unos 8 min de pitch + 3 min de demo ≈ 11 min.** Si os dan menos tiempo, mirad "Si hay que recortar" al final.

---

## 1 · Portada (≈ 15 s)
Hola. Somos el equipo de Willo. Willo es el modo fácil de tu banco, para personas con discapacidad intelectual. Se usa hablando, en lectura fácil. Su lema: tu voluntad, tu dinero.

## 2 · Javi (≈ 20 s)
Este es Javi. Tiene 34 años, trabaja en una lavandería y cobra 980 euros al mes. Quiere decidir sobre su dinero, como cualquiera. Pero la app de su banco no está hecha para él. Así que pregunta a su familia para todo, o se arriesga a que le engañen.

## 3 · El problema (≈ 25 s)
Y Javi no es un caso aislado. Según el INE, solo una de cada tres personas con discapacidad intelectual usa internet de forma habitual. En la población general es el 84 por ciento. La banca digital deja fuera justo a quien más apoyo necesita. Y aquí está la oportunidad: desde junio de 2025, la ley obliga a los bancos a ser accesibles.

## 4 · La solución (≈ 20 s)
Por eso hemos creado Willo. Es una app de dinero que se usa hablando, con frases cortas y cifras en euros. Su asistente se llama Noa. Noa hace la cuenta y la explica. Pero nunca decide por la persona: siempre termina con "Tú decides".

## 5 · El mercado (≈ 40 s) · CAMBIADA
Nuestro mercado.
**TAM, Europa:** hay casi 7 millones de personas con discapacidad intelectual, y la directiva europea de accesibilidad obliga a todos los bancos de la UE. Son unos 207 millones de euros al año.
**SAM, España:** según el IMSERSO, 157.895 personas con discapacidad intelectual o del desarrollo reconocida; unos 4,7 millones al año.
**SOM:** empezamos por las personas que ya están en asociaciones y organizaciones como AMAS o Plena inclusión. Plena inclusión apoya a 150.000 personas; queremos llegar a 13.816, menos de 1 de cada 10. Eso son unos 410.000 euros al año, a 2,99 euros al mes por usuario, IVA incluido.

## 6 · La competencia (≈ 40 s)
Ya hay empresas trabajando en esto. CaixaBank tiene una cuenta con persona de apoyo y una guía en lectura fácil, pero la app no te habla ni te explica cada pago. SpendAble, en Australia, es una tarjeta con app para personas con discapacidad intelectual, pero los presupuestos los pone la persona de apoyo. True Link, en Estados Unidos, protege de estafas bloqueando: decide el cuidador. Y Blue, de BBVA, habla con IA, pero no en lectura fácil ni con apoyos. Willo es el único que junta todo y deja decidir a la persona.

## 7 · Demo en directo (3 min)
Vamos a verlo en directo con los móviles de Javi y de su hermana Ana. Empezamos en la app de MyInvestor: Willo es un botón más, el modo fácil.
→ Seguid `docs/diseno/guion-demo.md` (rama `main`): entrada del concierto, multa, Bizum de Carlos e informe. Si falla internet, vídeo de reserva.

## 8 · Lo que habéis visto (≈ 25 s)
Resumen de lo que acabáis de ver. Uno: Noa hace la cuenta y dice "Tú decides". Dos: Noa lee una multa; Javi confirma los datos y la foto no se guarda. Tres: ante un Bizum raro, Willo hace una pausa y explica por qué parece una estafa, pero no bloquea nada. Cuatro: el informe para el juez sale en un clic.

## 9 · Círculo de apoyo (≈ 30 s)
En vez de un control parental, Willo tiene un círculo de apoyo. Javi elige quién le apoya y cuánto, con nombres fáciles: Solo yo, Ver, Apoyar, Guardar y Representar. Ver y Apoyar los da y los quita Javi. Ana, su hermana, está en Guardar: recibe avisos de estafa al momento y saca el informe anual para el juez. Esto sigue la Ley 8/2021: apoyar a la persona, no sustituirla.

## 10 · Cómo funciona (≈ 25 s)
La clave técnica: la IA nunca calcula ni decide. ElevenLabs da la voz y la conversación de Noa, y el dictado con Scribe. Nuestro backend en FastAPI hace todas las cuentas y las reglas antiestafa. Claude lee los documentos y lo escribe en lectura fácil. Y al final decide Javi. Es una PWA desplegada en Render, sin tienda de apps.

## 11 · Lectura fácil, medida (≈ 35 s)
¿Cómo sabemos que Noa explica fácil? Lo medimos. El índice Fernández-Huerta mide lo fácil que es leer un texto en español, de 0 a 100; de 80 para arriba es fácil. En nuestros tres ejemplos, una carta falsa de la Seguridad Social pasa de 22, muy difícil, a 98 con Noa. La multa, de 44 a 87. Y la factura de la luz, de 26 a 100.

## 12 · Modelo de negocio (≈ 35 s) · CAMBIADA
¿Quién paga? El banco, no la persona. Es un SaaS B2B2C: el banco paga cada mes por cada usuario activo, y se lo da gratis a sus clientes con discapacidad intelectual. ¿Por qué paga? Porque la Ley 11/2023 ya le obliga a ser accesible.
El precio de referencia es **2,99 euros al mes por usuario, IVA incluido**. Va por tramos: cuantos más usuarios, más barato le sale cada uno nuevo, de 3,49 a 2,49. Y depende del uso: incluye una media de 3 conversaciones al día; cada una extra, 2 céntimos.

## 13 · Ingresos y costes (≈ 40 s) · NUEVA
Y los números salen. Con nuestro SOM, 13.816 usuarios a 2,99 euros, facturamos unos 41.300 euros al mes; sin IVA, 34.140.
Los costes: la IA es el más grande, unos 15.100 euros al mes, contando 3 conversaciones al día por usuario a poco más de 1 céntimo cada una. Mantenimiento: 30 horas al mes a 40 euros la hora, 1.200 euros. Y el alojamiento con Vercel y Supabase, unos 40 euros. En total, unos 16.360 euros.
Nos quedan unos **17.780 euros al mes: un margen operativo del 52 por ciento**. Y cubrimos los costes a partir de unos 900 usuarios.

## 14 · Go to market (≈ 45 s) · CAMBIADA (métricas)
¿Cómo llegamos? Paso 1: entramos por las asociaciones. AMAS ya ha validado Willo y quiere que sus usuarios prueben la demo, y Plena inclusión agrupa unas 950 asociaciones. Así conseguimos los 100 primeros usuarios: 10 asociaciones, 10 personas cada una. Paso 2: un piloto con un banco, con Willo dentro de su app; esa pantalla ya está hecha. Paso 3: más bancos y Europa, porque la ley viene de una directiva europea.
Nuestros objetivos: 2,47 euros al mes por usuario sin IVA, captación casi gratis gracias a las asociaciones y menos de un 3 % de bajas al mes. Así, cada usuario nos deja unos 46 euros de margen.

## 15 · Equipo (≈ 15 s)
Somos seis y nos complementamos: Inés, nuestra arquitecta de machine learning; Jiawen, analista de datos; He Ye, de Informática y ADE; Nolan, de Empresa y Tecnología; XingYi, de Telecomunicación; y Anqi, de Economía.

## 16 · Objetivo (≈ 25 s)
Nuestro objetivo: un piloto con un banco en 2027. Para llegar, hoy os pedimos dos cosas: contactos en bancos y mentoría para preparar ese piloto. Ya tenemos la demo; en los próximos meses, los 100 primeros usuarios con AMAS; en 2027, el piloto con un banco; y después, más bancos y Europa.

## 17 · Cierre (≈ 5 s)
Willo no decide por nadie. Explica, avisa y deja decidir. Willo: tu voluntad, tu dinero. Gracias.

---

## Si hay que recortar
- **A 5 min de pitch:** quitad la 8 (lo acaban de ver en la demo), la 11 (decid solo "de 22 a 98 en lectura fácil" en la 10) y la 15 (el equipo se presenta en la portada).
- **En la 13**, quedaos con una frase: "Ingresamos 34.000 euros al mes, gastamos 16.000, sobre todo en IA: un margen del 52 % y rentables desde unos 900 usuarios."

---

## Preguntas que puede hacer el jurado

**¿El 2,99 € lleva IVA? A un banco se le suele dar el precio sin IVA.**
Sí, lleva IVA. Sin IVA son 2,47 €, y con esa cifra están hechos todos los ingresos y el margen. Si el jurado es de negocio, decid "2,47 € más IVA".

**¿De dónde sale el SOM de 13.816?**
Son las personas que ya van a asociaciones. Plena inclusión apoya a unas 150.000; 13.816 es menos de 1 de cada 10, y el 8,75 % de las 157.895 de España. Es una hipótesis del equipo.

**¿Y el TAM de 7 millones?**
Es una estimación publicada en *European Psychiatry* (2020): entre el 1 y el 2 % de la población. Usamos Europa porque la Directiva (UE) 2019/882 obliga a todos los bancos de la UE.

**La IA es el 92 % de los costes. ¿Qué pasa si se usa más?**
Por eso el precio incluye 3 conversaciones al día de media, y cada una extra cuesta 0,02 € (a nosotros, unos 0,012 €). Además, el coste por conversación de los modelos baja cada año. Cada usuario nos cuesta unos 1,09 € al mes en IA.

**¿Por qué tramos?**
Funcionan como el IRPF, pero al revés: cada usuario paga el precio de su tramo, así que al banco nunca le sale más caro crecer. Solo cuentan los usuarios que usan Willo ese mes.

**40 € de infraestructura parece poco para 13.816 usuarios.**
Son los planes básicos de Vercel y Supabase de hoy. Con más uso habrá que subir de plan, pero aunque fueran unos cientos de euros, el margen seguiría por encima del 50 %.

**¿Cómo calculáis el LTV?**
Margen por usuario (2,47 € − 1,09 € de IA = 1,38 € al mes) ÷ 3 % de bajas al mes ≈ 46 €. Como la captación es casi gratis, cada usuario es rentable desde el primer mes.

**¿Cuándo sois rentables?**
Los costes fijos son unos 1.240 € al mes (mantenimiento e infraestructura). Con 1,38 € de margen por usuario, se cubren con unos 900 usuarios.

---

## Cifras de referencia (para no equivocarse)

| Concepto | Cifra |
|---|---|
| Precio | 2,99 €/usuario/mes con IVA = 2,47 € sin IVA |
| Tramos (con IVA) | hasta 2.000: 3,49 € · 2.001–10.000: 2,99 € · más de 10.000: 2,49 € |
| Uso incluido | 3 conversaciones al día de media; extra 0,02 € cada una |
| Facturación SOM | 41.309,84 €/mes con IVA · 34.140,36 € sin IVA |
| IA | 15.116,55 €/mes (1.243.440 conversaciones × 0,0136 $, 1 $ ≈ 0,89 €) |
| Mantenimiento | 1.200 €/mes (30 h × 40 €) |
| Infraestructura | 40,23 €/mes (Vercel + Supabase) |
| Costes totales | 16.356,78 €/mes |
| Resultado operativo | 17.783,58 €/mes · margen 52,1 % |
| Ingresos al año (sin IVA) | TAM ≈ 207 M€ · SAM ≈ 4,7 M€ · SOM ≈ 410.000 € |
| LTV | ≈ 46 € de margen |
| Punto de equilibrio | ≈ 900 usuarios |

Fuentes: *European Psychiatry* (2020), "Are we training psychiatrists to develop skills in intellectual disability psychiatry?"; IMSERSO (2024); Plena inclusión España; Ley 11/2023; Directiva (UE) 2019/882.

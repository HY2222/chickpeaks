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
**TAM, Europa:** hay casi 7 millones de personas con discapacidad intelectual, y la directiva europea de accesibilidad obliga a todos los bancos de la UE. Son unos 200 millones de euros al año.
**SAM, España:** según el IMSERSO, 157.895 personas con discapacidad intelectual o del desarrollo reconocida; unos 4,5 millones al año.
**SOM:** empezamos por las personas que ya están en asociaciones y organizaciones como AMÁS o Plena inclusión. Plena inclusión apoya a 150.000 personas; queremos llegar a 13.816, menos de 1 de cada 10. Eso son unos 416.000 euros al año.

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

## 12 · Modelo de negocio (≈ 40 s) · CAMBIADA
¿Quién paga? El banco, no la persona. Es un SaaS B2B2C: el banco se lo da gratis a sus clientes con discapacidad intelectual. ¿Por qué paga? Porque la Ley 11/2023 ya le obliga a ser accesible.
Cobramos en tres partes. Una **implantación de 15.000 euros**, una sola vez: integrar Willo en su app, con su marca, y formar a su equipo. Una **cuota base de 1.500 euros al mes**, que cubre la plataforma y el soporte. Y **2,40 euros al mes por cada usuario activo**: solo cuenta quien usa Willo ese mes. Así el banco paga según el uso real. Por ejemplo, un banco con 13.816 usuarios paga unos 34.700 euros al mes.

## 13 · Ingresos y costes (≈ 40 s) · NUEVA
Y los números salen. Con nuestro SOM, un banco con 13.816 usuarios nos paga 1.500 euros de base y 2,40 euros por usuario: unos 34.700 euros al mes.
Los costes: la IA es el más grande, unos 15.100 euros al mes, contando 3 conversaciones al día por usuario a poco más de 1 céntimo cada una. Mantenimiento: 30 horas al mes a 40 euros la hora, 1.200 euros. Y el alojamiento en Vercel y Render, unos 24 euros. En total, unos 16.340 euros.
Nos quedan unos **18.320 euros al mes: un margen operativo del 53 por ciento**. Y la cuota base ya cubre nuestros costes fijos: cada usuario nuevo nos deja 1,31 euros de margen al mes.

## 14 · Go to market (≈ 45 s) · CAMBIADA (métricas)
¿Cómo llegamos? Paso 1: entramos por las asociaciones. AMÁS ya ha validado Willo y quiere que sus usuarios prueben la demo. Y ese es nuestro canal: Plena inclusión agrupa unas 950 asociaciones que apoyan a 150.000 personas. Paso 2: un piloto con un banco, con Willo dentro de su app; esa pantalla ya está hecha. Paso 3: más bancos y Europa, porque la ley viene de una directiva europea.
En números: cada banco paga 15.000 euros al empezar, 1.500 euros al mes de base y 2,40 euros por usuario activo. Y captar usuarios nos cuesta casi cero, porque nos llegan por las asociaciones.

## 15 · Equipo (≈ 15 s)
Somos seis y nos complementamos: Inés, nuestra arquitecta de machine learning; Jiawen, analista de datos; He, de Informática y ADE; Nolan, de Empresa y Tecnología; Xingyi, de Telecomunicación; y Anqi, de Economía.

## 16 · Cierre (≈ 10 s) · CAMBIADA
Nuestro objetivo: contactos en bancos y mentoría para el piloto. Willo no decide por nadie. Explica, avisa y deja decidir. Willo: tu voluntad, tu dinero. Gracias.

---

## Si hay que recortar
- **A 5 min de pitch:** quitad la 8 (lo acaban de ver en la demo), la 11 (decid solo "de 22 a 98 en lectura fácil" en la 10) y la 15 (el equipo se presenta en la portada).
- **En la 13**, quedaos con una frase: "Con 13.816 usuarios ingresamos unos 34.700 euros al mes y gastamos 16.300, sobre todo en IA: un margen del 53 %. La cuota base cubre los costes fijos, y cada usuario nuevo suma margen."

---

## Preguntas que puede hacer el jurado

**¿Por qué una cuota base y además un precio por usuario?**
La cuota base le da al banco un coste mínimo previsible y a nosotros nos cubre los costes fijos (mantenimiento e infraestructura, unos 1.224 € al mes). El precio por usuario sigue el uso real, igual que nuestro coste principal, la IA. Así nunca perdemos dinero con un banco que crece.

**¿De dónde salen los precios?**
Son una propuesta nuestra, pero siguen el mercado. FinCell (app de banca de marca blanca) cobra igual: alta, cuota fija y una cuota por usuario activo, desde 1.000 € al mes. Crassula cobra 20.000 € de alta y 8.000 € al mes, y Synctera, de 5.000 a 25.000 $ de alta: nuestros 15.000 € están en medio. Un asistente de IA para bancos en AWS cobra unos 0,35 $ por conversación; nosotros, unos 0,03 €.

**¿Cuánto os cuesta conseguir un banco?**
Ese es el CAC (coste de adquisición de cliente) que más importa, porque quien paga es el banco. Todavía no lo sabemos: por eso pedimos contactos en bancos y mentoría. Lo que sí es casi gratis es conseguir usuarios, porque nos llegan por las asociaciones.

**¿Los precios llevan IVA?**
No. En B2B se habla siempre sin IVA.

**¿De dónde sale el SOM de 13.816?**
Son las personas que ya van a asociaciones. Plena inclusión apoya a unas 150.000; 13.816 es menos de 1 de cada 10, y el 8,75 % de las 157.895 de España. Es una hipótesis del equipo.

**¿Y el TAM de 7 millones?**
Es una estimación publicada en *European Psychiatry* (2020): entre el 1 y el 2 % de la población. Usamos Europa porque la Directiva (UE) 2019/882 obliga a todos los bancos de la UE. Los euros de TAM y SAM están calculados a 2,40 € por usuario al mes.

**La IA es el 92 % de los costes. ¿Qué pasa si se usa más?**
Cada usuario nos cuesta unos 1,09 € al mes en IA (3 conversaciones al día) y nos paga 2,40 €. Si un usuario usara mucho más, lo cubriríamos con un límite de uso razonable en el contrato. Y el coste por conversación de los modelos baja cada año.

**¿Qué incluye la implantación?**
Integrar Willo en la app del banco (esa pantalla ya está hecha en la demo), adaptarlo a su marca y formar a su equipo.

**¿Cuándo sois rentables?**
Los costes fijos son unos 1.224 € al mes, y la cuota base de un solo banco (1.500 €) ya los cubre. A partir de ahí, cada usuario deja 1,31 € de margen al mes (2,40 € − 1,09 € de IA).

**¿Dónde está alojada la app?**
El backend, en Render; la parte web, en Vercel. Hoy son unos 24 € al mes; con más uso habrá que subir de plan, pero el margen seguiría por encima del 50 %.

---

## Cifras de referencia (para no equivocarse)

| Concepto | Cifra |
|---|---|
| Implantación | 15.000 € por banco, una sola vez (sin IVA) |
| Cuota base | 1.500 € al mes por banco (sin IVA) |
| Por usuario activo | 2,40 € al mes (sin IVA) |
| Ingresos SOM | 34.658,40 €/mes (1.500 + 13.816 × 2,40) · ≈ 416.000 €/año |
| IA | 15.116,55 €/mes (1.243.440 conversaciones × 0,0136 $, 1 $ ≈ 0,89 €) · ≈ 1,09 € por usuario |
| Mantenimiento | 1.200 €/mes (30 h × 40 €) |
| Infraestructura | 24,14 €/mes (Vercel 20 $ + Render 7 $) |
| Costes totales | 16.340,69 €/mes |
| Resultado operativo | 18.317,71 €/mes · margen 52,9 % |
| Margen por usuario | 1,31 € al mes (2,40 € − 1,09 €) |
| Ingresos al año | TAM ≈ 200 M€ · SAM ≈ 4,5 M€ (a 2,40 €/usuario) · SOM ≈ 416.000 € |

Fuentes de precios: FinCell (Software Advice), Crassula (crassula.io/prices), Synctera (CostBench), BankAssist (AWS Marketplace).

Fuentes: *European Psychiatry* (2020), "Are we training psychiatrists to develop skills in intellectual disability psychiatry?"; IMSERSO (2024); Plena inclusión España; Ley 11/2023; Directiva (UE) 2019/882.

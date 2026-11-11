#set page(
  paper: "us-letter",
  margin: (x: 2cm, top: 2.5cm, bottom: 2.2cm),
  header: context {
    if here().page() > 1 [
      #text(9pt, fill: rgb("#7a6b5f"))[
        *Torre Satori PMS* · Guión Maestro de Sustentación (ITIL 4 — Actividad 5)
        #h(1fr)
        _Hotel Torre Satori, Sevilla_
      ]
      #v(-4pt)
      #line(length: 100%, stroke: 0.5pt + rgb("#d4a373"))
    ]
  },
  footer: context [
    #line(length: 100%, stroke: 0.5pt + rgb("#e0d6cc"))
    #v(2pt)
    #text(8.5pt, fill: rgb("#9c8e82"))[
      Proyecto Integrador II · Universidad Icesi
      #h(1fr)
      Página #here().page() de #counter(page).final().at(0)
    ]
  ]
)

#set text(
  font: "Liberation Sans",
  size: 10pt,
  lang: "es",
  fill: rgb("#261d19")
)

#set par(justify: true, leading: 0.65em)

// Estilos de ponentes
#let badge(speaker, role, col) = {
  rect(
    fill: col.lighten(85%),
    stroke: 0.8pt + col,
    radius: 3pt,
    inset: (x: 6pt, y: 3pt),
    outset: 0pt,
  )[#text(size: 8.5pt, weight: "bold", fill: col)[#speaker · #role]]
}

#let juan_jose(body) = {
  block(
    width: 100%,
    stroke: (left: 3pt + rgb("#1e40af")),
    inset: (left: 10pt, y: 4pt),
    fill: rgb("#f0f5ff"),
    radius: (right: 4pt),
  )[
    #badge("JUAN JOSÉ ARIAS", "Product Owner", rgb("#1e40af")) \
    #v(2pt)
    #body
  ]
}

#let esteban(body) = {
  block(
    width: 100%,
    stroke: (left: 3pt + rgb("#15803d")),
    inset: (left: 10pt, y: 4pt),
    fill: rgb("#f0fdf4"),
    radius: (right: 4pt),
  )[
    #badge("ESTEBAN GUARÍN", "Scrum Master / ITIL Lead", rgb("#15803d")) \
    #v(2pt)
    #body
  ]
}

#let juan_felipe(body) = {
  block(
    width: 100%,
    stroke: (left: 3pt + rgb("#b45309")),
    inset: (left: 10pt, y: 4pt),
    fill: rgb("#fffbeb"),
    radius: (right: 4pt),
  )[
    #badge("JUAN FELIPE GARZÓN", "Development Team / Motores Críticos", rgb("#b45309")) \
    #v(2pt)
    #body
  ]
}

#let slide_header(num, title, time) = {
  v(8pt)
  rect(
    fill: rgb("#2b1e17"),
    width: 100%,
    radius: 4pt,
    inset: (x: 10pt, y: 6pt),
  )[
    #grid(
      columns: (1fr, auto),
      align: (left + horizon, right + horizon),
      text(weight: "bold", fill: white, size: 10.5pt)[Diapositiva #num: #title],
      text(weight: "bold", fill: rgb("#f5dfc6"), size: 9pt)[⏱ #time]
    )
  ]
  v(2pt)
}

// ── PORTADA ────────────────────────────────────────────────────────────
#align(center)[
  #v(10pt)
  #text(size: 11pt, weight: "bold", fill: rgb("#c48b59"), tracking: 2pt)[HOTEL TORRE SATORI · SEVILLA, VALLE DEL CAUCA] \
  #v(4pt)
  #text(size: 20pt, weight: "black", fill: rgb("#261d19"))[Torre Satori PMS] \
  #text(size: 13pt, weight: "bold", fill: rgb("#7a3e1d"))[Guión Maestro de Sustentación Colegiada] \
  #text(size: 10pt, style: "italic", fill: rgb("#7a6b5f"))[Entregable de Transición del Servicio y Operaciones (ITIL 4) — Actividad 5] \
  #v(8pt)
  #line(length: 40%, stroke: 1.5pt + rgb("#d4a373"))
  #v(8pt)
]

#rect(
  fill: rgb("#faf6f0"),
  stroke: 1pt + rgb("#e2d5c5"),
  radius: 6pt,
  width: 100%,
  inset: 10pt,
)[
  #grid(
    columns: (1fr, 1fr, 1fr),
    align: center,
    [
      *Duración Total*\
      ~18 a 20 minutos\
      _(+ sesión de preguntas)_
    ],
    [
      *Diapositivas Soporte*\
      36 láminas interactivas\
      `index.html` (SVG 16:9)
    ],
    [
      *Stack Tecnológico*\
      FastAPI · Postgres 16 GiST\
      React 18 · n8n · Alembic
    ]
  )
]

#v(8pt)

== 1. Matriz de Reparto de Roles y Tiempos

#table(
  columns: (1.4fr, 1.3fr, 1.5fr, 0.8fr, 0.6fr),
  fill: (col, row) => if row == 0 { rgb("#322621") } else if calc.even(row) { rgb("#fcfaf7") } else { white },
  stroke: 0.5pt + rgb("#d9cbbe"),
  inset: 6pt,
  align: (left, left, left, center, center),
  [#text(fill: white, weight: "bold")[Integrante]],
  [#text(fill: white, weight: "bold")[Rol en Proyecto]],
  [#text(fill: white, weight: "bold")[Bloques Asignados]],
  [#text(fill: white, weight: "bold")[Diapositivas]],
  [#text(fill: white, weight: "bold")[Tiempo]],

  [*Juan José Arias G.*], [Product Owner], [Acto 1 (Negocio/Alcance) y Acto 5 (Go-Live/Cierre/ROI)], [01–08, 31–36], [~7 min],
  [*Esteban Guarín V.*], [Scrum Master / ITIL], [Acto 2 (Despliegue/Cambios) y Acto 4 (Soporte/SLA)], [09–19, 26–30], [~7 min],
  [*Juan Felipe Garzón*], [Dev Team / Ingeniero], [Acto 3 (Validación, Pruebas y Candado GiST RN-02)], [20–25], [~5 min],
)

#v(10pt)
#line(length: 100%, stroke: 0.5pt + rgb("#d4a373"))
#v(6pt)

== ACTO 1: INTRODUCCIÓN, DIAGNÓSTICO Y ALCANCE (00:00 – 03:30)
#text(size: 9pt, fill: rgb("#7a6b5f"))[*Ponente Principal:* Juan José Arias Gallego · *Objetivo:* Enmarcar el negocio, los dolores del hotel y la propuesta de valor.]

#slide_header("01 / 36", "Portada Institucional", "00:00 – 00:30 (30 s)")
_Acción visual: Proyectar la lámina inicial con la tipografía oficial SatoriPMS._
#juan_jose[
  "Muy buenos días, estimado profesor y miembros del jurado. Hoy sustentamos la culminación formal de la *Actividad 5: Transición del Servicio y Operaciones bajo el marco ITIL 4* para el sistema *Torre Satori PMS*.

  Hotel Torre Satori es un hotel boutique de 9 habitaciones ubicado en Sevilla, Valle del Cauca. Nuestro reto fue transicionar un servicio digital unificado que sincroniza en tiempo real el canal de WhatsApp para los huéspedes con la gestión web de recepción y cafetería, garantizando cero colisiones de reserva y máxima eficiencia operativa."
]

#slide_header("02 / 36", "Equipo de Dirección e Ingeniería", "00:30 – 00:55 (25 s)")
_Acción visual: Señalar las tres columnas con fotos y responsabilidades._
#juan_jose[
  "Para esta transición, la gobernanza del equipo se estructuró en tres roles unívocos:
  *Esteban Guarín Valencia*, como Scrum Master y líder ITIL, a cargo del plan de despliegue, control de cambios y SLAs;
  *Juan Felipe Garzón Ruiz*, en el Development Team, responsable de la arquitectura modular, base de datos relacional y el motor de concurrencia;
  y quien les habla, *Juan José Arias*, como Product Owner, enfocado en el modelo de negocio, criterios UAT y dictamen final de transición."
]

#slide_header("03 / 36", "Diagnóstico: Los 8 Problemas del Hotel", "00:55 – 01:30 (35 s)")
_Acción visual: Recorrer las 8 tarjetas de dolores operativos del hotel._
#juan_jose[
  "Previo al proyecto, Torre Satori operaba con cuadernos y hojas de cálculo. Esto detonaba 8 problemas críticos:
  Primero, riesgo constante de *sobreventa* entre WhatsApp y mostrador; segundo, pérdida de ventas nocturnas por falta de atención inmediata 24/7; fugas de dinero por cobros manuales erróneos; cuentas de café abiertas sin conciliar; y una carga de tareas manuales repetitivas que saturaba al personal."
]

#slide_header("04 / 36", "Del Problema a la Solución de Ingeniería", "01:30 – 02:00 (30 s)")
_Acción visual: Destacar los paneles horizontales con el impacto técnico directo._
#juan_jose[
  "Frente a ello, implementamos soluciones de ingeniería definitivas:
  Para eliminar el overbooking: un *candado atómico relacional en PostgreSQL 16* con restricción GiST y expiración inline, blindando el 0.0% de colisiones.
  Para capturar ventas 24/7: un chatbot en WhatsApp Cloud API orquestado por n8n con IA asistida para recomendaciones locales.
  Y para el control de caja: una SPA en React 18 que unifica reservas y consumos de café en el folio de la habitación."
]

#slide_header("05 / 36", "Hoja de Ruta: Los 8 Componentes ITIL 4", "02:00 – 02:25 (25 s)")
_Acción visual: Mostrar la matriz de 8 bloques de la transición de servicio._
#juan_jose[
  "Siguiendo ITIL 4, estructuramos este informe en 8 componentes de servicio: Definición y alcance, Plan de despliegue, Autorización de cambios, Validación y pruebas, Operación y soporte, Gestión del conocimiento, Comunicación y go-live, y Dictamen de cierre. Veamos el alcance de la versión entregada."
]

#slide_header("06 a 08 / 36", "Componente 1: Definición, Funcionalidades y Entorno", "02:25 – 03:30 (65 s)")
_Acción visual: Transicionar entre Slide 6 (Propósito), Slide 7 (Entregables) y Slide 8 (Límites y Marcha Blanca)._
#juan_jose[
  "En esta versión final `1.0.0-FINAL`, entregamos 4 módulos nucleares: cotización y bloqueo temporal de cuartos, catálogo dinámico de tarifas y eventos especiales, comandas y tienda de Salgados Café, y auditoría inmutable de transacciones.
  Como exclusión formal acordada con el cliente, dejamos fuera la pasarela de dispersión bancaria directa (manejando comprobantes validados en recepción) y la cancelación automática de No-Show a mediodía. El sistema opera contenerizado en un servidor VPS con TLS 1.3.
  Le cedo la palabra a Esteban Guarín para detallar el Plan de Despliegue y los Cambios."
]

#pagebreak()

== ACTO 2: PLAN DE DESPLIEGUE, ARQUITECTURA Y GESTIÓN DE CAMBIOS (03:30 – 09:30)
#text(size: 9pt, fill: rgb("#7a6b5f"))[*Ponente Principal:* Esteban Guarín Valencia · *Objetivo:* Demostrar rigurosidad de despliegue, infraestructura y gobernanza CAB.]

#slide_header("09 / 36", "Componente 2.1: Arquitectura y Componentes Desplegados", "03:30 – 04:15 (45 s)")
_Acción visual: Explicar las 4 capas del diagrama de arquitectura hexagonal._
#esteban[
  "Muchas gracias, Juan José. La arquitectura de Torre Satori PMS es un *monolito modular hexagonal*:
  Los huéspedes interactúan mediante WhatsApp Cloud API conectado a n8n, mientras recepción opera una SPA en React 18 con Tailwind. Ambos canales consumen exactamente la misma API REST construida sobre *FastAPI con Python 3.12 y servidor ASGI Uvicorn*.
  En la persistencia, una base de datos *PostgreSQL 16 Alpine* maneja tanto el candado temporal de 15 minutos mediante expiración inline y APScheduler, como la restricción física `EXCLUDE USING gist`, garantizando aislamiento ACID estricto sin dependencias externas innecesarias."
]

#slide_header("10 / 36", "Componente 2.2: Infraestructura y Recursos Tecnológicos", "04:15 – 04:50 (35 s)")
_Acción visual: Señalar las barras de consumo de recursos frente a los límites del host VPS._
#esteban[
  "El entorno de producción se montó sobre un VPS de 4 vCPUs, 8 GB de RAM y 50 GB SSD.
  Al perfilar el consumo contenerizado en Docker Compose: FastAPI requiere 1.5 CPUs y 1.5 GB RAM; PostgreSQL 16 opera con 1.0 CPU y 1.0 GB; n8n utiliza 0.8 CPU y 512 MB; los workers en segundo plano consumen 0.5 CPU y 256 MB; y Nginx apenas 0.2 CPU y 128 MB. Esto deja más de un 50% de capacidad ociosa en el servidor para absorber picos de tráfico en temporada alta."
]

#slide_header("11 / 36", "Componente 2.3: Procedimientos de BD y Versionamiento Alembic", "04:50 – 05:30 (40 s)")
_Acción visual: Mostrar el panel de migraciones V1 a V6 y la inyección automatizada de semillas._
#esteban[
  "El esquema relacional evoluciona de manera inmutable mediante *Alembic*.
  Contamos con 6 revisiones formales: desde el esquema base V1, la extensión `btree_gist` y restricción temporal RN-02 en V2, reservas grupales en V3, pagos acumulados y reseñas en V4, tarifas dinámicas por eventos en V5, hasta el catálogo de cafetería en V6.
  Al iniciar el contenedor, se ejecuta automáticamente `alembic upgrade head`, inyectando la semilla `dev_seed.sql` con los 9 cuartos iniciales si la base se encuentra limpia."
]

#slide_header("12 / 36", "Componente 2.4: Configuraciones Necesarias y Seguridad Perimetral", "05:30 – 06:10 (40 s)")
_Acción visual: Señalar la tabla de variables cifradas y el diagrama de aislamiento de puertos._
#esteban[
  "En seguridad perimetral aplicamos defensa en profundidad:
  Todos los secretos (`DATABASE_URL`, `JWT_SECRET`, tokens de WhatsApp y API keys) se inyectan cifrados mediante archivos `.env` fuera del repositorio Git.
  Únicamente los puertos web seguros (443/80) están expuestos a internet vía Nginx con TLS 1.3. El puerto de la base de datos (5432) y la API interna (8000) residen en una red Docker privada tipo `bridge`, totalmente inaccesibles desde el exterior."
]

#slide_header("13 a 16 / 36", "Secuencia de Despliegue, Ventana Nocturna, Rollback y Checklist", "06:10 – 07:30 (80 s)")
_Acción visual: Recorrer las 8 fases (13), el cronograma (14), el árbol de reversión (15) y el checklist (16)._
#esteban[
  "El despliegue se estandarizó en 8 fases secuenciales ejecutadas durante una ventana nocturna de bajo tráfico (22:00 a 23:30 h).
  Si durante las pruebas de humo se detecta incompatibilidad en base de datos o indisponibilidad mayor a 15 minutos, se dispara el *Plan de Rollback*: restauración automatizada del backup `pg_dump` previo y retorno a la versión anterior de contenedores en menos de 8 minutos.
  La lista de chequeo técnica de salida certificó el 100% de criterios aprobados antes de autorizar la apertura."
]

#slide_header("17 a 19 / 36", "Componente 3: Gestión de Cambios (CAB) y Autorización", "07:30 – 09:30 (120 s)")
_Acción visual: Mostrar los 6 cambios (CHG-01 a 06), la matriz de riesgos y el Acta formal firmada._
#esteban[
  "El Comité de Cambios (CAB) evaluó y aprobó 6 cambios significativos:
  Destaco el *CHG-02*, que consolidó el candado de reservas directamente en PostgreSQL con expiración inline y liberación atómica al desistir una cotización;
  el *CHG-01*, que corrigió el cálculo de reembolsos aplicándolo sobre el dinero abonado y no sobre la estancia completa, protegiendo la caja del hotel;
  y los cambios CHG-03 a CHG-06 para cuartos dinámicos, eventos, Salgados Café y auditoría inmutable.
  Con salvaguardas que redujeron el riesgo residual a nivel Nulo o Bajo, el Comité autorizó por unanimidad el pase a producción de la versión `1.0.0-FINAL`.
  Doy paso a Juan Felipe Garzón para sustentar la validación técnica y el candado GiST."
]

#pagebreak()

== ACTO 3: VALIDACIÓN, PRUEBAS Y EL CANDADO ATÓMICO RN-02 (09:30 – 14:30)
#text(size: 9pt, fill: rgb("#7a6b5f"))[*Ponente Principal:* Juan Felipe Garzón Ruiz · *Objetivo:* Demostrar el blindaje matemático anti-overbooking y resiliencia.]

#slide_header("20 y 21 / 36", "Componente 4.1 y 4.2: Estrategia de Pruebas e Integración", "09:30 – 10:50 (80 s)")
_Acción visual: Mostrar la división Utilidad/Garantía y los 5 escenarios funcionales superados._
#juan_felipe[
  "Muchas gracias, Esteban. Para certificar que el software es apto para su propósito (*Fit for Purpose*) y apto para su uso (*Fit for Use*), ejecutamos pruebas rigurosas:
  En utilidad, validamos 5 escenarios end-to-end: cotización por WhatsApp, confirmación en recepción, adición de consumos de café, reembolsos y auditoría, obteniendo un 100% de éxito contra contratos OpenAPI.
  En garantía, sometimos el núcleo transaccional a tres pruebas extremas: concurrencia en milisegundo cero, estrés bajo carga y recuperación ante desastres."
]

#slide_header("22 / 36", "Componente 4.3: El Candado Atómico Relacional (RN-02)", "10:50 – 12:30 (100 s) — CLAVE")
_Acción visual: Explicar paso a paso la secuencia concurrente de Cliente A vs Cliente B._
#juan_felipe[
  "Llegamos a la prueba de ingeniería más exigente: *El Candado Atómico de Concurrencia (RN-02)*.
  Simulamos el peor escenario de sobreventa hotelera:
  En el *milisegundo 0*, el Cliente A solicita por WhatsApp la Habitación 101. FastAPI abre una transacción, limpia expirados inline e inserta la reserva como `BLOQUEADA_TEMPORAL` con vigencia de 15 minutos.
  Tan solo *2 milisegundos después*, el Cliente B intenta reservar esa misma habitación desde la recepción web.
  En ese instante, la base de datos ejecuta la restricción física:
  #align(center)[
    #text(size: 8.5pt, fill: rgb("#991b1b"))[
      `EXCLUDE USING gist (room_id WITH =, daterange(check_in, check_out, '\[)') WITH &&)` \
      `WHERE (status IN ('BLOQUEADA_TEMPORAL', 'CONFIRMADA', 'EN_CURSO'))`
    ]
  ]
  PostgreSQL detecta la colisión a nivel de índice GiST, serializa la operación y *rechaza de inmediato al Cliente B con un error HTTP 409 Conflict*.
  Cuando el Cliente A valida su pago, la fila pasa a `CONFIRMADA`. Si no paga, el scheduler la marca como `EXPIRADA`.
  *El resultado es contundente: 0.0% de sobreventas o colisiones ante concurrencia extrema.*"
]

#slide_header("23 / 36", "Componente 4.4: Rendimiento y Latencia de Respuesta", "12:30 – 13:10 (40 s)")
_Acción visual: Contrastar las barras de latencia real contra los límites de SLA._
#juan_felipe[
  "Bajo pruebas de carga sostenida, los tiempos de respuesta superaron holgadamente las metas:
  La consulta de disponibilidad en la API REST respondió en *48 ms* (SLA: < 300 ms);
  La interacción completa del bot de WhatsApp tomó *1.2 segundos* (SLA: < 3.0 s);
  El bloqueo atómico de cuarto tomó *85 ms*;
  Y la carga del calendario en React tomó *180 ms*. El sistema es extremadamente ágil."
]

#slide_header("24 y 25 / 36", "Componente 4.5 y 4.6: Recuperación ante Desastres (DR) y UAT", "13:10 – 14:30 (80 s)")
_Acción visual: Mostrar la prueba de caída forzada (Slide 24) y la encuesta UAT con nota 9.4/10 (Slide 25)._
#juan_felipe[
  "En las pruebas de Desastre (DR), forzamos la caída de contenedores y corrupción de datos. El script de restauración desde el backup diario recuperó el servicio íntegro en *4 minutos con 12 segundos*, pulverizando nuestro RTO objetivo de 15 minutos, con cero pérdida de datos (RPO = 0).
  Finalmente, en las pruebas UAT, el equipo del hotel operó el sistema en escenarios reales durante 4 días, otorgando una satisfacción de *9.4 sobre 10* y firmando la conformidad.
  Regreso la palabra a Esteban Guarín para exponer la operación y soporte."
]

#pagebreak()

== ACTO 4: OPERACIONES, SOPORTE, SLA Y TRANSFERENCIA (14:30 – 17:00)
#text(size: 9pt, fill: rgb("#7a6b5f"))[*Ponente Principal:* Esteban Guarín Valencia · *Objetivo:* Sustentar la continuidad operativa, acuerdos de servicio y capacitación.]

#slide_header("26 a 28 / 36", "Componente 5: Estructura de Soporte, SLAs y Respaldo", "14:30 – 15:45 (75 s)")
_Acción visual: Mostrar los niveles L1/L2 (26), la tabla de severidades P1/P2/P3 (27) y la política R2 (28)._
#esteban[
  "Para sostener el servicio en producción establecimos un modelo de soporte en dos escalones:
  *Nivel 1 (Mostrador):* Recepcionistas y administrador resuelven dudas funcionales inmediatas de huéspedes y operación del PMS.
  *Nivel 2 (Ingeniería):* El equipo técnico monitorea la infraestructura Docker, webhooks de WhatsApp y base de datos.
  Nuestros SLAs fijan que ante incidentes críticos P1 (indisponibilidad total) el tiempo de respuesta es menor a 15 minutos y la solución en menos de 2 horas. Para fallas medias P2, resolución en menos de 8 horas; y para P3, en menos de 24 horas.
  La continuidad operativa está blindada con backups diarios automatizados a las 3:00 a. m. con `pg_dump` cifrado y replicado en Cloudflare R2 con retención de 30 días."
]

#slide_header("29 y 30 / 36", "Componente 6: Documentación y Capacitación del Personal", "15:45 – 17:00 (75 s)")
_Acción visual: Señalar los 4 manuales entregados (29) y el acta de 12 horas de capacitación (30)._
#esteban[
  "Para asegurar la autonomía del hotel entregamos cuatro manuales exhaustivos: Manual de Recepción, Guía de Administración, Guía Técnica de Despliegue en contenedor y Contratos OpenAPI de la API.
  Asimismo, completamos 12 horas de formación práctica con los 3 recepcionistas y el administrador en registro de huéspedes, asignación de habitaciones y cuadre de caja, logrando un 100% de aprobación en las pruebas evaluativas.
  Cedo el cierre a nuestro Product Owner, Juan José Arias."
]

== ACTO 5: COMUNICACIÓN, GO-LIVE, CIERRE Y RETORNO DE INVERSIÓN (17:00 – 19:30)
#text(size: 9pt, fill: rgb("#7a6b5f"))[*Ponente Principal:* Juan José Arias Gallego · *Objetivo:* Demostrar éxito de go-live, firmas de cierre y ROI del hotel.]

#slide_header("31 y 32 / 36", "Componente 7: Plan de Comunicación y Marcha Blanca", "17:00 – 17:50 (50 s)")
_Acción visual: Mostrar la matriz de stakeholders (31) y el cronograma de guardia presencial (32)._
#juan_jose[
  "En el Componente 7 gestionamos el factor humano: comunicamos formalmente a gerencia, personal de recepción, cafetería y huéspedes habituales mediante circulares y códigos QR informativos.
  La salida a producción se ejecutó bajo una *Marcha Blanca de 7 días*, con guardia presencial en recepción durante los primeros 3 días para resolver cualquier duda en vivo, logrando una adopción fluida sin traumatismos en el mostrador."
]

#slide_header("33 y 34 / 36", "Componente 8: Resultados Consolidados y Dictamen Formal", "17:50 – 18:40 (50 s)")
_Acción visual: Resumir los criterios cumplidos (33) y mostrar las tres firmas oficiales del Acta (34)._
#juan_jose[
  "El Componente 8 consolida los resultados: cero sobreventas en producción, catálogo dinámico operativo, backups certificados y personal capacitado. Los riesgos residuales son de impacto bajo y cuentan con planes de contingencia.
  En virtud de ello, el Comité de Transición emitió el *Dictamen de Aprobación Sin Salvedades*, formalizado en el Acta de Puesta en Servicio firmada por la Dirección de Tecnología, el Scrum Master y la Gerencia del Hotel."
]

#slide_header("35 y 36 / 36", "Retorno de Inversión (ROI), Conclusión y Preguntas", "18:40 – 19:30 (50 s)")
_Acción visual: Destacar los 4 números de negocio (-80%, 0.0%, +28%, 100%) y finalizar en la Slide 36._
#juan_jose[
  "El retorno de inversión para Torre Satori es contundente:
  *-80% de carga administrativa manual* en recepción;
  *0.0% de colisiones por overbooking* gracias a PostgreSQL GiST;
  *+28% de ventas nocturnas proyectadas* mediante el bot 24/7;
  y *100% de soberanía tecnológica*, ahorrando más de 15 millones de pesos anuales en licencias propietarias.
  Torre Satori PMS demuestra que con las prácticas de ITIL 4 es posible transicionar tecnología con cero disrupción y máximo valor. Muchas gracias; quedamos a su disposición para la sesión de preguntas."
]

#pagebreak()

== 2. Banco de Preguntas Típicas del Jurado y Respuestas Asignadas

#rect(
  fill: rgb("#fef3c7"),
  stroke: 1pt + rgb("#f59e0b"),
  radius: 4pt,
  width: 100%,
  inset: 10pt,
)[
  #text(weight: "bold", fill: rgb("#92400e"))[Recomendación Estratégica:]
  Si el jurado lanza una pregunta abierta, debe responder quien tiene el dominio directo del tema según la tabla siguiente. No se interrumpan; muestren cohesión de equipo.
]

#v(8pt)

=== Pregunta 1: Arquitectura y Candado de Concurrencia
*Pregunta del Jurado:* _"¿Por qué decidieron resolver el candado en PostgreSQL con `btree_gist` en lugar de usar Redis o bloqueos en memoria a nivel de aplicación?"_ \
*Asignado a:* *Juan Felipe Garzón Ruiz (Dev Team)* \
#juan_felipe[
  "Para un hotel de 9 habitaciones, introducir Redis generaba un punto único de falla adicional, mayor complejidad de red y riesgo de inconsistencias tipo *split-brain*.
  Al implementar la extensión `btree_gist` de PostgreSQL 16 y la restricción física `EXCLUDE USING gist`, el motor de base de datos evalúa matemáticamente el solapamiento de rangos de fechas a nivel de árbol GiST en la misma transacción ACID.
  Combinado con nuestra política de expiración inline (`expires_at < NOW()`), la base de datos es la única fuente de la verdad, no requiere sincronizaciones externas y garantiza el 0% de sobreventas con máxima simplicidad operacional."
]

#v(6pt)

=== Pregunta 2: Plan de Contingencia y Rollback
*Pregunta del Jurado:* _"Si durante el despliegue nocturno falla una migración de Alembic, ¿cómo garantizan que el hotel pueda operar al día siguiente?"_ \
*Asignado a:* *Esteban Guarín Valencia (Scrum Master / ITIL)* \
#esteban[
  "Nuestro procedimiento de rollback (Componente 2.7) está automatizado en un script de un solo paso: antes de iniciar `alembic upgrade head`, el sistema toma un dump completo de la base de datos.
  Si el healthcheck post-despliegue falla o supera los 15 minutos de diagnóstico, el script ejecuta `docker compose down`, restaura la base de datos al snapshot previo y levanta los contenedores etiquetados con el release estable anterior.
  En nuestras pruebas de recuperación de desastres (DR), este proceso tomó exactamente 4 minutos con 12 segundos, garantizando que a las 6:00 a. m. la recepción cuente con el sistema 100% disponible."
]

#v(6pt)

=== Pregunta 3: Adopción y Gestión del Cambio en el Negocio
*Pregunta del Jurado:* _"¿Cómo mitigaron la resistencia al cambio de recepcionistas acostumbrados al cuaderno físico?"_ \
*Asignado a:* *Juan José Arias Gallego (Product Owner)* \
#juan_jose[
  "Aplicamos el principio de ITIL 4 de *colaborar y promover visibilidad*:
  Involucramos a los recepcionistas desde el diseño de la interfaz web en React, asegurando que la grilla del calendario imitara la disposición mental de sus habitaciones.
  No entregamos el software 'en frío': realizamos 12 horas de capacitación basada en roles y estuvimos en guardia presencial durante los primeros 3 días de la Marcha Blanca acompañando check-ins reales.
  Al notar que tareas que antes tomaban 15 minutos ahora se completaban en 30 segundos, el personal abrazó la herramienta con una satisfacción final de 9.4 sobre 10."
]

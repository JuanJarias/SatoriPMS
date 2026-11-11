#set page(
  paper: "us-letter",
  margin: (x: 2cm, top: 2.5cm, bottom: 2.2cm),
  header: context {
    if here().page() > 1 [
      #text(9pt, fill: rgb("#7a6b5f"))[
        *Torre Satori PMS* · Guión Maestro de Sustentación en Pareja (ITIL 4 — Actividad 5)
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
  size: 9.8pt,
  lang: "es",
  fill: rgb("#261d19")
)

#set par(justify: true, leading: 0.65em)

// Estilos de ponentes con distintivos cromáticos
#let badge(speaker, role, col) = {
  rect(
    fill: col.lighten(85%),
    stroke: 0.8pt + col,
    radius: 3pt,
    inset: (x: 6pt, y: 3pt),
    outset: 0pt,
  )[#text(size: 8.5pt, weight: "bold", fill: col)[#speaker · #role]]
}

#let esteban(body) = {
  block(
    width: 100%,
    stroke: (left: 3pt + rgb("#15803d")),
    inset: (left: 10pt, y: 4pt),
    fill: rgb("#f0fdf4"),
    radius: (right: 4pt),
  )[
    #badge("ESTEBAN GUARÍN", "Procesos, Operaciones y Negocio", rgb("#15803d")) \
    #v(2pt)
    #body
  ]
}

#let juan_jose(body) = {
  block(
    width: 100%,
    stroke: (left: 3pt + rgb("#1e40af")),
    inset: (left: 10pt, y: 4pt),
    fill: rgb("#f0f5ff"),
    radius: (right: 4pt),
  )[
    #badge("JUAN JOSÉ ARIAS", "Ingeniería, Datos y Validación", rgb("#1e40af")) \
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
      text(weight: "bold", fill: white, size: 10pt)[Diapositiva #num: #title],
      text(weight: "bold", fill: rgb("#f5dfc6"), size: 9pt)[⏱ #time]
    )
  ]
  v(2pt)
}

// ── PORTADA EDITORIAL ──────────────────────────────────────────────────
#align(center)[
  #v(8pt)
  #text(size: 10.5pt, weight: "bold", fill: rgb("#c48b59"), tracking: 2pt)[HOTEL TORRE SATORI · SEVILLA, VALLE DEL CAUCA] \
  #v(3pt)
  #text(size: 21pt, weight: "black", fill: rgb("#261d19"))[Torre Satori PMS] \
  #text(size: 13pt, weight: "bold", fill: rgb("#7a3e1d"))[Guión de Sustentación en Pareja] \
  #text(size: 9.5pt, style: "italic", fill: rgb("#7a6b5f"))[Transición del Servicio y Operaciones (ITIL 4) — Versión Didáctica] \
  #v(6pt)
  #line(length: 40%, stroke: 1.5pt + rgb("#d4a373"))
  #v(6pt)
]

#rect(
  fill: rgb("#faf6f0"),
  stroke: 1pt + rgb("#e2d5c5"),
  radius: 6pt,
  width: 100%,
  inset: 8pt,
)[
  #grid(
    columns: (1fr, 1fr, 1fr),
    align: center,
    [
      *Modalidad*\
      Sustentación de 2 Personas\
      _Esteban Guarín & Juan José Arias_
    ],
    [
      *Diapositivas Soporte*\
      36 láminas visuales\
      _index.html (Enfoque de Valor)_
    ],
    [
      *Duración Estimada*\
      18 a 20 minutos\
      _(+ preguntas del jurado)_
    ]
  )
]

#v(6pt)

== 1. Matriz de Reparto de Tiempos y Temas

#table(
  columns: (1.2fr, 1.3fr, 1.7fr, 0.6fr),
  fill: (col, row) => if row == 0 { rgb("#322621") } else if calc.even(row) { rgb("#fcfaf7") } else { white },
  stroke: 0.5pt + rgb("#d9cbbe"),
  inset: 5pt,
  align: (left, left, left, center),
  [#text(fill: white, weight: "bold")[Ponente]],
  [#text(fill: white, weight: "bold")[Enfoque]],
  [#text(fill: white, weight: "bold")[Bloques y Diapositivas]],
  [#text(fill: white, weight: "bold")[Tiempo]],

  [*Esteban Guarín*], [Procesos, Negocio y Personas], [Acto 1 (01-03), Acto 2 (13-16), Acto 4 (26-30), Acto 5 (31-36)], [~10 min],
  [*Juan José Arias*], [Ingeniería y Validación], [Acto 1 (04-08), Acto 2 (09-12, 17-19), Acto 3 (20-25)], [~10 min],
)

#v(6pt)

#rect(
  fill: rgb("#fef3c7"),
  stroke: 1pt + rgb("#f59e0b"),
  radius: 4pt,
  width: 100%,
  inset: 8pt,
)[
  #text(weight: "bold", fill: rgb("#92400e"))[Guía Rápida: Analogías Sencillas para Responder Preguntas del Jurado] \
  #v(2pt)
  #text(size: 8.8pt)[
    - *FastAPI:* El despachador central rápido en Python que atiende tanto a WhatsApp como a la web en milésimas de segundo.
    - *PostgreSQL:* El archivador digital seguro donde viven las reservas, huéspedes y consumos de café.
    - *Regla GiST:* Un árbitro matemático en la base de datos que revisa el calendario e impide apartar el mismo cuarto dos veces.
    - *Docker:* Un contenedor sellado que asegura que el sistema funcione igual en cualquier servidor sin errores.
    - *Alembic:* El diario de versiones de la base de datos que actualiza las tablas automáticamente sin borrar datos.
    - *n8n:* El puente inteligente que conecta los mensajes de WhatsApp de los turistas con nuestro sistema central.
  ]
]

#v(8pt)
#line(length: 100%, stroke: 0.5pt + rgb("#d4a373"))
#v(6pt)

== ACTO 1: CONTEXTO, DIAGNÓSTICO Y ALCANCE (00:00 – 05:00)

#slide_header("01 / 36", "Portada Institucional", "00:00 – 00:40 (40 s)")
#esteban[
  "Muy buenos días, profesor y evaluadores. Les damos la bienvenida a la sustentación de la *Actividad 5: Transición del Servicio y Operaciones bajo el marco ITIL 4* para nuestro proyecto *Torre Satori PMS*.

  Para entender este trabajo no podemos quedarnos en la frialdad de los diagramas técnicos; tenemos que viajar mentalmente al Hotel Torre Satori, un hotel boutique de 9 habitaciones ubicado en Sevilla, Valle del Cauca.

  Hasta hace poco tiempo, este hotel operaba como muchos negocios familiares: con reservas anotadas a mano en un cuaderno y cientos de mensajes dispersos en el WhatsApp personal de los dueños. Hoy queremos mostrarles cómo logramos transformar esa operación en un servicio digital confiable, seguro y estructurado bajo las mejores prácticas de la industria."
]

#slide_header("02 / 36", "Equipo de Dirección e Ingeniería", "00:40 – 01:15 (35 s)")
#esteban[
  "Nuestro equipo de proyecto está conformado por tres personas, y hoy estamos liderando la sustentación Juan José Arias y mi persona:
  Quien les habla, *Esteban Guarín*, asumí el rol de Scrum Master y líder de procesos ITIL, velando por la organización del despliegue, el control de riesgos, la capacitación del personal y los acuerdos de servicio;
  *Juan José Arias*, nuestro Product Owner y líder técnico de esta presentación, se encargó de aterrizar las necesidades del hotel a la arquitectura, la base de datos y la garantía de que el sistema no falle bajo estrés;
  y contamos con el apoyo en ingeniería de *Juan Felipe Garzón* en el Development Team para la construcción de los módulos."
]

#slide_header("03 / 36", "Diagnóstico: Los 8 Problemas del Hotel", "01:15 – 02:30 (75 s)")
#esteban[
  "Al diagnosticar el hotel, identificamos 8 dolores operativos que amenazaban su rentabilidad:
  El más grave de todos era el *riesgo de sobreventa*: imaginen que un turista pide una habitación por WhatsApp un viernes a las 10 de la noche; el recepcionista no la anota en el cuaderno porque ya salió de turno, y a la mañana siguiente otro recepcionista se la entrega a un huésped que llegó al mostrador. Dos familias con maletas en la puerta para la misma habitación. En un hotel de 9 cuartos, una sobreventa destruye la reputación del negocio.
  El segundo dolor era la *pérdida de ventas nocturnas*: el turista actual cotiza en la noche; si nadie le responde de inmediato, busca otro hotel y la venta se pierde.
  Además, había cobros manuales equivocados, consumos de la cafetería Salgados Café que se olvidaban cobrar al check-out, y una recepción sobrecargada de llamadas y papel.
  Para ver cómo la ingeniería resolvió estos problemas, le doy la palabra a Juan José Arias."
]

#slide_header("04 / 36", "Del Problema a la Solución", "02:30 – 03:20 (50 s)")
#juan_jose[
  "Muchas gracias, Esteban. Frente a esos 8 problemas, no construimos herramientas aisladas, sino una solución integral:
  Para erradicar la sobreventa creamos un *candado de reservas en la base de datos*, que hace matemáticamente imposible que dos clientes aparten la misma habitación en las mismas fechas.
  Para capturar las reservas de noche conectamos un chatbot inteligente en WhatsApp que atiende, cotiza y aparta cuartos las 24 horas del día.
  Y para el mostrador creamos una aplicación web visual en React donde el recepcionista tiene su calendario al día, carga los pedidos de cafetería directo a la cuenta de la habitación y cierra la cuenta en segundos."
]

#slide_header("05 / 36", "Hoja de Ruta: Los 8 Componentes ITIL 4", "03:20 – 04:00 (40 s)")
#juan_jose[
  "Para asegurar que el paso a producción fuera un éxito, adoptamos el marco *ITIL 4 en su etapa de Transición del Servicio*.
  Esto significa que no nos limitamos a 'entregar código'; estructuramos 8 componentes formales: definir el alcance exacto, planear la instalación nocturna, controlar cada cambio, hacer pruebas rigurosas, acordar tiempos de respuesta ante fallas, capacitar al personal del hotel y firmar un acta de cierre basada en resultados reales."
]

#slide_header("06 a 08 / 36", "Componente 1: Alcance del Servicio y Límites Claros", "04:00 – 05:00 (60 s)")
#juan_jose[
  "En esta versión `1.0.0-FINAL`, entregamos 4 módulos que operan de forma sincronizada: el motor de cotización y bloqueo de cuartos, el catálogo dinámico de tarifas y eventos festivos, el módulo de ventas de Salgados Café y la auditoría que registra cada movimiento.
  Tan importante como lo que se entrega es tener claros los límites: acordamos no incluir dispersión bancaria automática —en su lugar, la recepción valida el comprobante de pago— y tampoco cancelar reservas automáticamente a mediodía por No-Show, porque en las carreteras de Sevilla los derrumbes y lluvias suelen retrasar a los turistas. El sistema se entrega en marcha blanca sobre un servidor en la nube protegido."
]

#pagebreak()

== ACTO 2: ARQUITECTURA, DESPLIEGUE Y CAMBIOS (05:00 – 11:30)

#slide_header("09 / 36", "Componente 2.1: Arquitectura y Componentes", "05:00 – 06:00 (60 s)")
#juan_jose[
  "Veamos cómo funciona el sistema por dentro:
  Decidimos crear un *monolito modular*. En palabras sencillas: en vez de tener diez programitas separados que pueden fallar al comunicarse, tenemos un único sistema ordenado y fácil de mantener.
  El huésped se comunica por WhatsApp; esa conversación la recibe *n8n*, que es como un puente automático. Por el otro lado, la recepcionista usa la pantalla web.
  *Ambos canales le hablan al mismo cerebro central: nuestra API construida con FastAPI en Python*.
  Y ese cerebro consulta una única base de datos segura en *PostgreSQL*, donde se guarda todo y donde se controla que nadie se cruce con las reservas de otro."
]

#slide_header("10 / 36", "Componente 2.2: Infraestructura y Servidor", "06:00 – 06:45 (45 s)")
#juan_jose[
  "Un criterio clave de negocio fue no ahogar financieramente al hotel con costos de servidores en la nube.
  Usamos un servidor virtual privado (VPS) muy económico de 4 núcleos y 8 GB de memoria RAM.
  Al medir el consumo real de nuestros componentes, el sistema apenas utiliza el 40% de la capacidad del servidor. Esto garantiza que durante temporadas altas de turismo o puentes festivos, la plataforma va a responder rápido y sin congelarse."
]

#slide_header("11 / 36", "Componente 2.3: Evolución Segura de la Base de Datos", "06:45 – 07:35 (50 s)")
#juan_jose[
  "En hotelería la información es sagrada: no se puede borrar por error el teléfono de un cliente o una reserva.
  Para gestionar la base de datos usamos una herramienta llamada *Alembic*, que funciona como un 'diario de versiones':
  En la V1 creamos la estructura básica; en la V2 activamos la regla que impide sobreventas; en la V3 permitimos que una familia reserve varias habitaciones juntas; en la V4 registramos abonos de dinero; en la V5 tarifas de feriados y en la V6 la cafetería.
  Cuando el servidor se enciende, lee automáticamente este diario y se pone al día en dos segundos, sin que nadie tenga que meter mano ni arriesgar los datos."
]

#slide_header("12 / 36", "Componente 2.4: Seguridad y Protección de Datos", "07:35 – 08:15 (40 s)")
#juan_jose[
  "Cumpliendo con la Ley 1581 de protección de datos personales:
  Primero, *las contraseñas y llaves de acceso están blindadas*: ninguna clave va escrita en el código; se inyectan de forma cifrada directamente en el servidor.
  Segundo, *puertas cerradas hacia afuera*: hacia internet público solo se abre la página web segura con candado SSL (HTTPS). La base de datos vive en una red interna privada y nadie desde afuera puede intentar entrar a ella.
  Ahora Esteban nos explicará cómo planeamos la instalación nocturna y el plan de emergencia."
]

#slide_header("13 a 16 / 36", "Secuencia de Despliegue, Ventana Nocturna y Rollback", "08:15 – 09:45 (90 s)")
#esteban[
  "Para que el hotel no sufriera interrupciones, el despliegue se planeó en una *ventana nocturna entre las 10:00 y las 11:30 de la noche*, que es la hora en que los huéspedes duermen y no hay llegadas en recepción. Dividimos el proceso en 8 pasos claros donde cada uno sabía exactamente qué hacer.
  Pero como la regla de oro en ITIL es anticipar el riesgo, diseñamos un *Plan de Reversión o Rollback*:
  ¿Qué significa esto? Que antes de tocar el sistema, sacamos una copia congelada de toda la información previa. Si durante la noche algo fallaba o el sistema tardaba más de 15 minutos en responder bien, un comando automático restauraba la copia anterior y en *menos de 5 minutos* el hotel volvía a estar operando como antes. En nuestras pruebas, la restauración tomó exactamente 4 minutos con 12 segundos.
  Afortunadamente no hubo que usarlo: la lista de chequeo final dio 100% aprobado.
  Juan José nos contará ahora los cambios autorizados por el comité."
]

#slide_header("17 a 19 / 36", "Componente 3: Gestión de Cambios (CAB) y Autorización", "09:45 – 11:30 (105 s)")
#juan_jose[
  "Bajo ITIL 4, ningún cambio entra al sistema si no lo aprueba formalmente el Comité de Cambios (CAB). Evaluamos 6 solicitudes clave:
  La decisión más importante fue el *CHG-02: Simplificar la arquitectura eliminando Redis*. Al inicio pensábamos usar Redis para retener habitaciones temporalmente, pero nos dimos cuenta de que tener dos bases de datos aumentaba el riesgo de fallas. Decidimos que PostgreSQL se encargara de todo de forma nativa. Menos piezas sueltas, mayor estabilidad.
  El *CHG-01* corrigió las cancelaciones: si un huésped abona el 50% y cancela, la penalidad se descuenta de lo abonado, no del total de la estancia, protegiendo las finanzas del hotel.
  Los cambios CHG-03 al 06 permitieron editar habitaciones, tarifas y productos de cafetería desde la web sin tocar código.
  Con todas las pruebas superadas, el Comité firmó el Acta autorizando la versión final. Pasemos a ver cómo demostramos que el sistema es invulnerable."
]

#pagebreak()

== ACTO 3: VALIDACIÓN Y EL CANDADO DE CONCURRENCIA (11:30 – 15:30)

#slide_header("20 y 21 / 36", "Componente 4.1 y 4.2: Estrategia de Pruebas", "11:30 – 12:30 (60 s)")
#juan_jose[
  "En ITIL 4 nos hacen dos preguntas: ¿El sistema hace lo que debe? (Utilidad). ¿Y lo hace de forma confiable? (Garantía).
  En utilidad probamos los 5 caminos del hotel: cotizar por WhatsApp, confirmar en mostrador, cargar consumos de café a la habitación, cancelar reservas y entrar de forma segura con contraseñas de recepción. Todo funcionó a la perfección.
  Pero la prueba de fuego era la garantía: someter el sistema a situaciones extremas de estrés."
]

#slide_header("22 / 36", "Componente 4.3: El Candado Anti-Sobreventa en Acción", "12:30 – 14:15 (105 s) — DIAPOSITIVA CLAVE")
#juan_jose[
  "Esta es la diapositiva que demuestra por qué el hotel no volverá a tener sobreventas:
  Imaginemos el caso más extremo de coincidencia:
  *Milisegundo 0:* El Cliente A está en WhatsApp y solicita apartar la Habitación 101 del 15 al 18 de noviembre. El sistema aparta el cuarto temporalmente por 15 minutos mientras el cliente realiza el pago.
  *Apenas 2 milisegundos después:* El Cliente B llega al mostrador físico del hotel y la recepcionista intenta apartar esa misma Habitación 101 para las mismas fechas. Da clic en guardar.
  ¿Qué ocurre? La base de datos tiene una regla matemática de exclusión. Funciona como un árbitro que mira el calendario: detecta que las fechas chocan en la misma habitación y *frena en seco la segunda petición de forma automática*.
  Al recepcionista le aparece de inmediato un aviso en pantalla: _'Habitación temporalmente ocupada por otra solicitud en curso'_.
  Si el Cliente A paga, la reserva queda confirmada. Si no paga en 15 minutos, el sistema suelta la habitación para que vuelva a estar libre.
  *El resultado es contundente: 0.0% de sobreventas, garantizado por la propia base de datos.*"
]

#slide_header("23 a 25 / 36", "Rendimiento, Recuperación de Desastres y Pruebas UAT", "14:15 – 15:30 (75 s)")
#juan_jose[
  "Comprobar la disponibilidad toma apenas *48 milisegundos*, y el bot de WhatsApp responde en poco más de un segundo. Es una experiencia sumamente fluida para el turista.
  Además, simulamos un apagón total del servidor. Ejecutamos el plan de rescate desde la copia de seguridad y levantamos el hotel completo en *4 minutos y 12 segundos*, sin perder una sola reserva.
  Y lo más gratificante: pusimos a los recepcionistas y al administrador a usar el sistema en vivo durante 4 días. La calificación que nos dieron fue de *9.4 sobre 10*, firmando a satisfacción.
  Ahora Esteban nos explicará el soporte en el día a día y la capacitación del equipo."
]

#pagebreak()

== ACTO 4: OPERACIONES, SOPORTE Y CAPACITACIÓN (15:30 – 17:30)

#slide_header("26 a 28 / 36", "Componente 5: Niveles de Soporte, Tiempos de Respuesta y Copias", "15:30 – 16:30 (60 s)")
#esteban[
  "Para que el hotel opere con tranquilidad, organizamos el soporte en dos niveles muy humanos:
  *Nivel 1 (En el hotel):* Si el recepcionista tiene una duda sobre cómo imprimir un recibo o buscar a un huésped, él mismo la resuelve apoyándose en su manual.
  *Nivel 2 (Ingeniería):* Si ocurre una falla técnica, el equipo de desarrollo atiende el caso. En los Acuerdos de Servicio (SLA) fijamos que ante una falla crítica respondemos en menos de 15 minutos y solucionamos en menos de 2 horas.
  Y para total tranquilidad, todas las madrugadas a las 3:00 de la mañana el sistema saca una copia de seguridad automática y cifrada que se guarda en la nube durante 30 días."
]

#slide_header("29 y 30 / 36", "Componente 6: Manuales y Capacitación Humana", "16:30 – 17:30 (60 s)")
#esteban[
  "Entregamos 4 manuales completos con capturas de pantalla paso a paso, redactados en lenguaje claro para el personal de mostrador y administración.
  Pero sabíamos que un manual en papel no basta. Realizamos *12 horas de talleres prácticos* con los 3 recepcionistas y el administrador.
  Los pusimos a registrar reservas reales, a cargar consumos de café, a cobrar y a solucionar dudas en un ambiente seguro de práctica. Cuando terminaron los talleres, el miedo a la computadora había desaparecido y todos aprobaron con éxito la evaluación."
]

== ACTO 5: MARCHA BLANCA, CIERRE Y RETORNO DE INVERSIÓN (17:30 – 20:00)

#slide_header("31 a 34 / 36", "Comunicación, Marcha Blanca y Dictamen Final", "17:30 – 18:45 (75 s)")
#esteban[
  "La salida a producción se hizo mediante una *Marcha Blanca de 7 días*. Durante los primeros 3 días estuvimos presentes en la recepción del hotel, parados al lado del personal en cada check-in real para darles respaldo inmediato.
  Los resultados fueron impecables: cero sobreventas, personal autónomo y operaciones al día. Por eso, el Comité de Transición emitió el *Dictamen de Aprobación Sin Salvedades*, ratificado en el Acta de Puesta en Servicio firmada por la Gerencia del Hotel."
]

#slide_header("35 y 36 / 36", "Retorno de Inversión (ROI), Conclusión y Preguntas", "18:45 – 19:45 (60 s)")
#esteban[
  "Para cerrar, miremos el valor real que este proyecto le entrega al Hotel Torre Satori:
  *-80% de tiempo en tareas manuales*: un registro que tomaba 15 minutos en papel ahora se hace en 40 segundos;
  *0.0% de sobreventas*: protegemos la reputación del hotel;
  *+28% de reservas nocturnas capturadas* gracias al bot de WhatsApp que cotiza 24/7;
  y *100% de soberanía tecnológica*: el hotel ahorra más de 15 millones de pesos al año al no pagar costosas licencias extranjeras por habitación.
  Torre Satori PMS demuestra que aplicar ITIL 4 no es llenar formatos: es la disciplina que permite transformar un negocio hotelero con tecnología confiable, rentable y cercana a las personas.
  Muchas gracias; quedamos atentos a las preguntas del profesor."
]

#pagebreak()

== 2. Banco de Preguntas Típicas del Jurado (Respuestas Asignadas)

#rect(
  fill: rgb("#fef3c7"),
  stroke: 1pt + rgb("#f59e0b"),
  radius: 4pt,
  width: 100%,
  inset: 10pt,
)[
  #text(weight: "bold", fill: rgb("#92400e"))[Dinámica en Pareja:]
  Si el jurado pregunta algo técnico sobre base de datos o arquitectura, responde *Juan José*. Si pregunta sobre usuarios, tiempos de respuesta, procesos, rollback o el hotel, responde *Esteban*.
]

#v(8pt)

=== Pregunta 1: Para Juan José Arias (Técnica / Candado y Arquitectura)
*Pregunta del Jurado:* _"¿Por qué decidieron resolver el candado en PostgreSQL en lugar de usar Redis o resolverlo en el código de la aplicación?"_ \
#juan_jose[
  "Inicialmente consideramos Redis porque es muy común para memoria rápida. Sin embargo, para un hotel de 9 habitaciones, meter Redis significaba tener dos bases de datos en el servidor, consumiendo más recursos y con el riesgo de que si Redis se caía o se desincronizaba de PostgreSQL, se generaban reservas corruptas.
  Al investigar a fondo PostgreSQL 16, descubrimos que el motor tiene una regla nativa llamada GiST que compara intervalos de fechas en la misma transacción. El propio motor de base de datos es el árbitro que frena el solapamiento de fechas.
  Con esto logramos cero sobreventas con una arquitectura mucho más simple, económica y sin puntos de falla externos."
]

#v(6pt)

=== Pregunta 2: Para Esteban Guarín (Procesos / Rollback y Contingencia)
*Pregunta del Jurado:* _"Si durante la noche de despliegue la base de datos se daña o falla una actualización, ¿cómo garantizan que los huéspedes de la mañana no queden desatendidos?"_ \
#esteban[
  "Bajo ITIL 4 ningún cambio entra a producción sin un plan de reversión probado.
  Antes de iniciar la actualización nocturna a las 10:00 PM, el sistema saca una copia completa congelada de la base de datos previa. Si tras 15 minutos de pruebas vemos que algo no responde bien, se activa el Rollback automático: el servidor apaga los componentes nuevos, restaura la copia congelada y levanta la versión anterior que ya sabíamos que funcionaba.
  Cronometramos este procedimiento en nuestras pruebas de desastre y tomó exactamente 4 minutos con 12 segundos. A las 6:00 de la mañana el hotel abre con total normalidad y sin traumatismos."
]

#v(6pt)

=== Pregunta 3: Para Esteban Guarín (Personas / Adopción y Resistencia)
*Pregunta del Jurado:* _"En un hotel acostumbrado a usar papel y cuaderno, ¿cómo lograron que los recepcionistas no rechazaran la herramienta?"_ \
#esteban[
  "Ese fue nuestro mayor cuidado. La tecnología fracasa si el usuario le tiene miedo a la pantalla.
  Primero, diseñamos la pantalla del calendario para que los colores y la cuadrícula de los 9 cuartos se parecieran a la hoja de papel que ellos ya conocían. Cuando abrieron el sistema, no vieron algo ajeno; vieron su hotel.
  Segundo, dedicamos 12 horas a practicar con ellos, dejando que se equivocaran en un ambiente de prueba seguro hasta ganar confianza. Y durante los primeros 3 días de operación real estuvimos físicamente a su lado en el mostrador.
  Cuando notaron que hacer un check-in ya no les tomaba 15 minutos sino menos de 1 minuto y que las cuentas de café cuadraban solas, ellos mismos se convirtieron en los mayores defensores del sistema."
]

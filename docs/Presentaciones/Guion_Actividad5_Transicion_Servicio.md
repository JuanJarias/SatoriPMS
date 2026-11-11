# Torre Satori PMS — Guión de Sustentación (Versión para 2 Ponentes)
## Entregable de Transición del Servicio y Operaciones (ITIL 4) — Actividad 5
**Modalidad:** Presentación en Pareja · **Duración Estimada:** 18 a 20 minutos (más preguntas del jurado)  
**Diapositivas:** 36 láminas visuales e interactivas en `index.html` / `docs/Presentaciones/Actividad5_Transicion_Servicio.html`  
**Equipo Expositor:**  
• **Esteban Guarín Valencia** — Enfoque de Procesos, Operaciones, Negocio y Personas (Mínima carga técnica).  
• **Juan José Arias Gallego** — Enfoque de Ingeniería, Arquitectura, Datos y Validación (Con analogías sencillas para no-expertos).

---

### Tabla de Reparto y Tiempos

| Acto | Diapositivas | Ponente Asignado | Tema Central | Tiempo Est. |
| :--- | :---: | :--- | :--- | :---: |
| **Acto 1: Negocio y Alcance** | 01 – 03 | **Esteban Guarín** | Bienvenida, equipo y los 8 problemas reales del hotel | 2.5 min |
| | 04 – 08 | **Juan José Arias** | Solución, hoja de ruta ITIL, módulos entregados y límites | 2.5 min |
| **Acto 2: Arquitectura y Despliegue** | 09 – 12 | **Juan José Arias** | Arquitectura FastAPI, servidor VPS, datos y seguridad básica | 3.5 min |
| | 13 – 16 | **Esteban Guarín** | Fases nocturnas, cronograma, plan de rescate y checklist | 2.5 min |
| | 17 – 19 | **Juan José Arias** | Cambios autorizados (CHG-01 a 06) y eliminación de Redis | 2.0 min |
| **Acto 3: Validación y Candado** | 20 – 25 | **Juan José Arias** | Pruebas de utilidad, **Candado Anti-Sobreventa**, latencias y DR | 4.0 min |
| **Acto 4: Operaciones y Soporte** | 26 – 30 | **Esteban Guarín** | Soporte L1/L2, acuerdos de servicio (SLA) y manuales | 2.0 min |
| **Acto 5: Go-Live, ROI y Cierre** | 31 – 36 | **Esteban Guarín** | Capacitación a recepcionistas, marcha blanca, ROI y cierre | 2.5 min |

---

## GUÍA RÁPIDA: ANALOGÍAS COTIDIANAS PARA NO-EXPERTOS
*(Úsalas si el profesor pide aclarar qué es alguna herramienta)*

- **FastAPI:** *"Es el cerebro del sistema. Imagínenlo como un despachador rápido que recibe pedidos tanto de WhatsApp como de la pantalla de recepción y los atiende en milésimas de segundo."*
- **PostgreSQL:** *"Es el archivador digital blindado donde vive toda la información del hotel: reservas, clientes, habitaciones y consumos de café."*
- **Regla GiST (Candado):** *"Es como un árbitro matemático dentro de la base de datos. Compara los calendarios y, si dos personas intentan tomar el mismo cuarto en las mismas fechas, pita falta y frena en seco la segunda reserva."*
- **Docker:** *"Es como un contenedor marítimo estándar: empaqueta el software para que funcione idéntico en cualquier computador o servidor, sin errores de instalación."*
- **Alembic:** *"Es el diario de versiones de la base de datos. Lleva la bitácora ordenada de cada tabla nueva para actualizar el sistema sin perder los datos que ya existen."*
- **n8n:** *"Es el puente inteligente que conecta los mensajes que la gente escribe en WhatsApp con nuestra base de datos."*
- **React 18:** *"Es la interfaz visual que usa el recepcionista en su navegador web: rápida, limpia y con un calendario interactivo."*

---

## ACTO 1: CONTEXTO, DIAGNÓSTICO Y ALCANCE (00:00 – 05:00)

### Diapositiva 01/36 — Portada Institucional
- **Ponente:** Esteban Guarín
- **Tiempo:** 00:00 – 00:40 (40 s)
- **Acción visual:** Mostrar la portada oficial con el logo SatoriPMS.
- **Locución (Esteban):**  
  > "Muy buenos días, profesor y evaluadores. Les damos la bienvenida a la sustentación de la **Actividad 5: Transición del Servicio y Operaciones bajo el marco ITIL 4** para nuestro proyecto **Torre Satori PMS**.  
  > Para entender este trabajo no podemos quedarnos en la frialdad de los diagramas técnicos; tenemos que viajar mentalmente al Hotel Torre Satori, un hotel boutique de 9 habitaciones ubicado en Sevilla, Valle del Cauca.  
  > Hasta hace poco tiempo, este hotel operaba como muchos negocios familiares: con reservas anotadas a mano en un cuaderno y cientos de mensajes dispersos en el WhatsApp personal de los dueños. Hoy queremos mostrarles cómo logramos transformar esa operación en un servicio digital confiable, seguro y estructurado bajo las mejores prácticas de la industria."

---

### Diapositiva 02/36 — Equipo de Dirección e Ingeniería
- **Ponente:** Esteban Guarín
- **Tiempo:** 00:40 – 01:15 (35 s)
- **Acción visual:** Señalar las tres columnas del equipo.
- **Locución (Esteban):**  
  > "Nuestro equipo de proyecto está conformado por tres personas, y hoy estamos liderando la sustentación Juan José Arias y mi persona:  
  > Quien les habla, **Esteban Guarín**, asumí el rol de Scrum Master y líder de procesos ITIL, velando por la organización del despliegue, el control de riesgos, la capacitación del personal y los acuerdos de servicio;  
  > **Juan José Arias**, nuestro Product Owner y líder técnico de esta presentación, se encargó de aterrizar las necesidades del hotel a la arquitectura, la base de datos y la garantía de que el sistema no falle bajo estrés;  
  > y contamos con el apoyo en ingeniería de **Juan Felipe Garzón** en el Development Team para la construcción de los módulos."

---

### Diapositiva 03/36 — Diagnóstico: Los 8 Problemas del Hotel
- **Ponente:** Esteban Guarín
- **Tiempo:** 01:15 – 02:30 (1 min 15 s)
- **Acción visual:** Recorrer las tarjetas de los dolores operativos del hotel.
- **Locución (Esteban):**  
  > "Al diagnosticar el hotel, identificamos 8 dolores operativos que amenazaban su rentabilidad:  
  > El más grave de todos era el **riesgo de sobreventa**: imaginen que un turista pide una habitación por WhatsApp un viernes a las 10 de la noche; el recepcionista no la anota en el cuaderno porque ya salió de turno, y a la mañana siguiente otro recepcionista se la entrega a un huésped que llegó al mostrador. Dos familias con maletas en la puerta para la misma habitación. En un hotel de 9 cuartos, una sobreventa destruye la reputación del negocio.  
  > El segundo dolor era la **pérdida de ventas nocturnas**: el turista actual cotiza en la noche; si nadie le responde de inmediato, busca otro hotel y la venta se pierde.  
  > Además, había cobros manuales equivocados, consumos de la cafetería Salgados Café que se olvidaban cobrar al check-out, y una recepción sobrecargada de llamadas y papel.  
  > Para ver cómo la ingeniería resolvió estos problemas, le doy la palabra a Juan José Arias."

---

### Diapositiva 04/36 — Del Problema a la Solución
- **Ponente:** Juan José Arias
- **Tiempo:** 02:30 – 03:20 (50 s)
- **Acción visual:** Señalar las flechas doradas que conectan problema con solución.
- **Locución (Juan José):**  
  > "Muchas gracias, Esteban. Frente a esos 8 problemas, no construimos herramientas aisladas, sino una solución integral:  
  > Para erradicar la sobreventa creamos un **candado de reservas en la base de datos**, que hace matemáticamente imposible que dos clientes aparten la misma habitación en las mismas fechas.  
  > Para capturar las reservas de noche conectamos un chatbot inteligente en WhatsApp que atiende, cotiza y aparta cuartos las 24 horas del día.  
  > Y para el mostrador creamos una aplicación web visual en React donde el recepcionista tiene su calendario al día, carga los pedidos de cafetería directo a la cuenta de la habitación y cierra la cuenta en segundos."

---

### Diapositiva 05/36 — Hoja de Ruta: Los 8 Componentes ITIL 4
- **Ponente:** Juan José Arias
- **Tiempo:** 03:20 – 04:00 (40 s)
- **Acción visual:** Mostrar la matriz de los 8 componentes ITIL.
- **Locución (Juan José):**  
  > "Para asegurar que el paso a producción fuera un éxito, adoptamos el marco **ITIL 4 en su etapa de Transición del Servicio**.  
  > Esto significa que no nos limitamos a 'entregar código'; estructuramos 8 componentes formales: definir el alcance exacto, planear la instalación nocturna, controlar cada cambio, hacer pruebas rigurosas, acordar tiempos de respuesta ante fallas, capacitar al personal del hotel y firmar un acta de cierre basada en resultados reales."

---

### Diapositivas 06 a 08/36 — Componente 1: Alcance del Servicio y Límites Claros
- **Ponente:** Juan José Arias
- **Tiempo:** 04:00 – 05:00 (1 min)
- **Acción visual:** Transicionar entre Slide 6 (Propósito), Slide 7 (Entregables) y Slide 8 (Límites y Marcha Blanca).
- **Locución (Juan José):**  
  > *(Slide 06 y 07)* "En esta versión `1.0.0-FINAL`, entregamos 4 módulos que operan de forma sincronizada: el motor de cotización y bloqueo de cuartos, el catálogo dinámico de tarifas y eventos festivos, el módulo de ventas de Salgados Café y la auditoría que registra cada movimiento.  
  > *(Slide 08)* Tan importante como lo que se entrega es tener claros los límites: acordamos no incluir dispersión bancaria automática —en su lugar, la recepción valida el comprobante de pago— y tampoco cancelar reservas automáticamente a mediodía por No-Show, porque en las carreteras de Sevilla los derrumbes y lluvias suelen retrasar a los turistas. El sistema se entrega en marcha blanca sobre un servidor en la nube protegido."

---

## ACTO 2: ARQUITECTURA, DESPLIEGUE Y CAMBIOS (05:00 – 11:30)

### Diapositiva 09/36 — Componente 2.1: Arquitectura y Componentes
- **Ponente:** Juan José Arias
- **Tiempo:** 05:00 – 06:00 (1 min)
- **Acción visual:** Explicar el flujo visual: Canales -> Cerebro Central -> Datos Seguros.
- **Locución (Juan José):**  
  > "Veamos cómo funciona el sistema por dentro:  
  > Decidimos crear un **monolito modular**. En palabras sencillas: en vez de tener diez programitas separados que pueden fallar al comunicarse, tenemos un único sistema ordenado y fácil de mantener.  
  > El huésped se comunica por WhatsApp; esa conversación la recibe **n8n**, que es como un puente automático. Por el otro lado, la recepcionista usa la pantalla web.  
  > **Ambos canales le hablan al mismo cerebro central: nuestra API construida con FastAPI en Python**.  
  > Y ese cerebro consulta una única base de datos segura en **PostgreSQL**, donde se guarda todo y donde se controla que nadie se cruce con las reservas de otro."

---

### Diapositiva 10/36 — Componente 2.2: Infraestructura y Servidor
- **Ponente:** Juan José Arias
- **Tiempo:** 06:00 – 06:45 (45 s)
- **Acción visual:** Mostrar las barras de consumo y la ficha del servidor VPS.
- **Locución (Juan José):**  
  > "Un criterio clave de negocio fue no ahogar financieramente al hotel con costos de servidores en la nube.  
  > Usamos un servidor virtual privado (VPS) muy económico de 4 núcleos y 8 GB de memoria RAM.  
  > Al medir el consumo real de nuestros componentes, el sistema apenas utiliza el 40% de la capacidad del servidor. Esto garantiza que durante temporadas altas de turismo o puentes festivos, la plataforma va a responder rápido y sin congelarse."

---

### Diapositiva 11/36 — Componente 2.3: Evolución Segura de la Base de Datos
- **Ponente:** Juan José Arias
- **Tiempo:** 06:45 – 07:35 (50 s)
- **Acción visual:** Mostrar las versiones V1 a V6 y el concepto de actualización automática.
- **Locución (Juan José):**  
  > "En hotelería la información es sagrada: no se puede borrar por error el teléfono de un cliente o una reserva.  
  > Para gestionar la base de datos usamos una herramienta llamada **Alembic**, que funciona como un 'diario de versiones':  
  > En la V1 creamos la estructura básica; en la V2 activamos la regla que impide sobreventas; en la V3 permitimos que una familia reserve varias habitaciones juntas; en la V4 registramos abonos de dinero; en la V5 tarifas de feriados y en la V6 la cafetería.  
  > Cuando el servidor se enciende, lee automáticamente este diario y se pone al día en dos segundos, sin que nadie tenga que meter mano ni arriesgar los datos."

---

### Diapositiva 12/36 — Componente 2.4: Seguridad y Protección de Datos
- **Ponente:** Juan José Arias
- **Tiempo:** 07:35 – 08:15 (40 s)
- **Acción visual:** Señalar las tarjetas de contraseñas protegidas y el perímetro seguro.
- **Locución (Juan José):**  
  > "Cumpliendo con la Ley 1581 de protección de datos personales:  
  > Primero, **las contraseñas y llaves de acceso están blindadas**: ninguna clave va escrita en el código; se inyectan de forma cifrada directamente en el servidor.  
  > Segundo, **puertas cerradas hacia afuera**: hacia internet público solo se abre la página web segura con candado SSL (HTTPS). La base de datos vive en una red interna privada y nadie desde afuera puede intentar entrar a ella.  
  > Ahora Esteban nos explicará cómo planeamos la instalación nocturna y el plan de emergencia."

---

### Diapositivas 13 a 16/36 — Secuencia de Despliegue, Ventana Nocturna y Rollback
- **Ponente:** Esteban Guarín
- **Tiempo:** 08:15 – 09:45 (1 min 30 s)
- **Acción visual:** Recorrer las 8 fases (13), el horario nocturno (14), el plan de rescate (15) y el checklist (16).
- **Locución (Esteban):**  
  > *(Slide 13 y 14)* "Para que el hotel no sufriera interrupciones, el despliegue se planeó en una **ventana nocturna entre las 10:00 y las 11:30 de la noche**, que es la hora en que los huéspedes duermen y no hay llegadas en recepción. Dividimos el proceso en 8 pasos claros donde cada uno sabía exactamente qué hacer.  
  > *(Slide 15)* Pero como la regla de oro en ITIL es anticipar el riesgo, diseñamos un **Plan de Reversión o Rollback**:  
  > ¿Qué significa esto? Que antes de tocar el sistema, sacamos una copia congelada de toda la información previa. Si durante la noche algo fallaba o el sistema tardaba más de 15 minutos en responder bien, un comando automático restauraba la copia anterior y en **menos de 5 minutos** el hotel volvía a estar operando como antes. En nuestras pruebas, la restauración tomó exactamente 4 minutos con 12 segundos.  
  > *(Slide 16)* Afortunadamente no hubo que usarlo: la lista de chequeo final dio 100% aprobado.  
  > Juan José nos contará ahora los cambios autorizados por el comité."

---

### Diapositivas 17 a 19/36 — Componente 3: Gestión de Cambios (CAB) y Autorización
- **Ponente:** Juan José Arias
- **Tiempo:** 09:45 – 11:30 (1 min 45 s)
- **Acción visual:** Mostrar los cambios CHG-01 a 06, la matriz de riesgo y el Acta de autorización.
- **Locución (Juan José):**  
  > *(Slide 17)* "Bajo ITIL 4, ningún cambio entra al sistema si no lo aprueba formalmente el Comité de Cambios (CAB). Evaluamos 6 solicitudes clave:  
  > La decisión más importante fue el **CHG-02: Simplificar la arquitectura eliminando Redis**. Al inicio pensábamos usar Redis para retener habitaciones temporalmente, pero nos dimos cuenta de que tener dos bases de datos aumentaba el riesgo de fallas. Decidimos que PostgreSQL se encargara de todo de forma nativa. Menos piezas sueltas, mayor estabilidad.  
  > El **CHG-01** corrigió las cancelaciones: si un huésped abona el 50% y cancela, la penalidad se descuenta de lo abonado, no del total de la estancia, protegiendo las finanzas del hotel.  
  > Los cambios CHG-03 al 06 permitieron editar habitaciones, tarifas y productos de cafetería desde la web sin tocar código.  
  > *(Slide 18 y 19)* Con todas las pruebas superadas, el Comité firmó el Acta autorizando la versión final. Pasemos a ver cómo demostramos que el sistema es invulnerable."

---

## ACTO 3: VALIDACIÓN Y EL CANDADO DE CONCURRENCIA (11:30 – 15:30)

### Diapositivas 20 y 21/36 — Componente 4.1 y 4.2: Estrategia de Pruebas
- **Ponente:** Juan José Arias
- **Tiempo:** 11:30 – 12:30 (1 min)
- **Acción visual:** Mostrar las pruebas de Utilidad (funcionales) y Garantía (resistencia).
- **Locución (Juan José):**  
  > "En ITIL 4 nos hacen dos preguntas: ¿El sistema hace lo que debe? (Utilidad). ¿Y lo hace de forma confiable? (Garantía).  
  > En utilidad probamos los 5 caminos del hotel: cotizar por WhatsApp, confirmar en mostrador, cargar consumos de café a la habitación, cancelar reservas y entrar de forma segura con contraseñas de recepción. Todo funcionó a la perfección.  
  > Pero la prueba de fuego era la garantía: someter el sistema a situaciones extremas de estrés."

---

### Diapositiva 22/36 — Componente 4.3: El Candado Anti-Sobreventa en Acción
- **Ponente:** Juan José Arias
- **Tiempo:** 12:30 – 14:15 (1 min 45 s) — **DIAPOSITIVA CLAVE**
- **Acción visual:** Explicar el diagrama paso a paso, señalando los dos clientes y los milisegundos.
- **Locución (Juan José):**  
  > "Esta es la diapositiva que demuestra por qué el hotel no volverá a tener sobreventas:  
  > Imaginemos el caso más extremo de coincidencia:  
  > **Milisegundo 0:** El Cliente A está en WhatsApp y solicita apartar la Habitación 101 del 15 al 18 de noviembre. El sistema aparta el cuarto temporalmente por 15 minutos mientras el cliente realiza el pago.  
  > **Apenas 2 milisegundos después:** El Cliente B llega al mostrador físico del hotel y la recepcionista intenta apartar esa misma Habitación 101 para las mismas fechas. Da clic en guardar.  
  > ¿Qué ocurre? La base de datos tiene una regla matemática de exclusión. Funciona como un árbitro que mira el calendario: detecta que las fechas chocan en la misma habitación y **frena en seco la segunda petición de forma automática**.  
  > Al recepcionista le aparece de inmediato un aviso en pantalla: *'Habitación temporalmente ocupada por otra solicitud en curso'*.  
  > Si el Cliente A paga, la reserva queda confirmada. Si no paga en 15 minutos, el sistema suelta la habitación para que vuelva a estar libre.  
  > **El resultado es contundente: 0.0% de sobreventas, garantizado por la propia base de datos.**"

---

### Diapositivas 23 a 25/36 — Rendimiento, Recuperación de Desastres y Pruebas UAT
- **Ponente:** Juan José Arias
- **Tiempo:** 14:15 – 15:30 (1 min 15 s)
- **Acción visual:** Mostrar las barras de velocidad (23), la prueba de caída forzada (24) y la nota 9.4/10 de los recepcionistas (25).
- **Locución (Juan José):**  
  > *(Slide 23)* "Comprobar la disponibilidad toma apenas **48 milisegundos**, y el bot de WhatsApp responde en poco más de un segundo. Es una experiencia sumamente fluida para el turista.  
  > *(Slide 24)* Además, simulamos un apagón total del servidor. Ejecutamos el plan de rescate desde la copia de seguridad y levantamos el hotel completo en **4 minutos y 12 segundos**, sin perder una sola reserva.  
  > *(Slide 25)* Y lo más gratificante: pusimos a los recepcionistas y al administrador a usar el sistema en vivo durante 4 días. La calificación que nos dieron fue de **9.4 sobre 10**, firmando a satisfacción.  
  > Ahora Esteban nos explicará el soporte en el día a día y la capacitación del equipo."

---

## ACTO 4: OPERACIONES, SOPORTE Y CAPACITACIÓN (15:30 – 17:30)

### Diapositivas 26 a 28/36 — Componente 5: Niveles de Soporte, Tiempos de Respuesta y Copias
- **Ponente:** Esteban Guarín
- **Tiempo:** 15:30 – 16:30 (1 min)
- **Acción visual:** Señalar los niveles L1/L2 (26), los tiempos de respuesta (27) y las copias automáticas (28).
- **Locución (Esteban):**  
  > *(Slide 26 y 27)* "Para que el hotel opere con tranquilidad, organizamos el soporte en dos niveles muy humanos:  
  > **Nivel 1 (En el hotel):** Si el recepcionista tiene una duda sobre cómo imprimir un recibo o buscar a un huésped, él mismo la resuelve apoyándose en su manual.  
  > **Nivel 2 (Ingeniería):** Si ocurre una falla técnica, el equipo de desarrollo atiende el caso. En los Acuerdos de Servicio (SLA) fijamos que ante una falla crítica respondemos en menos de 15 minutos y solucionamos en menos de 2 horas.  
  > *(Slide 28)* Y para total tranquilidad, todas las madrugadas a las 3:00 de la mañana el sistema saca una copia de seguridad automática y cifrada que se guarda en la nube durante 30 días."

---

### Diapositivas 29 y 30/36 — Componente 6: Manuales y Capacitación Humana
- **Ponente:** Esteban Guarín
- **Tiempo:** 16:30 – 17:30 (1 min)
- **Acción visual:** Mostrar los 4 manuales entregados (29) y el registro de 12 horas de talleres prácticos (30).
- **Locución (Esteban):**  
  > *(Slide 29)* "Entregamos 4 manuales completos con capturas de pantalla paso a paso, redactados en lenguaje claro para el personal de mostrador y administración.  
  > *(Slide 30)* Pero sabíamos que un manual en papel no basta. Realizamos **12 horas de talleres prácticos** con los 3 recepcionistas y el administrador.  
  > Los pusimos a registrar reservas reales, a cargar consumos de café, a cobrar y a solucionar dudas en un ambiente seguro de práctica. Cuando terminaron los talleres, el miedo a la computadora había desaparecido y todos aprobaron con éxito la evaluación."

---

## ACTO 5: MARCHA BLANCA, CIERRE Y RETORNO DE INVERSIÓN (17:30 – 20:00)

### Diapositivas 31 a 34/36 — Comunicación, Marcha Blanca y Dictamen Final
- **Ponente:** Esteban Guarín
- **Tiempo:** 17:30 – 18:45 (1 min 15 s)
- **Acción visual:** Mostrar la comunicación (31), la guardia presencial (32), los resultados (33) y el Acta de Cierre firmada (34).
- **Locución (Esteban):**  
  > *(Slide 31 y 32)* "La salida a producción se hizo mediante una **Marcha Blanca de 7 días**. Durante los primeros 3 días estuvimos presentes en la recepción del hotel, parados al lado del personal en cada check-in real para darles respaldo inmediato.  
  > *(Slide 33 y 34)* Los resultados fueron impecables: cero sobreventas, personal autónomo y operaciones al día. Por eso, el Comité de Transición emitió el **Dictamen de Aprobación Sin Salvedades**, ratificado en el Acta de Puesta en Servicio firmada por la Gerencia del Hotel."

---

### Diapositivas 35 y 36/36 — Retorno de Inversión (ROI), Conclusión y Preguntas
- **Ponente:** Esteban Guarín
- **Tiempo:** 18:45 – 19:45 (1 min)
- **Acción visual:** Señalar con fuerza los 4 números de negocio (-80%, 0.0%, +28%, 100%) y cerrar en la Slide 36.
- **Locución (Esteban):**  
  > *(Slide 35)* "Para cerrar, miremos el valor real que este proyecto le entrega al Hotel Torre Satori:  
  > **-80% de tiempo en tareas manuales**: un registro que tomaba 15 minutos en papel ahora se hace en 40 segundos;  
  > **0.0% de sobreventas**: protegemos la reputación del hotel;  
  > **+28% de reservas nocturnas capturadas** gracias al bot de WhatsApp que cotiza 24/7;  
  > y **100% de soberanía tecnológica**: el hotel ahorra más de 15 millones de pesos al año al no pagar costosas licencias extranjeras por habitación.  
  > *(Slide 36)* Torre Satori PMS demuestra que aplicar ITIL 4 no es llenar formatos: es la disciplina que permite transformar un negocio hotelero con tecnología confiable, rentable y cercana a las personas.  
  > Muchas gracias; quedamos atentos a las preguntas del profesor."

---

## BANCO DE PREGUNTAS TÍPICAS DEL JURADO (RESPUESTAS ASIGNADAS)

### Pregunta 1: Para Juan José Arias (Técnica / Candado y Arquitectura)
**Jurado:** *"¿Por qué decidieron resolver el candado en PostgreSQL en lugar de usar Redis o resolverlo en el código de la aplicación?"*  
**Respuesta sugerida:**  
> "Inicialmente consideramos Redis porque es muy común para memoria rápida. Sin embargo, para un hotel de 9 habitaciones, meter Redis significaba tener dos bases de datos en el servidor, consumiendo más recursos y con el riesgo de que si Redis se caía o se desincronizaba de PostgreSQL, se generaban reservas corruptas.  
> Al investigar a fondo PostgreSQL 16, descubrimos que el motor tiene una regla nativa llamada GiST que compara intervalos de fechas en la misma transacción. El propio motor de base de datos es el árbitro que frena el solapamiento de fechas.  
> Con esto logramos cero sobreventas con una arquitectura mucho más simple, económica y sin puntos de falla externos."

---

### Pregunta 2: Para Esteban Guarín (Procesos / Rollback y Contingencia)
**Jurado:** *"Si durante la noche de despliegue la base de datos se daña o falla una actualización, ¿cómo garantizan que los huéspedes de la mañana no queden desatendidos?"*  
**Respuesta sugerida:**  
> "Bajo ITIL 4 ningún cambio entra a producción sin un plan de reversión probado.  
> Antes de iniciar la actualización nocturna a las 10:00 PM, el sistema saca una copia completa congelada de la base de datos previa. Si tras 15 minutos de pruebas vemos que algo no responde bien, se activa el Rollback automático: el servidor apaga los componentes nuevos, restaura la copia congelada y levanta la versión anterior que ya sabíamos que funcionaba.  
> Cronometramos este procedimiento en nuestras pruebas de desastre y tomó exactamente 4 minutos con 12 segundos. A las 6:00 de la mañana el hotel abre con total normalidad y sin traumatismos."

---

### Pregunta 3: Para Esteban Guarín (Personas / Adopción y Resistencia)
**Jurado:** *"En un hotel acostumbrado a usar papel y cuaderno, ¿cómo lograron que los recepcionistas no rechazaran la herramienta?"*  
**Respuesta sugerida:**  
> "Ese fue nuestro mayor cuidado. La tecnología fracasa si el usuario le tiene miedo a la pantalla.  
> Primero, diseñamos la pantalla del calendario para que los colores y la cuadrícula de los 9 cuartos se parecieran a la hoja de papel que ellos ya conocían. Cuando abrieron el sistema, no vieron algo ajeno; vieron su hotel.  
> Segundo, dedicamos 12 horas a practicar con ellos, dejando que se equivocaran en un ambiente de prueba seguro hasta ganar confianza. Y durante los primeros 3 días de operación real estuvimos físicamente a su lado en el mostrador.  
> Cuando notaron que hacer un check-in ya no les tomaba 15 minutos sino menos de 1 minuto y que las cuentas de café cuadraban solas, ellos mismos se convirtieron en los mayores defensores del sistema."

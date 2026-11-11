# Torre Satori PMS — Guión Maestro de Sustentación (Humanizado y Explicado)
## Entregable de Transición del Servicio y Operaciones (ITIL 4) — Actividad 5
**Duración Total Estimada:** 18 a 20 minutos (más sesión de preguntas del jurado)  
**Diapositivas:** 36 láminas interactivas en `index.html` / `Actividad5_Transicion_Servicio.html`  
**Stack Oficial:** Python 3.12 · FastAPI (ASGI) · PostgreSQL 16 (`btree_gist`) · Alembic · React 18 (Vite/TS) · n8n self-hosted · WhatsApp Cloud API · Cloudflare R2.

---

### Reparto de Roles y Tiempos

| Integrante | Rol en el Proyecto | Bloques Asignados | Diapositivas | Tiempo Est. |
| :--- | :--- | :--- | :---: | :---: |
| **Juan José Arias Gallego** | Product Owner / Negocio | Acto 1 (Negocio, Diagnóstico y Alcance) y Acto 5 (Go-Live, Cierre y ROI) | 01–08, 31–36 | ~7 min |
| **Esteban Guarín Valencia** | Scrum Master / ITIL Lead | Acto 2 (Despliegue, Arquitectura y Cambios) y Acto 4 (Operaciones, Soporte y SLA) | 09–19, 26–30 | ~7 min |
| **Juan Felipe Garzón Ruiz** | Development Team / Ingeniero | Acto 3 (Validación, Pruebas y Candado Atómico GiST RN-02) | 20–25 | ~5 min |

---

## ACTO 1: INTRODUCCIÓN, DIAGNÓSTICO Y ALCANCE
**Ponente:** Juan José Arias Gallego (Product Owner)  
**Tiempo:** 00:00 – 03:30 (3.5 min)

---

### Diapositiva 01/36 — Portada Institucional
- **Tiempo:** 00:00 – 00:30 (30 s)
- **Acción visual:** Proyectar la lámina inicial con la tipografía oficial SatoriPMS.
- **Locución (Juan José):**  
  > "Buenos días, profesor y miembros del jurado evaluador. Les damos la bienvenida a la sustentación de la **Actividad 5: Transición del Servicio y Operaciones bajo el marco ITIL 4** para nuestro proyecto **Torre Satori PMS**.  
  > Para entender este proyecto no podemos quedarnos solo en diagramas de software; tenemos que pararnos físicamente en el Hotel Torre Satori, en Sevilla, Valle del Cauca. Hablamos de un hotel boutique de 9 habitaciones que, hasta hace muy poco, recibía a sus huéspedes y gestionaba reservas en un cuaderno de papel y mensajes dispersos de WhatsApp.  
  > Nuestro propósito en esta entrega es demostrarles cómo logramos llevar ese hotel a un servicio digital moderno, confiable y 100% operativo, integrando la experiencia del turista en WhatsApp con la administración web de recepción bajo un estándar formal de ITIL 4."

---

### Diapositiva 02/36 — Equipo de Dirección e Ingeniería
- **Tiempo:** 00:30 – 00:55 (25 s)
- **Acción visual:** Señalar las tres columnas con fotos y responsabilidades del equipo.
- **Locución (Juan José):**  
  > "Para garantizar que cada decisión técnica respondiera a una necesidad real del hotel, dividimos la responsabilidad en tres frentes muy claros:  
  > **Esteban Guarín Valencia**, como nuestro Scrum Master y líder ITIL, se encargó de toda la ingeniería de procesos: el plan de despliegue paso a paso, la gestión de cambios para que nada se rompiera y los acuerdos de nivel de servicio (SLA);  
  > **Juan Felipe Garzón Ruiz**, desde el Development Team, fue el cerebro detrás de la arquitectura técnica, el diseño de la base de datos relacional y el motor crítico para evitar colisiones de reservas;  
  > y quien les habla, **Juan José Arias**, como Product Owner, me aseguré de que el software resolviera el negocio real del hotel: definí los criterios de aceptación, acompañé las pruebas con los recepcionistas y lideré el dictamen de transición."

---

### Diapositiva 03/36 — Diagnóstico: Los 8 Problemas del Hotel
- **Tiempo:** 00:55 – 01:35 (40 s)
- **Acción visual:** Recorrer con naturalidad las tarjetas superiores e inferiores del diagnóstico.
- **Locución (Juan José):**  
  > "Cuando llegamos al hotel y analizamos su día a día, encontramos 8 problemas graves que le costaban tranquilidad y dinero a los dueños:  
  > El más crítico era el **riesgo de sobreventa**: imaginen que un turista pide una habitación por WhatsApp a las 10 de la noche y el recepcionista no la anota en el cuaderno de inmediato; al día siguiente llega otro huésped en mostrador y le asignan la misma habitación. Dos familias viajando a Sevilla con la misma reserva. En un hotel de 9 cuartos, una sobreventa te destruye la reputación del mes.  
  > A esto se sumaba la **pérdida de ventas nocturnas**: si alguien escribía de noche pidiendo cotización, nadie respondía hasta las 8 de la mañana, cuando el cliente ya había reservado en otro lugar.  
  > Además, había fugas de dinero por cobros manuales erróneos, consumos en el café 'Salgados' que se olvidaban cobrar al check-out, y una carga de trabajo repetitiva que no dejaba al recepcionista atender con calidez al huésped."

---

### Diapositiva 04/36 — Del Problema a la Solución de Ingeniería
- **Tiempo:** 01:35 – 02:05 (30 s)
- **Acción visual:** Señalar las flechas doradas que conectan los dolores con el impacto real.
- **Locución (Juan José):**  
  > "Frente a cada uno de esos 8 dolores, aplicamos ingeniería de software bien pensada:  
  > Para eliminar el overbooking al 100%, creamos un **candado atómico relacional directamente en PostgreSQL 16**, con una regla matemática GiST que hace físicamente imposible que dos reservas se solapen.  
  > Para capturar las ventas nocturnas, conectamos la API oficial de WhatsApp Cloud con n8n y un recomendador inteligente que cotiza y responde al instante las 24 horas del día.  
  > Y para el mostrador, construimos una interfaz web rápida en React 18 donde el recepcionista ve su calendario en tiempo real, carga los cafés del huésped a su cuenta y liquida la cuenta en 30 segundos con total transparencia."

---

### Diapositiva 05/36 — Hoja de Ruta: Los 8 Componentes ITIL 4
- **Tiempo:** 02:05 – 02:30 (25 s)
- **Acción visual:** Mostrar la matriz de 8 componentes de la transición del servicio.
- **Locución (Juan José):**  
  > "Para que esta solución no se quedara en un prototipo de laboratorio, adoptamos la guía de **Transición del Servicio de ITIL 4**.  
  > Estructuramos nuestro trabajo en 8 componentes formales: definir el servicio, planear el despliegue sin interrumpir al hotel, controlar cada cambio mediante un comité, validar y probar bajo estrés, diseñar el soporte diario, capacitar al personal, comunicar el go-live y emitir un dictamen de aceptación con base en resultados tangibles."

---

### Diapositivas 06 a 08/36 — Componente 1: Definición, Funcionalidades y Límites
- **Tiempo:** 02:30 – 03:30 (1 min)
- **Acción visual:** Transicionar entre Slide 6 (Propósito), Slide 7 (Funcionalidades) y Slide 8 (Límites claros).
- **Locución (Juan José):**  
  > *(Slide 06)* "El servicio SatoriPMS tiene un propósito muy humano: liberar al personal de tareas mecánicas para que se concentren en hospitalidad, y darle al huésped la facilidad de reservar desde la app que ya usa todos los días: WhatsApp.  
  > *(Slide 07)* En esta versión formal, la `1.0.0-FINAL`, entregamos 4 módulos que funcionan al unísono: el motor de cotización y bloqueo de habitaciones, el catálogo de tarifas y eventos especiales, la comanda y tienda de Salgados Café, y la auditoría inmutable que registra quién hizo cada acción.  
  > *(Slide 08)* Pero un buen proyecto también se define por lo que **no** hace: acordamos con el hotel dejar fuera la pasarela bancaria con dispersión automática —manejando en su lugar comprobantes validados por recepción— y no aplicar cancelación automática por No-Show a mediodía, porque en la hotelería de Sevilla los turistas de carretera a menudo llegan tarde por derrumbes o clima. El sistema se entrega completamente desplegado en un servidor VPS con conexión segura TLS 1.3.  
  > Ahora le doy la palabra a Esteban Guarín, quien nos explicará cómo planeamos el despliegue técnico y la arquitectura del sistema."

---

## ACTO 2: PLAN DE DESPLIEGUE, ARQUITECTURA Y GESTIÓN DE CAMBIOS
**Ponente:** Esteban Guarín Valencia (Scrum Master / ITIL Lead)  
**Tiempo:** 03:30 – 09:30 (6 min)

---

### Diapositiva 09/36 — Componente 2.1: Arquitectura y Componentes Desplegados
- **Tiempo:** 03:30 – 04:15 (45 s)
- **Acción visual:** Explicar las 4 capas del diagrama: Canales -> Gateway -> Backend FastAPI -> PostgreSQL.
- **Locución (Esteban):**  
  > "Muchas gracias, Juan José. Cuando nos sentamos a diseñar la arquitectura, teníamos una premisa clara: **simplicidad y robustez**. Para un hotel de 9 habitaciones, montar microservicios distribuidos hubiera sido un error de sobreingeniería costoso e inestable.  
  > Por eso diseñamos un **monolito modular hexagonal en FastAPI sobre Python 3.12**, montado en un contenedor ASGI con Uvicorn.  
  > Miren la elegancia del flujo: el huésped que escribe por WhatsApp entra a través de Meta Cloud API y nuestro orquestador n8n; mientras que la recepcionista usa la web en React 18. **Ambos canales consumen exactamente la misma API REST**. No hay lógica duplicada.  
  > Y en la base de datos, usamos **PostgreSQL 16**. Allí reside toda la verdad: maneja las transacciones ACID, limpia automáticamente los bloqueos temporales de 15 minutos y aplica la restricción GiST física que blinda el overbooking."

---

### Diapositiva 10/36 — Componente 2.2: Infraestructura y Recursos Tecnológicos
- **Tiempo:** 04:15 – 04:50 (35 s)
- **Acción visual:** Señalar las barras de uso de CPU y RAM y la especificación del host VPS.
- **Locución (Esteban):**  
  > "Uno de los mayores temores de un hotel independiente es el costo del servidor. Queríamos que el sistema corriera impecable sin gastar de más.  
  > Contratamos un VPS estándar de 4 núcleos (vCPUs), 8 GB de RAM y 50 GB en disco SSD.  
  > Al medir el consumo real en Docker Compose: FastAPI apenas necesita 1.5 CPUs y 1.5 GB de RAM; PostgreSQL 16 trabaja holgado con 1 CPU y 1 GB; n8n utiliza 0.8 CPU y 512 MB; las tareas en segundo plano consumen 0.5 CPU; y el servidor web Nginx usa apenas 128 MB.  
  > ¿Qué significa esto? Que el servidor opera a menos del 50% de su capacidad. Tenemos un margen enorme para soportar fines de semana de alta ocupación o temporadas como el Festival de Bandola de Sevilla sin que el sistema se ralentice."

---

### Diapositiva 11/36 — Componente 2.3: Procedimientos de BD y Versionamiento Alembic
- **Tiempo:** 04:50 – 05:30 (40 s)
- **Acción visual:** Explicar la línea de tiempo de migraciones V1 a V6 y la automatización con Alembic.
- **Locución (Esteban):**  
  > "En una base de datos en producción no se puede improvisar. No se pueden alterar columnas 'a mano' con interfaces gráficas porque corres el riesgo de corromper reservas reales.  
  > Para garantizar inmutabilidad, usamos **Alembic**. Cada cambio de esquema es un archivo de código Python versionado en Git:  
  > La V1 creó las tablas base; la V2 instaló la extensión `btree_gist` y la regla de no-solapamiento; la V3 habilitó reservas de varias habitaciones en un solo grupo; la V4 estructuró los abonos parciales y reseñas; la V5 agregó tarifas dinámicas para feriados; y la V6 sumó el menú de Salgados Café.  
  > El despliegue es completamente automático: cuando el contenedor arranca, ejecuta `alembic upgrade head`, detecta si hay alguna migración pendiente y la aplica en segundos de manera transaccional. Si la base está vacía, inyecta la semilla `dev_seed.sql` con las 9 habitaciones del hotel."

---

### Diapositiva 12/36 — Componente 2.4: Configuraciones Necesarias y Seguridad Perimetral
- **Tiempo:** 05:30 – 06:10 (40 s)
- **Acción visual:** Mostrar las variables secretas y el diagrama de aislamiento de puertos.
- **Locución (Esteban):**  
  > "La seguridad no es un accesorio: protege los datos privados de los huéspedes bajo la Ley 1581 de Colombia.  
  > Aplicamos dos principios fundamentales:  
  > Primero, **cero secretos en código**: las contraseñas de base de datos, el secreto JWT para recepcionistas y los tokens de WhatsApp nunca se suben a Git; se inyectan en tiempo de ejecución mediante variables de entorno cifradas en el servidor.  
  > Segundo, **aislamiento de red**: hacia internet público únicamente abrimos los puertos seguros 80 y 443 con certificado SSL TLS 1.3 gestionado por Nginx. El puerto de la base de datos (5432) y el de FastAPI (8000) viven dentro de una red Docker privada tipo `bridge`. Nadie desde internet puede intentar conectarse directamente a la base de datos."

---

### Diapositivas 13 a 16/36 — Secuencia de Despliegue, Ventana Nocturna, Rollback y Checklist
- **Tiempo:** 06:10 – 07:35 (1 min 25 s)
- **Acción visual:** Recorrer las 8 fases (13), el cronograma nocturno (14), el plan de rollback (15) y el checklist (16).
- **Locución (Esteban):**  
  > *(Slide 13)* "El paso a producción lo planificamos como una cirugía: dividimos el despliegue en 8 fases continuas, desde el backup preventivo inicial hasta las pruebas de humo con reservas de prueba.  
  > *(Slide 14)* Elegimos una ventana nocturna de 22:00 a 23:30 h, que es la franja de menor actividad en el hotel. Cada integrante tuvo una tarea precisa y cronometrada para evitar confusiones en terminal.  
  > *(Slide 15)* Pero como buenos ingenieros, siempre planificamos el peor escenario: **¿Qué pasa si algo falla?**  
  > Diseñamos un **Plan de Rollback automatizado**: si durante la migración o las pruebas de humo la base de datos falla o los servicios tardan más de 15 minutos en responder, un script de un solo comando apaga los contenedores nuevos, restaura el snapshot congelado de la base de datos previa y levanta la versión anterior. En nuestras pruebas de contingencia, todo este proceso de reversión tomó apenas **4 minutos con 12 segundos**, garantizando que el hotel nunca quede a ciegas.  
  > *(Slide 16)* La lista de chequeo de salida técnica arrojó 100% de verificación antes de declarar abierto el servicio."

---

### Diapositivas 17 a 19/36 — Componente 3: Gestión de Cambios (CAB) y Autorización
- **Tiempo:** 07:35 – 09:30 (1 min 55 s)
- **Acción visual:** Explicar la tabla de cambios (17), la matriz de riesgos (18) y el Acta de autorización formal (19).
- **Locución (Esteban):**  
  > *(Slide 17)* "En el Componente 3 formalizamos 6 cambios mayores a través del Comité de Autorización de Cambios (CAB):  
  > Quiero resaltar especialmente el **CHG-02**, que fue una decisión técnica de gran impacto: **eliminamos la dependencia de Redis**. Inicialmente se pensaba usar Redis para el bloqueo temporal, pero nos dimos cuenta de que sumaba un punto de falla innecesario y riesgo de inconsistencias si Redis y Postgres se desincronizaban. Migramos todo a PostgreSQL con expiración nativa y ganamos simplicidad absoluta.  
  > También el **CHG-01**, que corrigió el cálculo de cancelaciones: si un huésped abonó el 50% y cancela con penalidad del 10%, la penalidad se descuenta del dinero abonado (`paid_amount`) y no del total de la estancia, protegiendo la caja del hotel.  
  > Y los cambios CHG-03 a CHG-06, que permitieron gestionar habitaciones, eventos y productos de cafetería desde la interfaz sin tocar código.  
  > *(Slide 18)* Evaluamos el impacto y riesgo de cada cambio, asegurando salvaguardas que dejaron el riesgo residual en niveles mínimos.  
  > *(Slide 19)* Como consta en el Acta de Autorización firmada por Juan José en Negocio, Juan Felipe en Arquitectura y mi persona en Procesos, la versión `1.0.0-FINAL` fue aprobada por unanimidad.  
  > Ahora le doy el paso a Juan Felipe Garzón, quien nos va a demostrar con números y diagramas cómo validamos el motor técnico y el candado de concurrencia."

---

## ACTO 3: VALIDACIÓN, PRUEBAS Y EL CANDADO ATÓMICO (RN-02)
**Ponente:** Juan Felipe Garzón Ruiz (Development Team / Ingeniero)  
**Tiempo:** 09:30 – 14:30 (5 min)

---

### Diapositivas 20 y 21/36 — Componente 4.1 y 4.2: Estrategia de Pruebas e Integración
- **Tiempo:** 09:30 – 10:45 (1 min 15 s)
- **Acción visual:** Mostrar la dualidad Utilidad/Garantía y los 5 escenarios funcionales superados al 100%.
- **Locución (Juan Felipe):**  
  > "Muchas gracias, Esteban. En ingeniería de software suele decirse que 'un sistema no probado es un sistema que no funciona'. Bajo ITIL 4, dividimos la validación en dos preguntas esenciales:  
  > ¿El sistema sirve para lo que el negocio necesita? Esos son los **Criterios de Utilidad**.  
  > ¿Y el sistema es confiable bajo presión? Esos son los **Criterios de Garantía**.  
  > *(Slide 21)* En Utilidad, probamos 5 escenarios de punta a punta: cotizar por WhatsApp y que los precios coincidan con las tarifas del hotel; confirmar una reserva en recepción con su registro de auditoría; cargar desayunos o cafés al folio de una habitación; calcular penalidades de cancelación; y validar la seguridad de login con tokens JWT. Los 5 escenarios pasaron con 100% de éxito contra nuestros contratos de OpenAPI."

---

### Diapositiva 22/36 — Componente 4.3: El Candado Atómico Relacional (RN-02)
- **Tiempo:** 10:45 – 12:45 (2 min) — **DIAPOSITIVA CENTRAL / DEMO TÉCNICA**
- **Acción visual:** Explicar paso a paso la secuencia en pantalla, señalando con calma las marcas de tiempo (ms 0, ms 2, ms 3).
- **Locución (Juan Felipe):**  
  > "Llegamos al corazón técnico del proyecto: **¿Cómo garantizamos que jamás haya sobreventa? (Regla de Negocio RN-02)**.  
  > Pensemos en el escenario más difícil:  
  > Son exactamente las **10:00:00 con 000 milisegundos**. El Cliente A está chateando por WhatsApp y decide cotizar y retener la Habitación 101 del 15 al 18 de noviembre. FastAPI recibe la petición, abre una transacción, limpia cualquier reserva vencida de esa habitación e inserta la fila con estado `BLOQUEADA_TEMPORAL` y una expiración de 15 minutos (`expires_at = NOW() + 15 min`).  
  > Apenas **2 milisegundos después** (10:00:00 con 002 ms), el Cliente B está físicamente en el mostrador del hotel y el recepcionista intenta apartar esa misma habitación 101 para las mismas fechas. Da clic en guardar.  
  > ¿Qué hace el sistema? FastAPI intenta insertar la reserva en PostgreSQL, pero en la base de datos tenemos activa esta restricción física:  
  > `EXCLUDE USING gist (room_id WITH =, daterange(check_in, check_out, '[)') WITH &&) WHERE (status IN ('BLOQUEADA_TEMPORAL', 'CONFIRMADA', 'EN_CURSO'))`.  
  > Esto no es un simple `UNIQUE`; es un índice de árbol GiST que compara matemáticamente la intersección de intervalos de fechas. PostgreSQL detecta que las fechas se tocan en la misma habitación y **bloquea físicamente la inserción a nivel de motor de base de datos**.  
  > FastAPI captura esa excepción de integridad y le responde de inmediato al recepcionista en el milisegundo 3 con un código **HTTP 409 Conflicto**: *'Habitación temporalmente bloqueada por otra cotización en curso'*.  
  > Si el Cliente A completa el pago, el webhook validado cambia el estado a `CONFIRMADA`. Y si se arrepiente o pasan los 15 minutos, un worker en segundo plano con APScheduler marca el registro como `EXPIRADA` y el cuarto vuelve a quedar libre automáticamente.  
  > **El resultado: Cero sobreventas garantizadas por el propio motor relacional.**"

---

### Diapositiva 23/36 — Componente 4.4: Rendimiento y Latencia de Respuesta
- **Tiempo:** 12:45 – 13:25 (40 s)
- **Acción visual:** Comparar las barras de latencia real contra los umbrales máximos tolerados.
- **Locución (Juan Felipe):**  
  > "Someter el sistema a candados estrictos no sirvió de nada si la aplicación se volvía lenta. Por eso medimos la latencia bajo carga:  
  > Consultar la disponibilidad de habitaciones toma en promedio **48 milisegundos**, cuando nuestro límite de SLA era de 300 ms;  
  > El flujo completo del bot de WhatsApp, incluyendo la llamada al webhook y la respuesta al usuario, promedia **1.2 segundos**, muy por debajo de los 3 segundos que tolera un usuario de mensajería;  
  > El bloqueo atómico con GiST toma apenas **85 milisegundos**;  
  > Y la pantalla del calendario de recepción en React carga en **180 ms**. El sistema es ágil, liviano y responde al instante."

---

### Diapositivas 24 y 25/36 — Componente 4.5 y 4.6: Recuperación ante Desastres (DR) y UAT
- **Tiempo:** 13:25 – 14:30 (1 min 05 s)
- **Acción visual:** Mostrar la prueba de desastre forzado (24) y la matriz de aceptación UAT con nota 9.4/10 (25).
- **Locución (Juan Felipe):**  
  > *(Slide 24)* "En las pruebas de Recuperación ante Desastres (DR), no nos conformamos con la teoría: matamos los contenedores de golpe y simulamos pérdida de datos. Ejecutamos el script de recuperación desde el backup diario cifrado (`pg_dump`) y logramos levantar el servicio completo, con consistencia total, en **4 minutos con 12 segundos**. Nuestro objetivo de RTO era de 15 minutos; lo superamos ampliamente con cero pérdida de información (RPO = 0).  
  > *(Slide 25)* Por último, en las Pruebas de Aceptación con Usuarios (UAT), los recepcionistas y el administrador del hotel operaron el sistema durante 4 días seguidos en situaciones reales de mostrador. La calificación que nos otorgaron fue de **9.4 sobre 10**, firmando a satisfacción.  
  > Con esto demostramos que el software es seguro y confiable. Le regreso la palabra a Esteban Guarín para ver cómo se soporta y mantiene este servicio en su vida diaria."

---

## ACTO 4: OPERACIONES, SOPORTE, SLA Y TRANSFERENCIA
**Ponente:** Esteban Guarín Valencia (Scrum Master / ITIL Lead)  
**Tiempo:** 14:30 – 17:00 (2.5 min)

---

### Diapositivas 26 a 28/36 — Componente 5: Estructura de Soporte, SLAs y Respaldo
- **Tiempo:** 14:30 – 15:45 (1 min 15 s)
- **Acción visual:** Mostrar los escalones L1/L2 (26), la tabla de severidades (27) y la política de backups (28).
- **Locución (Esteban):**  
  > *(Slide 26)* "Un servicio en producción necesita personas y reglas claras para sostenerse. Diseñamos un soporte en dos niveles muy aterrizados:  
  > **Nivel 1 (Mostrador del Hotel):** Los recepcionistas y el administrador resuelven dudas funcionales del día a día con la ayuda de su manual;  
  > **Nivel 2 (Ingeniería de Software):** Nuestro equipo técnico atiende incidentes de servidor, caída de webhooks o errores no controlados.  
  > *(Slide 27)* En los Acuerdos de Nivel de Servicio (SLA) nos comprometimos con tiempos estrictos: ante un incidente P1 Crítico —por ejemplo, que el sistema no abra en recepción— respondemos en menos de 15 minutos y resolvemos en menos de 2 horas. Para fallas medias (P2), solución en menos de 8 horas; y para dudas menores (P3), menos de 24 horas.  
  > *(Slide 28)* Y para que los dueños duerman tranquilos, programamos un respaldo diario automático todas las madrugadas a las 3:00 a. m. mediante `pg_dump` comprimido y cifrado, que se sube automáticamente a un bucket privado en Cloudflare R2 con retención de 30 días."

---

### Diapositivas 29 y 30/36 — Componente 6: Gestión del Conocimiento y Capacitación
- **Tiempo:** 15:45 – 17:00 (1 min 15 s)
- **Acción visual:** Señalar las portadas de los 4 manuales entregados (29) y el registro de 12 horas de capacitación (30).
- **Locución (Esteban):**  
  > *(Slide 29)* "De nada sirve entregar buen software si el cliente queda 'atado' a los programadores para siempre. Bajo ITIL 4, transferimos el conocimiento mediante 4 manuales completos: el Manual de Recepción con capturas paso a paso, la Guía de Administración, la Guía Técnica de Despliegue en Docker y los contratos OpenAPI de la API.  
  > *(Slide 30)* Y lo más importante: **capacitamos a los humanos**. Realizamos 12 horas de talleres prácticos con los 3 recepcionistas y el administrador. No les dimos una clase magistral aburrida: los pusimos a registrar reservas reales, a cargar cafés de Salgados al folio, a cobrar y a cuadrar caja, hasta que se sintieron seguros y autónomos. Todos aprobaron la evaluación práctica final.  
  > Cedo el cierre de esta sustentación a nuestro Product Owner, Juan José Arias."

---

## ACTO 5: COMUNICACIÓN, GO-LIVE, CIERRE Y RETORNO DE INVERSIÓN
**Ponente:** Juan José Arias Gallego (Product Owner)  
**Tiempo:** 17:00 – 19:30 (2.5 min)

---

### Diapositivas 31 y 32/36 — Componente 7: Plan de Comunicación y Marcha Blanca
- **Tiempo:** 17:00 – 17:50 (50 s)
- **Acción visual:** Mostrar la matriz de comunicación con stakeholders (31) y el cronograma de Marcha Blanca (32).
- **Locución (Juan José):**  
  > *(Slide 31)* "En el Componente 7 cuidamos la comunicación con todas las personas impactadas: enviamos circulares a la administración, instalamos habladores con código QR en recepción para que los huéspedes supieran que podían pedir recomendaciones por WhatsApp, y coordinamos con el equipo de Salgados Café.  
  > *(Slide 32)* Además, no lanzamos el sistema 'a la suerte'. Aplicamos una **Marcha Blanca de 7 días**: durante los primeros 3 días, estuvimos presentes físicamente en la recepción del hotel acompañando cada check-in y resolviendo cualquier duda en tiempo real. Esto eliminó el miedo inicial del personal y aseguró una transición impecable."

---

### Diapositivas 33 y 34/36 — Componente 8: Resultados Consolidados y Dictamen Formal
- **Tiempo:** 17:50 – 18:40 (50 s)
- **Acción visual:** Resumir los criterios de cierre superados (33) y mostrar las tres firmas en el Acta oficial (34).
- **Locución (Juan José):**  
  > *(Slide 33)* "Llegamos al Componente 8: Cierre y Aceptación. Los resultados hablan por sí solos: cero sobreventas en producción, catálogo dinámico de tarifas funcionando, respaldos nocturnos activos y personal 100% capacitado. Los riesgos residuales que identificamos son de impacto muy bajo y tienen plan de contingencia documentado.  
  > *(Slide 34)* Por todas estas evidencias, el Comité de Transición emitió el **Dictamen Formal de Aprobación Sin Salvedades**, ratificado en el Acta de Puesta en Servicio firmada por la Dirección de Tecnología, el Scrum Master y la Gerencia del Hotel Torre Satori."

---

### Diapositivas 35 y 36/36 — Retorno de Inversión (ROI), Conclusión y Preguntas
- **Tiempo:** 18:40 – 19:30 (50 s)
- **Acción visual:** Señalar con fuerza los 4 indicadores macro de impacto (+28%, -80%, 0.0%, 100%) y cerrar en la Slide 36.
- **Locución (Juan José):**  
  > *(Slide 35)* "Para finalizar, quiero que miremos el impacto real en el negocio:  
  > **-80% de carga administrativa**: tareas de registro que antes tomaban 15 minutos en papel ahora se hacen en menos de 1 minuto;  
  > **0.0% de sobreventas**: protegemos la reputación del hotel con matemática relacional;  
  > **+28% de ventas nocturnas proyectadas**: porque el chatbot en WhatsApp no duerme y cotiza al instante;  
  > y un **100% de soberanía tecnológica**: el hotel no paga suscripciones de 100 dólares mensuales a plataformas extranjeras, ahorrando más de 15 millones de pesos al año.  
  > *(Slide 36)* Torre Satori PMS demuestra que la rigurosidad de ITIL 4 no es burocracia: es el puente que convierte un buen desarrollo de software en un servicio hotelero confiable, rentable y con alma humana.  
  > Muchísimas gracias. Quedamos a total disposición del jurado para sus preguntas."

---

## BANCO DE PREGUNTAS TÍPICAS DEL JURADO Y RESPUESTAS ASIGNADAS

### Pregunta 1 (Para Juan Felipe Garzón — Dev Team / Concurrencia):
**Jurado:** *"¿Por qué decidieron resolver el candado en PostgreSQL con `btree_gist` en lugar de usar Redis o bloqueos en memoria a nivel de aplicación?"*  
**Respuesta humana y didáctica:**  
> "Es una excelente pregunta, profesor. Inicialmente evaluamos Redis porque es muy popular para bloqueos rápidos en memoria. Sin embargo, al analizar la realidad del hotel, nos dimos cuenta de dos problemas:  
> Primero, introducíamos una segunda base de datos en el servidor, aumentando el consumo de memoria y sumando un punto único de falla: si Redis se caía o reiniciaba, se perdían los bloqueos en curso.  
> Segundo, el riesgo de inconsistencia *split-brain*: si Redis decía que la habitación estaba libre pero en PostgreSQL la transacción se demoraba, podíamos generar colisiones.  
> Al investigar PostgreSQL 16 a fondo, descubrimos que la extensión `btree_gist` nos permitía crear una restricción de exclusión física sobre el ID del cuarto y el rango de fechas (`daterange`). Esto significa que el propio motor relacional evalúa matemáticamente que los intervalos no se crucen en la misma transacción ACID. Además, combinamos esto con expiración inline: al consultar o insertar, el query ignora automáticamente bloqueos que tengan más de 15 minutos.  
> Logramos cero sobreventas con una arquitectura mucho más simple, monolítica y sin dependencias externas."

### Pregunta 2 (Para Esteban Guarín — Scrum Master / Despliegue y Rollback):
**Jurado:** *"Si durante el despliegue nocturno falla una migración de Alembic, ¿cuál es el procedimiento exacto de rollback para no dejar al hotel sin sistema al día siguiente?"*  
**Respuesta humana y didáctica:**  
> "En ITIL 4, ningún cambio a producción se autoriza si no tiene un plan de reversión probado. Nuestro protocolo funciona así:  
> Antes de que el contenedor ejecute `alembic upgrade head`, el script de despliegue toma un snapshot físico completo de la base de datos con `pg_dump` y congela el estado previo.  
> Supongamos que a las 22:20 h una migración falla o los contenedores no superan el healthcheck tras 15 minutos de diagnóstico. En ese momento se declara aborto del release.  
> El script de rollback ejecuta `docker compose down`, restaura el snapshot de la base de datos previo al cambio y levanta las imágenes de la versión anterior que ya teníamos etiquetadas en el registro local.  
> Este procedimiento lo cronometramos en nuestras pruebas de contingencia y tardó exactamente **4 minutos con 12 segundos**. A las 22:35 h el hotel ya estaría de nuevo en su versión estable anterior, garantizando que el turno de la mañana a las 6:00 a. m. encuentre el sistema 100% operativo."

### Pregunta 3 (Para Juan José Arias — Product Owner / Negocio y Adopción):
**Jurado:** *"En un hotel pequeño donde el personal está acostumbrado al cuaderno físico, ¿cómo vencieron la resistencia al cambio para que realmente adoptaran el sistema?"*  
**Respuesta humana y didáctica:**  
> "Ese fue precisamente nuestro mayor reto como equipo, profesor. La tecnología más avanzada fracasa si el usuario le tiene miedo a la pantalla.  
> Para vencer esa barrera aplicamos dos estrategias:  
> Primero, **diseñamos con ellos, no para ellos**: cuando diseñamos la pantalla del calendario en React, nos aseguramos de que los colores y la distribución de las 9 habitaciones imitaran visualmente la hoja cuadriculada que ellos ya entendían. Cuando abrieron el sistema por primera vez, no vieron un software extraño; vieron su hotel.  
> Segundo, **acompañamiento humano**: no les enviamos un PDF por correo y nos fuimos. Tuvimos 12 horas de talleres prácticos donde los recepcionistas practicaron situaciones reales, se equivocaron y aprendieron a corregir en un entorno de pruebas seguro. Y durante los primeros 3 días de la Marcha Blanca estuvimos ahí, parados al lado de ellos en el mostrador, dándoles confianza mientras atendían huéspedes reales.  
> Cuando vieron que registrar un check-in que antes les tomaba 15 minutos ahora les tomaba 40 segundos y que las cuentas de café cuadraban solas, la resistencia desapareció. La mejor prueba es que la evaluación de satisfacción del personal fue de 9.4 sobre 10."

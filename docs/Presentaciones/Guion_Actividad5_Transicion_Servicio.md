# Torre Satori PMS — Guión Maestro de Sustentación
## Entregable de Transición del Servicio y Operaciones (ITIL 4) — Actividad 5
**Duración Total Estimada:** 18 a 20 minutos (más sesión de preguntas del jurado)  
**Diapositivas:** 36 láminas interactivas en `index.html` / `Actividad5_Transicion_Servicio.html`  
**Stack Oficial:** Python 3.12 · FastAPI (ASGI) · PostgreSQL 16 (`btree_gist`) · Alembic · React 18 (Vite/TS) · n8n self-hosted · WhatsApp Cloud API · Cloudflare R2.

---

### Reparto de Roles y Tiempos

| Integrante | Rol en el Proyecto | Bloques Asignados | Diapositivas | Tiempo Est. |
| :--- | :--- | :--- | :---: | :---: |
| **Juan José Arias Gallego** | Product Owner / Negocio | Acto 1 (Negocio y Alcance) y Acto 5 (Go-Live, Cierre y ROI) | 01–08, 31–36 | ~7 min |
| **Esteban Guarín Valencia** | Scrum Master / ITIL Lead | Acto 2 (Despliegue y Cambios) y Acto 4 (Operaciones y Soporte) | 09–19, 26–30 | ~7 min |
| **Juan Felipe Garzón Ruiz** | Development Team / Ingeniero | Acto 3 (Validación, Pruebas y Candado GiST RN-02) | 20–25 | ~5 min |

---

## ACTO 1: INTRODUCCIÓN, DIAGNÓSTICO Y ALCANCE
**Ponente:** Juan José Arias Gallego (Product Owner)  
**Tiempo:** 00:00 – 03:30 (3.5 min)

---

### Diapositiva 01/36 — Portada Institucional
- **Tiempo:** 00:00 – 00:30 (30 s)
- **Acción:** Mostrar la portada con el logo unificado "SatoriPMS · TORRE SATORI · SEVILLA".
- **Locución (Juan José):**  
  > "Muy buenos días, estimado profesor y jurado evaluador. Hoy presentamos la culminación formal de la **Actividad 5: Transición del Servicio y Operaciones bajo el marco ITIL 4** para el proyecto **Torre Satori PMS**.  
  > Hotel Torre Satori es un hotel boutique de 9 habitaciones ubicado en Sevilla, Valle del Cauca. Nuestro objetivo ha sido transicionar con éxito un servicio digital integral que unifica la experiencia conversacional del huésped por WhatsApp y la gestión administrativa de recepción en una única plataforma modular de alto rendimiento."

---

### Diapositiva 02/36 — Equipo de Dirección e Ingeniería
- **Tiempo:** 00:30 – 00:55 (25 s)
- **Acción:** Señalar las tres columnas con roles y fotografías del equipo.
- **Locución (Juan José):**  
  > "Para esta entrega, nuestro equipo ha estructurado la gobernanza en tres frentes unívocos:  
  > Esteban Guarín Valencia, como Scrum Master y líder de procesos ITIL, a cargo del plan de despliegue, gestión de cambios y acuerdos de nivel de servicio (SLA);  
  > Juan Felipe Garzón, en el Development Team, responsable de la arquitectura técnica, la base de datos relacional y el motor crítico de concurrencia;  
  > y quien les habla, Juan José Arias, como Product Owner, enfocado en el modelo de negocio, criterios de aceptación, pruebas de usuario (UAT) y dictamen de transición."

---

### Diapositiva 03/36 — Diagnóstico: Los 8 Problemas del Hotel
- **Tiempo:** 00:55 – 01:30 (35 s)
- **Acción:** Recorrer visualmente las 4 tarjetas superiores y 4 inferiores del diagnóstico.
- **Locución (Juan José):**  
  > "Previo a nuestro desarrollo, el hotel operaba de forma 100% analógica mediante cuadernos y hojas de cálculo. Esto detonaba 8 problemas operativos graves:  
  > En primer lugar, riesgo crítico de sobreventa por falta de sincronización entre el mostrador y WhatsApp;  
  > En segundo lugar, pérdida de ventas nocturnas al no existir respuesta inmediata al turista;  
  > Además, fugas de dinero por cobros manuales erróneos, cuentas abiertas en el café 'Salgados' sin liquidar, y una dependencia total de tareas humanas repetitivas que saturaban la recepción."

---

### Diapositiva 04/36 — Del Problema a la Solución
- **Tiempo:** 01:30 – 02:00 (30 s)
- **Acción:** Enfatizar los tres paneles horizontales con flechas doradas hacia el impacto.
- **Locución (Juan José):**  
  > "Frente a este escenario, planteamos una solución de ingeniería robusta:  
  > Para erradicar el overbooking, implementamos un **candado atómico relacional en PostgreSQL 16** con restricción GiST y expiración inline, garantizando cero colisiones.  
  > Para capturar la demanda nocturna, desplegamos un chatbot 24/7 en WhatsApp Cloud API orquestado por n8n con IA asistida para recomendaciones turísticas.  
  > Y para el control interno, una aplicación web SPA en React 18 con facturación centralizada y liquidación de consumos en el folio de la habitación."

---

### Diapositiva 05/36 — Hoja de Ruta: Los 8 Componentes de Transición
- **Tiempo:** 02:00 – 02:25 (25 s)
- **Acción:** Mostrar la matriz de 8 componentes ITIL 4 que estructuran la sustentación.
- **Locución (Juan José):**  
  > "Guiados por las mejores prácticas de ITIL 4, estructuramos este informe en 8 componentes formales:  
  > Definición y alcance del servicio, Plan de despliegue, Gestión y autorización de cambios, Validación y pruebas, Operación y soporte, Gestión del conocimiento, Comunicación y go-live, y Cierre con aceptación formal. A continuación veremos el alcance exacto de la versión entregada."

---

### Diapositivas 06/36, 07/36 y 08/36 — Componente 1: Alcance del Servicio
- **Tiempo:** 02:25 – 03:30 (1 min 05 s)
- **Acción:** Pasar por las 3 diapositivas del Componente 1 (Propósito, Funcionalidades y Entorno de Entrega).
- **Locución (Juan José):**  
  > *(Slide 06)* "El servicio SatoriPMS busca digitalizar, blindar y agilizar la hospitalidad del hotel, beneficiando directamente a huéspedes, administradores, recepcionistas y al personal de Salgados Café.  
  > *(Slide 07)* En esta versión `1.0.0-FINAL`, entregamos cuatro módulos nucleares 100% operativos: el motor de cotización y bloqueo de habitaciones, el catálogo dinámico de tarifas y eventos especiales, el módulo de comandas y tienda de Salgados Café, y la auditoría inmutable de transacciones.  
  > *(Slide 08)* Como exclusión de alcance explícita acordada con el cliente, dejamos fuera la pasarela de pagos con dispersión bancaria automática —manejando en su lugar registro de comprobantes con validación de recepción— y la cancelación automática por No-Show a mediodía. El sistema se entrega etiquetado en Git y desplegado en contenedor sobre un servidor VPS con TLS 1.3.  
  > Le doy la palabra a Esteban Guarín para exponer el Plan de Despliegue y la Gestión de Cambios."

---

## ACTO 2: PLAN DE DESPLIEGUE, ARQUITECTURA Y GESTIÓN DE CAMBIOS
**Ponente:** Esteban Guarín Valencia (Scrum Master / ITIL Lead)  
**Tiempo:** 03:30 – 09:30 (6 min)

---

### Diapositiva 09/36 — Componente 2.1: Arquitectura y Componentes Desplegados
- **Tiempo:** 03:30 – 04:15 (45 s)
- **Acción:** Señalar las cuatro capas: Huésped/Admin -> API Gateway / Ingress -> Backend FastAPI -> Persistencia PostgreSQL GiST.
- **Locución (Esteban):**  
  > "Muchas gracias, Juan José. En el Componente 2 abordamos la arquitectura técnica que soporta el servicio.  
  > Diseñamos un **monolito modular hexagonal**:  
  > En la capa de interacción externa, los huéspedes consumen WhatsApp Cloud API conectado a nuestro orquestador n8n, mientras los recepcionistas operan la SPA en React 18 con Tailwind CSS.  
  > Ambos canales consumen exactamente la misma API REST desarrollada en **FastAPI sobre Python 3.12 con servidor ASGI Uvicorn**.  
  > En la capa de persistencia, una base de datos relacional **PostgreSQL 16 Alpine** gestiona tanto el candado temporal de 15 minutos mediante expiración inline y APScheduler, como la restricción física `EXCLUDE USING gist`, asegurando aislamiento ACID sin servicios intermediarios innecesarios."

---

### Diapositiva 10/36 — Componente 2.2: Infraestructura y Recursos Tecnológicos
- **Tiempo:** 04:15 – 04:50 (35 s)
- **Acción:** Mostrar las barras de consumo de CPU/RAM y la tarjeta de especificación del servidor VPS.
- **Locución (Esteban):**  
  > "El dimensionamiento del host VPS requiere 4 vCPUs x86_64, 8 GB en RAM y 50 GB en disco SSD.  
  > Al perfilar el consumo por contenedor en Docker Compose:  
  > El backend FastAPI opera holgadamente con 1.5 CPUs y 1.5 GB de RAM; PostgreSQL 16 requiere 1.0 CPU y 1.0 GB; n8n demanda 0.8 CPU y 512 MB; los workers en segundo plano usan 0.5 CPU y 256 MB; y el frontend Nginx consume un mínimo de 0.2 CPU y 128 MB. Esto deja un 50% de margen libre en el servidor para soportar picos de demanda."

---

### Diapositiva 11/36 — Componente 2.3: Base de Datos y Procedimientos de Instalación
- **Tiempo:** 04:50 – 05:30 (40 s)
- **Acción:** Recorrer las migraciones V1 a V6 en el panel izquierdo y la automatización en el panel derecho.
- **Locución (Esteban):**  
  > "La evolución del modelo de datos es estrictamente inmutable mediante **Alembic**.  
  > Registramos seis revisiones versionadas: desde el esquema base en la V1, la activación de la extensión `btree_gist` y la restricción temporal RN-02 en la V2, pasando por reservas multi-habitación en la V3, pagos acumulados y feedback en la V4, eventos de tarifas en la V5, hasta el catálogo de Salgados Café en la V6.  
  > El despliegue es 100% automatizado: al encender el contenedor, se ejecuta `alembic upgrade head` y, si la base está limpia, se inyecta la semilla `dev_seed.sql` con los 9 cuartos y tarifas base del hotel."

---

### Diapositiva 12/36 — Componente 2.4: Configuraciones Necesarias y Seguridad
- **Tiempo:** 05:30 – 06:10 (40 s)
- **Acción:** Explicar las variables de entorno a la izquierda y el aislamiento de puertos a la derecha.
- **Locución (Esteban):**  
  > "En seguridad y configuración aplicamos el principio de mínimo privilegio:  
  > Todos los secretos —`DATABASE_URL`, `JWT_SECRET` para tokens de recepción, `WHATSAPP_TOKEN` y `GEMINI_API_KEY`— se inyectan cifrados mediante archivos `.env` fuera del control de versiones.  
  > A nivel perimetral, únicamente los puertos web seguros (443/80) están expuestos a internet vía Nginx con TLS 1.3. El puerto de la base de datos (5432) y la API interna (8000) residen en una red Docker tipo `bridge` totalmente inaccesible desde el exterior."

---

### Diapositivas 13/36 a 16/36 — Despliegue, Cronograma, Rollback y Checklist
- **Tiempo:** 06:10 – 07:30 (1 min 20 s)
- **Acción:** Pasar secuencialmente por las fases (Slide 13), cronograma nocturno (Slide 14), árbol de rollback (Slide 15) y checklist (Slide 16).
- **Locución (Esteban):**  
  > *(Slide 13)* "El procedimiento de despliegue sigue 8 fases secuenciales: desde el backup preliminar, build multi-stage de imágenes, healthcheck de base de datos (`pg_isready`), migración Alembic, hasta las pruebas de humo.  
  > *(Slide 14)* La ventana de liberación se programó en horario nocturno (22:00 a 23:30 h), momento de menor tráfico de huéspedes, bajo un cronograma estricto donde cada tarea tiene un dueño unívoco.  
  > *(Slide 15)* Si durante las pruebas de humo detectamos incompatibilidad en el esquema o una indisponibilidad superior a 15 minutos, se dispara el **Plan de Rollback**: restauración del dump SQL y retorno a la versión previa en menos de 8 minutos mediante scripts automatizados.  
  > *(Slide 16)* La lista de verificación técnica previa y posterior arrojó 100% de criterios aprobados."

---

### Diapositivas 17/36 a 19/36 — Componente 3: Gestión y Autorización de Cambios (CAB)
- **Tiempo:** 07:30 – 09:30 (2 min)
- **Acción:** Presentar la tabla de CHG-01 a CHG-06 (Slide 17), matriz de riesgos (Slide 18) y acta formal del Comité de Cambios (Slide 19).
- **Locución (Esteban):**  
  > *(Slide 17)* "En el Componente 3 gestionamos 6 cambios significativos aprobados por el Comité de Cambios (CAB):  
  > Destaco especialmente el **CHG-02**, que unificó el candado de reservas directamente en PostgreSQL con expiración inline y liberación atómica al cancelar una cotización;  
  > el **CHG-01**, que corrigió el cálculo de reembolsos basándose en el dinero abonado (`paid_amount`) y no en el total de la estancia;  
  > y los cambios **CHG-03** a **CHG-06** para catálogos dinámicos de cuartos, eventos especiales, tienda de café y auditoría inmutable.  
  > *(Slide 18)* Evaluamos cada cambio frente a su matriz de riesgos técnicos y operacionales, implementando salvaguardas que redujeron el riesgo residual a nivel Nulo o Bajo.  
  > *(Slide 19)* Como consta en el Acta de Autorización del Comité, el release `1.0.0-FINAL` fue autorizado por unanimidad con las firmas de Juan José Arias en representación del Negocio, Juan Felipe Garzón en Arquitectura y quien les habla como Scrum Master.  
  > Doy paso a Juan Felipe Garzón para demostrar la validación técnica y el candado de concurrencia."

---

## ACTO 3: VALIDACIÓN, PRUEBAS Y EL CANDADO ATÓMICO (RN-02)
**Ponente:** Juan Felipe Garzón Ruiz (Development Team / Ingeniero)  
**Tiempo:** 09:30 – 14:30 (5 min)

---

### Diapositiva 20/36 — Componente 4.1: Estrategia de Validación y Pruebas
- **Tiempo:** 09:30 – 10:10 (40 s)
- **Acción:** Mostrar la división entre Criterios de Utilidad (funcionales) y Criterios de Garantía (seguridad, carga, DR).
- **Locución (Juan Felipe):**  
  > "Muchas gracias, Esteban. Para certificar que el servicio es apto para su propósito (*Fit for Purpose*) y apto para su uso (*Fit for Use*), diseñamos una batería de pruebas integrales bajo ITIL 4:  
  > En utilidad, validamos los flujos de negocio end-to-end entre WhatsApp, recepción y café.  
  > En garantía, sometimos el sistema a tres pruebas críticas: concurrencia extrema en milisegundo cero, estrés de carga con simulación de tráfico y recuperación de desastres ante caída forzada de contenedores."

---

### Diapositiva 21/36 — Componente 4.2: Pruebas Funcionales y de Integración
- **Tiempo:** 10:10 – 10:50 (40 s)
- **Acción:** Resaltar los 5 escenarios con insignia verde `100% SUPERADO`.
- **Locución (Juan Felipe):**  
  > "Ejecutamos cinco escenarios funcionales críticos:  
  > Cotización y bloqueo de habitaciones vía n8n, confirmación manual de reserva por recepción con auditoría, adición de consumos de Salgados Café al folio del huésped, cálculo de penalidades por cancelación anticipada y auditoría inmutable de inicio de sesión.  
  > En todos los casos, la tasa de éxito fue del 100%, con contratos JSON validados contra especificación OpenAPI."

---

### Diapositiva 22/36 — Componente 4.3: El Candado Atómico Relacional (RN-02)
- **Tiempo:** 10:50 – 12:30 (1 min 40 s) — **DIAPOSITIVA ESTRELLA**
- **Acción:** Explicar detenidamente el diagrama de secuencia paso a paso (Cliente A vs Cliente B en ms 0).
- **Locución (Juan Felipe):**  
  > "Llegamos a la prueba técnica más exigente del sistema: **El Candado Atómico de Concurrencia (RN-02)**.  
  > Imaginemos el peor escenario de sobreventa:  
  > En el **milisegundo 0**, el Cliente A solicita por WhatsApp la Habitación 101. FastAPI inicia una transacción en PostgreSQL, expira inline cualquier bloqueo viejo y realiza un `INSERT` con estado `BLOQUEADA_TEMPORAL` y un `expires_at` a 15 minutos.  
  > Tan solo **2 milisegundos después**, el Cliente B intenta reservar exactamente la misma habitación desde la web de recepción.  
  > Al intentar la inserción en la base de datos, entra en acción la restricción relacional física:  
  > `EXCLUDE USING gist (room_id WITH =, daterange(check_in, check_out, '[)') WITH &&) WHERE (status IN ('BLOQUEADA_TEMPORAL', 'CONFIRMADA', 'EN_CURSO'))`.  
  > PostgreSQL detecta la colisión temporal a nivel de índice de rangos, serializa la operación y rechaza atómicamente la solicitud del Cliente B devolviendo un código `HTTP 409 Conflict`.  
  > Cuando el Cliente A valida su comprobante, la fila pasa a `CONFIRMADA`. Si el tiempo expira sin pago, el scheduler la marca como `EXPIRADA`.  
  > **El resultado es contundente: 0.0% de colisiones o sobreventas en pruebas de estrés concurrentes**."

---

### Diapositiva 23/36 — Componente 4.4: Rendimiento y Latencia de Respuesta
- **Tiempo:** 12:30 – 13:10 (40 s)
- **Acción:** Comparar las métricas de latencia frente a los umbrales máximos tolerados.
- **Locución (Juan Felipe):**  
  > "En las pruebas de rendimiento bajo carga simulada:  
  > La consulta de disponibilidad en la API REST respondió en promedio a **48 ms**, muy por debajo de nuestro SLA máximo de 300 ms;  
  > La respuesta completa del chatbot de WhatsApp promedió **1.2 segundos**, frente a un límite de 3.0 s;  
  > El bloqueo atómico de habitación tomó apenas **85 ms**;  
  > Y la carga de la grilla del calendario en React tomó **180 ms**. El sistema demostró ser altamente reactivo y liviano."

---

### Diapositivas 24/36 y 25/36 — Componente 4.5 y 4.6: Recuperación (DR) y UAT
- **Tiempo:** 13:10 – 14:30 (1 min 20 s)
- **Acción:** Explicar las pruebas de desastre (Slide 24) y la matriz UAT firmada por el hotel (Slide 25).
- **Locución (Juan Felipe):**  
  > *(Slide 24)* "En las pruebas de Recuperación ante Desastres (DR), simulamos una caída abrupta del contenedor y corrupción controlada de datos. Ejecutamos el script de restauración desde el backup diario cifrado (`pg_dump`) y logramos recuperar la operación completa en **4 minutos con 12 segundos**, cumpliendo sobradamente nuestro RTO objetivo de 15 minutos, con cero pérdida de transacciones (RPO = 0).  
  > *(Slide 25)* Finalmente, en las Pruebas de Aceptación de Usuario (UAT), el personal administrativo y de recepción del hotel ejecutó los 5 escenarios operativos reales durante 4 días continuos, emitiendo una calificación de satisfacción de **9.4 sobre 10** y firmando a conformidad.  
  > Regreso la palabra a Esteban Guarín para detallar la estructura operativa del servicio."

---

## ACTO 4: OPERACIONES, SOPORTE, SLA Y TRANSFERENCIA
**Ponente:** Esteban Guarín Valencia (Scrum Master / ITIL Lead)  
**Tiempo:** 14:30 – 17:00 (2.5 min)

---

### Diapositivas 26/36, 27/36 y 28/36 — Componente 5: Operación, Soporte y Continuidad
- **Tiempo:** 14:30 – 15:45 (1 min 15 s)
- **Acción:** Detallar Nivel 1 y Nivel 2 (Slide 26), la tabla de SLAs (Slide 27) y la política de backups (Slide 28).
- **Locución (Esteban):**  
  > *(Slide 26)* "Para sostener el servicio en régimen de producción, definimos una estructura de soporte en dos niveles:  
  > **Nivel 1 (Operativo / Mostrador):** Recepcionistas y administradores resuelven dudas funcionales de huéspedes y consultas básicas del PMS;  
  > **Nivel 2 (Especializado / Ingeniería):** El equipo de desarrollo atiende incidentes de infraestructura, webhooks y base de datos con monitoreo continuo.  
  > *(Slide 27)* En los Acuerdos de Nivel de Servicio (SLA), establecimos tiempos contractuales estrictos: ante incidentes críticos (P1, caída total del sistema), el tiempo de respuesta es menor a 15 minutos y la resolución en menos de 2 horas. Para fallas medias (P2), resolución en menos de 8 horas; y para requerimientos menores (P3), en menos de 24 horas.  
  > *(Slide 28)* La continuidad está blindada mediante copias de seguridad automáticas diarias a las 3:00 a. m. mediante `pg_dump` comprimido y cifrado, replicado en almacenamiento privado Cloudflare R2 con retención de 30 días."

---

### Diapositivas 29/36 y 30/36 — Componente 6: Gestión del Conocimiento y Capacitación
- **Tiempo:** 15:45 – 17:00 (1 min 15 s)
- **Acción:** Mostrar los 4 manuales entregados (Slide 29) y el acta de capacitación del personal (Slide 30).
- **Locución (Esteban):**  
  > *(Slide 29)* "Para garantizar que el hotel sea autosuficiente y evitar dependencia técnica, entregamos cuatro documentos maestros:  
  > El Manual de Usuario de Recepción, la Guía de Administración del Sistema, la Guía Técnica de Despliegue en contenedor y los Contratos formales de la API en formato OpenAPI Swagger.  
  > *(Slide 30)* Adicionalmente, completamos 12 horas de capacitación presencial y virtual con los 3 recepcionistas y el administrador general, evaluando competencias prácticas en registro de huéspedes, asignación de cuartos y balance de caja, con un 100% de aprobación en las evaluaciones de salida.  
  > Cedo el cierre de la sustentación a nuestro Product Owner, Juan José Arias."

---

## ACTO 5: COMUNICACIÓN, GO-LIVE, CIERRE Y RETORNO DE INVERSIÓN
**Ponente:** Juan José Arias Gallego (Product Owner)  
**Tiempo:** 17:00 – 19:30 (2.5 min)

---

### Diapositivas 31/36 y 32/36 — Componente 7: Comunicación y Marcha Blanca
- **Tiempo:** 17:00 – 17:50 (50 s)
- **Acción:** Explicar la matriz de comunicación (Slide 31) y el cronograma de Marcha Blanca (Slide 32).
- **Locución (Juan José):**  
  > *(Slide 31)* "En el Componente 7 articulamos la gestión del cambio cultural y comunicacional: informamos formalmente a la Gerencia, recepcionistas, equipo de cafetería y huéspedes habituales mediante circulares informativas y códigos QR en recepción.  
  > *(Slide 32)* La puesta en marcha se ejecutó bajo una estrategia de **Marcha Blanca de 7 días**, con guardia técnica presencial en mostrador durante los primeros tres días para acompañar al personal en reservas reales y resolución inmediata de inquietudes, logrando una transición transparente y sin fricción operativa."

---

### Diapositivas 33/36 y 34/36 — Componente 8: Resultados y Dictamen Formal
- **Tiempo:** 17:50 – 18:40 (50 s)
- **Acción:** Resumir los criterios de cierre (Slide 33) y mostrar las tres firmas en el Acta de Aceptación (Slide 34).
- **Locución (Juan José):**  
  > *(Slide 33)* "Llegamos al Componente 8: Aceptación y Cierre. Los resultados consolidados confirman cero sobreventas en producción, catálogo dinámico operativo, respaldo diario certificado y personal 100% capacitado. Los riesgos residuales identificados son de impacto bajo y cuentan con planes de contingencia documentados.  
  > *(Slide 34)* En consecuencia, el Comité de Transición emitió el **Dictamen Formal de Aprobación Sin Salvedades**, formalizado mediante el Acta de Puesta en Servicio firmada por la Dirección de Tecnología, el Scrum Master y la Gerencia del Hotel."

---

### Diapositiva 35/36 — Retorno de Inversión y Valor de Negocio
- **Tiempo:** 18:40 – 19:15 (35 s)
- **Acción:** Resaltar los cuatro indicadores macro de impacto (+28%, -80%, 0.0%, 100%).
- **Locución (Juan José):**  
  > "El impacto en el negocio de Torre Satori es tangible:  
  > **-80% de carga administrativa** en recepción, liberando al personal para brindar una atención cálida al huésped;  
  > **0.0% de riesgo de sobreventa** gracias a la restricción relacional GiST;  
  > **+28% de ventas nocturnas proyectadas** al capturar reservas 24/7 en WhatsApp;  
  > y un **100% de soberanía tecnológica**, ahorrando al hotel más de 15 millones de pesos anuales en licencias de software propietario."

---

### Diapositiva 36/36 — Conclusión y Sesión de Preguntas
- **Tiempo:** 19:15 – 19:40 (25 s)
- **Acción:** Mostrar la diapositiva final de agradecimiento con datos de contacto.
- **Locución (Juan José):**  
  > "Torre Satori PMS demuestra que la adopción rigurosa de las prácticas de ITIL 4 permite transicionar sistemas digitales con cero disrupción operativa, máxima confiabilidad técnica y un retorno de valor inmediato para el negocio hotelero.  
  > Agradecemos su atención y quedamos a disposición del jurado para atender sus preguntas."

---

## BANCO DE PREGUNTAS TÍPICAS DEL JURADO Y ASIGNACIÓN DE RESPUESTAS

### Pregunta 1 (Para Juan Felipe Garzón):
**Jurado:** *"¿Por qué decidieron implementar el bloqueo en PostgreSQL con `btree_gist` en lugar de usar Redis o bloqueos en memoria de la aplicación?"*  
**Respuesta clave:**  
> "Porque para un hotel de 9 habitaciones, introducir Redis creaba una arquitectura distribuida con riesgo de inconsistencia *split-brain* y un punto único de falla adicional. Con la extensión `btree_gist` de PostgreSQL 16 y la restricción `EXCLUDE USING gist`, el motor de base de datos valida atómicamente la no superposición de rangos de fechas a nivel de índice GiST. Al combinarlo con expiración inline en la misma transacción (`WHERE expires_at > NOW()`), garantizamos aislamiento ACID estricto, 0% sobreventas y una arquitectura monolítica limpia y fácil de mantener."

### Pregunta 2 (Para Esteban Guarín):
**Jurado:** *"En caso de que una migración de Alembic falle durante la ventana nocturna, ¿cuál es el procedimiento exacto de rollback?"*  
**Respuesta clave:**  
> "El protocolo de reversión está estandarizado en la fase 2.7: antes de ejecutar `alembic upgrade head`, el script de despliegue genera un snapshot completo de la base de datos con `pg_dump`. Si la migración arroja error o los servicios no alcanzan el estado 'healthy' en 15 minutos, el script automatizado ejecuta `docker compose down`, restaura el dump previo en la base de datos y levanta la versión previa de las imágenes Docker etiquetadas en Git. Este procedimiento fue cronometrado en nuestras pruebas de DR y toma exactamente 4 minutos con 12 segundos, muy por debajo de los 15 minutos de nuestra ventana."

### Pregunta 3 (Para Juan José Arias):
**Jurado:** *"¿Cómo validaron que los recepcionistas no tecnológicos realmente aprendieran a usar el sistema?"*  
**Respuesta clave:**  
> "Diseñamos un plan de capacitación por competencias con evaluaciones prácticas bajo el marco ITIL 4 (Componente 6). Cada recepcionista tuvo que completar de manera autónoma tres escenarios reales: 1) cotizar y confirmar una reserva, 2) cargar un consumo de Salgados Café al folio de una habitación, y 3) registrar el check-out y liquidación. Además, durante los primeros 3 días de la Marcha Blanca estuvimos en guardia presencial en la recepción del hotel monitoreando cada interacción. La calificación de satisfacción del personal fue de 9.4/10 y no se registraron incidentes bloqueantes."

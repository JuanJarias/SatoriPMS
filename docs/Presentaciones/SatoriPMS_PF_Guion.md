# Guion de Presentación Final — SatoriPMS

- **Público:** Dueño del Hotel Torre Satori (Sevilla, Valle del Cauca) y evaluación de Proyecto Integrador II.
- **Tono:** Claro, cercano al negocio y sin tecnicismos innecesarios. El guion **complementa** las diapositivas (no repite textualmente lo que se lee en pantalla).
- **Duración total:** **13 min 25 s (805 s)** — más de 1 minuto y medio de margen bajo el límite de 15 minutos.
- **Reparto equilibrado:**
  - **Esteban Guarín Valencia** (*Scrum Master*): Apertura, **Chatbot WhatsApp (n8n)**, **Disponibilidad y soporte por tickets**, Mejoras y Cierre (~4 min).
  - **Juan José Arias Gallego** (*Product Owner*): Necesidades del negocio, **Aplicación web (Frontend)**, Costos y ROI (~5 min).
  - **Juan Felipe Garzón Trejos** (*Development Team*): Arquitectura, doble candado, seguridad, **pruebas/rendimiento** y resultados (~4 min 30 s).

---

## Bloque 1 · Apertura y Pregunta 1: ¿Qué necesidad identificamos?

### Slide 01 — SatoriPMS *(15 s · Esteban)*
> "Buenos días. Hoy venimos a presentarles **SatoriPMS**, la plataforma diseñada a la medida para el Hotel Torre Satori en Sevilla. Nuestro propósito fue claro desde el primer día: darles claridad operativa y permitir que el hotel atienda y venda sin límites de horario."

### Slide 02 — Equipo del proyecto *(25 s · Esteban)*
> "El proyecto fue construido por tres frentes claros: Juan José Arias desde la visión de negocio y la aplicación web; Juan Felipe Garzón en la arquitectura, base de datos y pruebas; y quien les habla, Esteban Guarín, en la automatización por WhatsApp con n8n y la continuidad del servicio. Le doy paso a Juan José para recordar el punto de partida."

### Slide 03 — Contexto del hotel *(35 s · Juan José Arias)*
> "Cuando analizamos la operación diaria en Sevilla, encontramos un hotel boutique con nueve habitaciones, tienda y Salgados Café operando únicamente por mostrador y un WhatsApp personal, sin una base de datos centralizada donde cruzar esa información."

### Slide 04 — Necesidades identificadas *(40 s · Juan José Arias)*
> "Ese esquema generaba cinco dolores concretos. El más crítico era el riesgo de vender la misma noche dos veces cuando llegaban consultas por distintos lados, además de perder reservas de madrugada y calcular precios o reembolsos manualmente."

### Slide 05 — Impacto en el negocio *(35 s · Juan José Arias)*
> "Esto le pegaba directo al bolsillo y a la reputación del hotel: una sola sobreventa daña la confianza del huésped, depender de agencias externas cuesta un 18 % por noche, y registrar manualmente cada llegada quitaba tiempo valioso en recepción."

### Slide 06 — Objetivo y alcance *(30 s · Juan José Arias)*
> "Por eso nos propusimos un objetivo sencillo: que el viajero reserve a cualquier hora por WhatsApp sin descargar aplicaciones, y que ustedes controlen habitaciones, cafetería y finanzas en un solo lugar. Juan Felipe les explicará cómo lo diseñamos."

---

## Bloque 2 · Pregunta 2: ¿Qué solución diseñamos y cómo la construimos?

### Slide 07 — Arquitectura de la solución *(45 s · Juan Felipe Garzón)*
> "Para que todo funcione sin enredos, conectamos ambos canales —el WhatsApp del huésped y la pantalla web de recepción— a un mismo cerebro central. Así, cuando alguien consulta o reserva por WhatsApp, recepción lo ve al instante porque ambos leen exactamente los mismos datos."

### Slide 08 — Control de sobreventas *(45 s · Juan Felipe Garzón)*
> "Miren el recorrido de una habitación. El viajero A la elige y queda apartada 15 minutos; si entrega sus datos pasa a pendiente de pago y tiene 24 horas con el link de Wompi; cuando el pago se aprueba queda confirmada. Si no avanza o no paga a tiempo, la habitación se libera sola. Mientras tanto, si el viajero B pide las mismas fechas, PostgreSQL aplica una regla física que prohíbe cruzar fechas en la misma habitación y lo rechaza de inmediato con un error 409, incluso si fallara la red. Resultado: cero sobreventas."

### Slide 09 — Decisiones de diseño *(40 s · Juan Felipe Garzón)*
> "Tomamos cuatro decisiones pensando en su tranquilidad: separar los mensajes del chatbot para ajustarlos rápido; obligar a la inteligencia artificial a ofrecer solo habitaciones realmente libres; cobrar con link externo de Wompi para no tocar datos de tarjetas; y usar tecnología abierta sin licencias. Ahora Esteban les muestra cómo funciona el canal de WhatsApp."

---

## Bloque 3 · Pregunta 3: ¿Qué implementamos y cómo demostramos que funciona?

### Slide 10 — Alcance implementado (v1.0.0) *(35 s · Esteban)*
> "El producto final se divide en dos experiencias conectadas: el huésped se autoatiende por WhatsApp las 24 horas para reservar, pagar, cancelar o dejar reseña; y el personal del hotel opera todo el negocio desde la web, incluida la bandeja para pausar el bot y responder a un huésped."

### Slide 11 — Reserva por WhatsApp (n8n) *(55 s · Esteban)*
> "En nuestro flujo de n8n, el huésped elige fechas, ve habitaciones libres y en ese instante la habitación queda apartada 15 minutos. Si otra persona pide esa misma habitación al mismo tiempo, el sistema la rechaza de inmediato. Después se piden los datos con el aviso de la Ley 1581, se cotiza con recargos y eventos, y se envía el link de Wompi con su código `TS-XXXX`; la reserva queda confirmada cuando el pago se aprueba. Ahora Juan José les muestra cómo lo ve recepción en la web."

### Slide 12 — Operación en aplicación web *(55 s · Juan José Arias)*
> "Apenas se confirma el pago, la reserva aparece en el calendario web sin digitar nada. El día de llegada, recepción hace el check-in, registra pedidos de Salgados Café cargados directo a la habitación, aplica tarifas de eventos especiales en segundos y todo queda guardado en la bitácora para que la gerencia sepa qué hizo cada usuario. Juan Felipe cierra esta parte con seguridad y pruebas."

### Slide 13 — Seguridad y protección de datos *(40 s · Juan Felipe Garzón)*
> "En seguridad separamos permisos: solo el administrador modifica tarifas o habitaciones, mientras recepción opera el día a día. Cumplimos la Ley 1581 enmascarando documentos y validando cada pago con firma criptográfica de Wompi."

### Slide 14 — Validación y pruebas *(35 s · Juan Felipe Garzón)*
> "No solo lo decimos, lo probamos sobre la versión final: aprobaron las 37 pruebas del servidor, las 4 pruebas de la web con navegador real, los 65 escenarios del chatbot, las 11 pruebas de pagos con Wompi y los 7 flujos reales en vivo de punta a punta."

### Slide 15 — Concurrencia y rendimiento *(35 s · Juan Felipe Garzón)*
> "Lo medimos sobre la versión final. Con 50 solicitudes simultáneas sobre la misma habitación, el sistema aceptó una y rechazó las otras 49: cero dobles reservas. Las cotizaciones respondieron en menos de 0,4 segundos, y una reserva nueva aparece en la web en menos de una décima de segundo porque WhatsApp y recepción leen la misma base de datos. Le paso la palabra a Juan José para revisar los números."

---

## Bloque 4 · Pregunta 4: ¿Qué recursos demandó y cómo se sostiene?

### Slide 16 — Inversión del proyecto *(35 s · Juan José Arias)*
> "Construir el sistema tomó 600 horas de ingeniería, equivalentes a 24,7 millones de pesos de inversión total, con el 85 % dedicado a construcción y cero pesos en licencias de software."

### Slide 17 — Costos de operación mensual *(35 s · Juan José Arias)*
> "Lo más atractivo para Torre Satori es el mantenimiento mensual: mientras un sistema comercial cuesta cerca de 1,37 millones al mes, operar SatoriPMS cuesta menos de 290 mil pesos incluyendo servidor, WhatsApp, IA y 5 horas de soporte. Esteban les explica cómo garantizamos que nunca se detenga."

### Slide 18 — Disponibilidad, fallos y soporte *(50 s · Esteban)*
> "El servicio apunta a una disponibilidad superior al 99,5 %, con un respaldo cifrado cada madrugada a las 3:00 a. m. en almacenamiento externo, y la restauración de un respaldo la probamos en menos de un segundo con los datos actuales. Si llegara a fallar la IA, el chatbot pasa automáticamente al menú guiado; si fallara Meta, recepción sigue operando desde la web. Además, ustedes cuentan con soporte en dos niveles y un canal de tickets con tiempos de respuesta menores a 15 minutos para fallos críticos."

---

## Bloque 5 · Pregunta 5: ¿Qué resultados alcanzamos y qué mejorar?

### Slide 19 — Resultados alcanzados *(30 s · Juan Felipe Garzón)*
> "Al cierre, las cinco necesidades iniciales quedaron cubiertas, el personal completó la capacitación al 100 % y el sistema cuenta con dictamen de piloto autorizado."

### Slide 20 — Retorno de la inversión *(35 s · Juan José Arias)*
> "Financieramente, el ahorro frente a un software comercial supera los 13 millones al año: la inversión se recupera en menos de 14 meses y con apenas 3 reservas directas al mes se cubren todos los costos técnicos."

### Slide 21 — Oportunidades de mejora *(30 s · Esteban)*
> "Como hoja de ruta v1.2.0 queda pasar la pasarela a producción con facturación electrónica DIAN, automatizar reseñas en Google, activar alertas de errores en producción y escalar a múltiples servidores cuando el hotel crezca."

### Slide 22 — Cierre *(25 s · Esteban)*
> "En resumen, Torre Satori pasa de atender en libreta a vender 24/7 con cero sobreventas, sobre una plataforma que ya está lista para el piloto. Gracias por su confianza y por acompañarnos en este proceso. Muchas gracias."

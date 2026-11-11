# Guía de Dominio Técnico y Criterios para Telemáticos: SatoriPMS

**Perfil de referencia:** Ingeniero Telemático (fortaleza en redes, protocolos, capas OSI, concurrencia física y arquitectura cliente-servidor; conocimientos iniciales en desarrollo web, ORMs y n8n).  
**Propósito:** Proveer las analogías, conceptos clave, recursos de estudio directo y plantillas de criterio para supervisar, construir o instruir al agente en modo **AGY** con autoridad y solvencia en la sustentación del Sprint 5.

---

## 1. El Puente Mental: De Telemática a Desarrollo de Software

Como telemático ya dominas conceptos de bajo nivel que muchos desarrolladores puros no comprenden en profundidad. Traduzcamos la jerga de desarrollo a conceptos de telecomunicaciones y redes:

| Concepto de Telemática / Redes | Equivalente en SatoriPMS | Explicación en Términos Telemáticos |
| :--- | :--- | :--- |
| **Cabecera de Trama / Paquete (IP/TCP)** | **Schemas de Pydantic** | Estructura formal de datos que define qué campos, tipos y bytes son válidos. Si un campo no cumple el protocolo (ej. falta `check_in`), se descarta en la frontera con error HTTP 422. |
| **Multiplexación por División de Frecuencias / Time-Slots** | **`EXCLUDE USING gist (daterange)`** | Evitar que dos señales ocupen el mismo canal al mismo tiempo. En la DB, el índice GiST impide que dos registros de reserva compartan el mismo `room_id` y solapen su rango de fechas `[check_in, check_out)`. |
| **Sockets No Bloqueantes / `epoll` / `select`** | **FastAPI con `async` / `await`** | En lugar de asignar un hilo por conexión (como hacía Java Tomcat tradicional), FastAPI corre en un *Event Loop* asíncrono (Uvicorn). Cuando la API espera a la base de datos o a Meta, libera el hilo para atender otras peticiones sin consumir memoria. |
| **Handshake / Firma de Paquete Criptográfica** | **HMAC SHA-256 (`X-Hub-Signature-256`)** | Similar a IPSec o autenticación de paquetes con clave compartida. El emisor (pasarela) concatena el cuerpo JSON con un secreto y calcula un hash SHA-256. El receptor recalcula el hash; si no coincide bit a bit, el paquete fue alterado o falsificado (se rechaza con HTTP 401). |
| **Token Stateless (tipo Kerberos / Ticket)** | **JSON Web Token (JWT)** | Un ticket firmado criptográficamente que el cliente guarda. En cada petición HTTP lo envía en la cabecera `Authorization: Bearer <token>`. El servidor no consulta la base de datos para saber quién es; solo verifica la firma matemática con su clave simétrica `JWT_SECRET`. |
| **Controlador de Tráfico / Enrutador de Mensajes** | **Flujo n8n** | Un multiplexor/demultiplexor visual de eventos. Recibe una trama HTTP push (webhook de Meta), extrae los datos del mensaje, consulta la API interna y reenvía la respuesta al gateway de WhatsApp. |
| **Polling vs. Push (Interrupción)** | **TanStack Query (Polling) vs. Webhook** | El webhook es una interrupción por hardware/red: un evento externo dispara una llamada HTTP. El polling es una consulta periódica por temporizador (ej. el navegador pregunta cada 5s "¿hay nuevas reservas?"). |

---

## 2. Tecnologías, Conceptos y Recursos Clave a Consultar

### A. FastAPI y Pydantic (Backend Python 3.12)
* **Qué es:** Framework web ultraligero basado en estándares abiertos (OpenAPI y JSON Schema).
* **Conceptos esenciales:**
  1. **Rutas y Códigos HTTP:** `@app.get("/rooms/availability")` (consulta idempotente 200), `@app.post("/bookings/lock")` (creación 200, o conflicto 409).
  2. **Inyección de Dependencias (`Depends`):** Similar a un filtro o middleware de red. Permite inyectar la sesión de base de datos (`get_db`) o verificar el token JWT del usuario (`require_role("Recepcionista")`) antes de ejecutar la lógica de la función.
  3. **Pydantic Models:** Clases como `LockRequest(BaseModel)` con validaciones automáticas de tipos de datos.
* **Recursos para consultar (30 min de lectura):**
  * [Tutorial Oficial de FastAPI - First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
  * [FastAPI - Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
  * [Pydantic Documentation - Basics](https://docs.pydantic.dev/latest/concepts/models/)

### B. PostgreSQL 16, SQLAlchemy 2.0 y Alembic (Persistencia y Concurrencia)
* **Qué es:** PostgreSQL es el motor relacional; SQLAlchemy 2.0 es el ORM (mapea tablas SQL a clases Python); Alembic es el sistema de control de versiones del esquema de base de datos (como un git para tablas SQL).
* **Conceptos esenciales:**
  1. **Migraciones con Alembic:** Scripts numerados (`001_initial_schema.py`) que ejecutan `upgrade()` para crear tablas y restricciones, y `downgrade()` para revertir.
  2. **Restricción `EXCLUDE USING gist` (RN-02):** Requiere la extensión `btree_gist`. Se define como:
     ```sql
     CONSTRAINT no_overlapping_active_bookings 
     EXCLUDE USING gist (
         room_id WITH =, 
         daterange(check_in, check_out, '[)') WITH &&
     ) 
     WHERE (status IN ('BLOQUEADA_TEMPORAL', 'CONFIRMADA', 'EN_CURSO'));
     ```
     *`WITH =`*: Misma habitación.  
     *`WITH &&`*: Rangos de fechas que se intersecan.  
     *`'[)'`*: Incluye día de entrada, excluye día de salida (permite salida a las 11:00 y entrada a las 15:00 el mismo día).  
     *`WHERE`*: Solo aplica a estados activos; cuando pasa a `CANCELADA` o `EXPIRADA`, PostgreSQL libera el rango instantáneamente.
  3. **Transacción Atómica (`commit` / `rollback`):** En una sola transacción SQL: expira bloqueos viejos de esa habitación (`UPDATE booking SET status='EXPIRADA' WHERE expires_at < NOW()`) e inserta el nuevo bloqueo. Si algo falla, nada se aplica.
* **Recursos para consultar:**
  * [PostgreSQL Docs - Exclusion Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION)
  * [PostgreSQL Docs - Range Types](https://www.postgresql.org/docs/current/rangetypes.html)
  * [Alembic Tutorial - Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

### C. n8n y WhatsApp Cloud API (Orquestación del Chatbot)
* **Qué es:** n8n es una plataforma de automatización de flujos de trabajo basada en eventos. WhatsApp Cloud API es la API REST oficial de Meta para enviar y recibir mensajes de WhatsApp empresarial.
* **Conceptos esenciales:**
  1. **Webhook de Meta:** Meta envía un `POST` HTTPS a n8n cada vez que el usuario escribe un mensaje.
  2. **Verificación de Webhook (`hub.challenge`):** Al configurar Meta, este hace un `GET` con `hub.mode=subscribe`, `hub.verify_token=tu_token` y `hub.challenge=un_numero`. El endpoint debe responder únicamente con el valor de `hub.challenge` para confirmar que la URL te pertenece.
  3. **Normalización en n8n:** El payload de Meta es complejo y anidado (`entry[0].changes[0].value.messages[0]`). n8n extrae el número de teléfono (`wa_id`) y el texto (`body`) y hace una petición HTTP limpia hacia FastAPI (`/api/v1/...`).
  4. **Eliminación de Redis:** El flujo no almacena nada en Redis; guarda el historial y la fase de la conversación en FastAPI en la tabla `conversation` con un campo JSONB (`session_data`).
* **Recursos para consultar:**
  * [Meta Developers - Get Started with WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started)
  * [n8n Docs - Webhook Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
  * [n8n Docs - HTTP Request Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)

### D. Seguridad y Webhook de Pagos (Sandbox e Idempotencia)
* **Qué es:** Mecanismo para confirmar transacciones financieras sin confiar en el navegador del usuario.
* **Conceptos esenciales:**
  1. **Firma HMAC SHA-256:**
     ```python
     expected_sig = hmac.new(SECRET_KEY.encode(), raw_body, hashlib.sha256).hexdigest()
     if not hmac.compare_digest(expected_sig, received_sig):
         raise HTTPException(status_code=401, detail="Firma inválida")
     ```
  2. **Idempotencia:** Si la pasarela reintenta el webhook por retrasos de red (duplicado), el sistema busca el `payment_id` en la tabla de pagos o auditoría. Si ya fue procesado, responde HTTP 200 inmediatamente sin volver a cobrar ni duplicar la reserva.
* **Recursos para consultar:**
  * [Python `hmac` Library Docs](https://docs.python.org/3/library/hmac.html)
  * [Stripe / MercadoPago Webhook Security Principles](https://docs.stripe.com/webhooks/signatures)

---

## 3. Plantilla de Criterio para Instruir al Agente en Modo AGY

Cuando vayas a pedirle al agente que escriba código (modo AGY), utiliza esta estructura basada en criterios técnicos claros para evitar que invente o genere código innecesario:

```markdown
### INSTRUCCIÓN DE LOTE [ID]
1. OBJETIVO: Implementar [Nombre de la tarea/endpoint].
2. ENTRADA (DTO): Definir schema Pydantic con validación de [campos exactos y tipos].
3. REGLA DE NEGOCIO: Aplicar la regla [RN-xx] garantizando que [descripción de la restricción, ej. verificar solapamiento o expiración de 15 min].
4. SALIDA: Retornar código HTTP [200/201/409] con estructura [JSON esperado].
5. RESTRICCIÓN ARQUITECTURAL: No usar Redis ni librerías externas no aprobadas. Usar sesión async de SQLAlchemy con PostgreSQL 16.
6. VERIFICACIÓN: Escribir el test en pytest que demuestre el caso exitoso y el caso de fallo/colisión.
```

---

## 4. Preguntas de Defensa Típicas para tu Perfil Telemático (y Cómo Responderlas)

En la sustentación, los profesores de telemática y software te harán preguntas específicas sobre arquitectura de comunicaciones y concurrencia. Aquí tienes las 3 preguntas clave preparadas:

### Pregunta 1: *"¿Por qué eliminaron Redis para los bloqueos temporales si como telemático sabes que la RAM es órdenes de magnitud más rápida que el disco de una base de datos relacional?"*
> **Tu respuesta:**  
> *"Es cierto que Redis en memoria ofrece latencias de microsegundos, pero en un hotel de 9 habitaciones (~40 reservas al mes) el cuello de botella jamás es el rendimiento, sino la **consistencia estricta (ACID)**. Con Redis teníamos una arquitectura de dos fuentes de verdad: el bloqueo en Redis y la reserva en PostgreSQL. Si ocurría un fallo de red o caída entre ambos servicios, se generaba inconsistencia (split-brain). PostgreSQL 16 con la extensión `btree_gist` resuelve el candado atómicamente a nivel de motor relacional en menos de 5 milisegundos mediante la restricción `EXCLUDE USING gist`, eliminando un servicio completo, reduciendo la superficie de ataque y garantizando consistencia transaccional absoluta sin sobrecosto de infraestructura."*

### Pregunta 2: *"¿Cómo manejan el problema de la doble reserva concurrente cuando dos usuarios en WhatsApp presionan 'Pagar' exactamente en el mismo milisegundo?"*
> **Tu respuesta:**  
> *"No lo resolvemos a nivel de aplicación con locks en Python, porque en un entorno distribuido o con múltiples workers de Uvicorn habría condiciones de carrera (race conditions). Lo delegamos al kernel de PostgreSQL 16 mediante un índice GiST sobre `room_id` y `daterange(check_in, check_out, '[)')`. PostgreSQL adquiere un candado a nivel de índice de rango durante la transacción; la primera petición se inserta con éxito y la segunda genera inmediatamente un error `ExclusionViolation` en la base de datos, que nuestra API captura limpiamente y traduce en un código HTTP `409 Conflict` avisando al usuario que la habitación acaba de ser tomada."*

### Pregunta 3: *"¿Por qué la arquitectura desacopla Meta de FastAPI poniendo n8n en el medio en lugar de recibir los webhooks directamente en FastAPI?"*
> **Tu respuesta:**  
> *"Por separación de responsabilidades y desacoplamiento de capas (patrón Hexagonal / Adaptador). Meta Cloud API actualiza frecuentemente la estructura de sus payloads de WhatsApp y maneja mecánicas de reintentos y plantillas. n8n actúa como adaptador de transporte en el borde (Edge Adapter): recibe la petición HTTP de Meta, valida el handshake de verificación (`hub.challenge`), normaliza el mensaje a un JSON plano de negocio y lo entrega a FastAPI mediante una llamada HTTP autenticada con clave de servicio (`X-Service-Key`). De esta forma, si el proveedor de mensajería cambia mañana (por ejemplo, a Telegram o Twilio), nuestro backend transaccional de FastAPI no sufre ninguna modificación."*

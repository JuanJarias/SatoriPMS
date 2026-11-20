# Suite de Pruebas y Herramientas del Chatbot — Torre Satori

Este directorio contiene las herramientas de construcción, verificación de integridad arquitectónica y la suite automatizada de pruebas para el asistente conversacional en WhatsApp (flujo V9) y los servicios transaccionales del servidor central (API) del Hotel Torre Satori.

El propósito principal de este conjunto de pruebas es validar de manera determinista y reproducible las transiciones de estado conversacionales, la interpretación de lenguaje natural con Inteligencia Artificial, el cálculo financiero estricto de tarifas y reembolsos, y las garantías de calidad y concurrencia bajo el marco ITIL 4 (Actividad 5).

---

## Estructura del Directorio

```text
tests/chatbot/
├── suite_pruebas_chatbot_v8.js      # Suite integral de 65 casos (incluye bloque V9 TC-56 a TC-65)
├── verify_n8n_flow_integrity.py     # Validador de topologia: 0 enlaces rotos, 0 huerfanos, 0 switch errors
├── test_pago_wompi_v9.js            # Suite de pruebas de cobro Wompi (11 en memoria, 5 en vivo)
├── test_e2e_v9_completo.js          # Prueba E2E en vivo de 9 pasos (fechas en 1 mensaje, mascota y aislamiento Redis)
├── test_e2e_reserva_wompi_v9.js     # E2E de reserva con Wompi: pendiente de pago -> link -> evento firmado -> confirmada
├── test_reserva_guiada_abono_50.js  # Reserva guiada con 50%: queda pendiente de pago (pending_payment)
├── test_asistente_ia_autonomo.js    # Agente autonomo con extraccion JSON: queda pendiente de pago
├── test_cancelacion_reembolso.js    # Cancelacion y regla RN-03
├── test_pago_saldo_restante.js      # Liquidacion de saldo pendiente
├── test_escalamiento_agente_humano.js # Escalamiento: verifica agent_active=true en la sesion de Redis
└── lib/
    └── env.js                       # Carga las variables del proceso y, si faltan, las del .env de la raiz
```

---

## Tecnologías y Estándares

| Tecnología / Herramienta | Rol en Pruebas | Versión / Estándar |
| :--- | :--- | :--- |
| Node.js | Entorno de ejecución de la suite automatizada y scripts de prueba | >= 18.x LTS |
| Python | Análisis topológico del flujo n8n (`verify_n8n_flow_integrity.py`) | >= 3.10 |
| n8n Workflow Schema | Especificación del motor de orquestación de nodos y conmutadores | n8n 2.47.3 (TypeVersion 2/3.4/4.2) |
| JSON Schema / REST API | Contratos de comunicación HTTP entre el chatbot y el servidor central | RFC 8259 |
| ITIL 4 Practices | Marco de validación de gestión de cambios, calidad y disponibilidad | Service Design & Transition |

---

## Arquitectura de Pruebas e Interfaz AI Runner

La suite implementa un diseño desacoplado que opera en dos modalidades complementarias:

1. **Modalidad In-Memory / Motor de Contratos:** Evalúa instantáneamente las funciones de normalización, transiciones de estados de n8n, parsers de expresiones regulares, reglas de validación de documentos colombianos (Ley 1581 de 2012) y cálculos aritméticos hoteleros sin requerir infraestructura externa levantada.
2. **Modalidad de Integración en Vivo:** Capaz de conectarse contra el servidor central (`http://localhost:8080`) y la instancia local de n8n (`http://localhost:5678`) para pruebas de extremo a extremo.

```mermaid
flowchart TD
    subgraph Canales ["1. Canales de Invocacion"]
        CLI["Consola CLI"]
        AI["Agente IA (AI Runner)"]
        CI["Tuberias CI/CD"]
    end

    subgraph Orquestador ["2. Motor de Pruebas (suite_pruebas_chatbot_v8.js)"]
        Parser["Analizador de Argumentos\n(--flow, --test, --json)"]
        Engine["Motor de Reglas y\nSimulacion In-Memory"]
        Runner["Ejecutor de Pruebas\n(runTestCase / runTestSuite)"]
        Parser --> Engine --> Runner
    end

    subgraph Modulos ["3. Modulos Evaluados (65 Casos de Prueba)"]
        direction TB
        subgraph Col1 ["Flujos Conversacionales"]
            F1["Flujo 1: Reserva Guiada (10)"]
            F2["Flujo 2: Reserva con IA (10)"]
            F3["Flujo 3: Reseñas y Google Reviews (10)"]
            F1 --> F2 --> F3
        end
        subgraph Col2 ["Gestion Operativa y Calidad"]
            F4["Flujo 4: Consulta, Saldo y Cancelacion (10)"]
            F5["Flujo 5: Escalamiento a Secretaria (10)"]
            FITIL["Bloque ITIL 4: Concurrencia y Carga (5)"]
            F4 --> F5 --> FITIL
        end
    end

    subgraph Salida ["4. Salida y Diagnostico"]
        ReportGen["Generador de Informes\n(Consola Formal / JSON Estructurado)"]
    end

    CLI --> Parser
    AI --> Parser
    CI --> Parser
    Runner --> F1
    Runner --> F4
    F3 --> ReportGen
    FITIL --> ReportGen
```

> **Alcance real de la suite integral:** de los 65 casos, 11 (TC-42 y TC-56 a TC-65) ejecutan el código real de los nodos del flujo V9. Los otros 54 evalúan las reglas de negocio con un motor en memoria que replica esas reglas dentro de la propia suite (reembolsos, tarifas, validaciones, formatos); sirven como especificación ejecutable, pero no detectan cambios en el flujo. El comportamiento del flujo en vivo lo cubren los scripts `test_*.js` de integración.

---

## Catálogo Detallado de Pruebas (65 Casos)

### Flujo 1: Reserva Guiada Paso a Paso (TC-01 a TC-10)
Valida la interacción guiada estructurada para usuarios que prefieren navegación menú a menú.

- **TC-01:** Validación de fechas futuras válidas (cálculo correcto de noches de estadía).
- **TC-02:** Rechazo de fechas pasadas en check-in (anterior a la fecha actual del sistema).
- **TC-03:** Rechazo de fecha check-out anterior o igual al check-in.
- **TC-04:** Selección válida de habitación por índice de listado o número de habitación.
- **TC-05:** Rechazo de selección de habitación fuera de rango o entrada de texto arbitraria.
- **TC-06:** Validación de cantidad de adultos (debe ser un entero mayor o igual a 1).
- **TC-07:** Validación estricta de identificación del titular (6 a 10 dígitos numéricos).
- **TC-08:** Validación de restricción de mascotas por habitación (`allows_pets = false`).
- **TC-09:** Desglose financiero: cálculo exacto del 50% de anticipo vs. 100% de pago total.
- **TC-10:** Cancelación manual en paso de pago y liberación limpia del bloqueo temporal.

### Flujo 2: Reserva con Asistente IA Autónomo (TC-11 a TC-20)
Valida el asistente impulsado por modelos generativos que extrae datos de mensajes libres.

- **TC-11:** Extracción completa de mensaje único con todos los parámetros (fechas, ocupación, titular, documento, mascota y acompañantes).
- **TC-12:** Detección y solicitud explícita ante información incompleta (ausencia de fechas o titular).
- **TC-13:** Detección y rechazo de rangos cronológicos incoherentes o invertidos interpretados por la IA.
- **TC-14:** Bucle de confirmación de datos: respuesta afirmativa ("Sí", "Correcto", "De acuerdo") avanza a disponibilidad.
- **TC-15:** Bucle de corrección de datos: ajuste incremental de parámetros en el borrador ante aclaraciones del huésped.
- **TC-16:** Selección de habitación única en el asistente IA.
- **TC-17:** Selección de habitaciones múltiples (ej. "1, 2" o "1 y 2") con bloqueo temporal conjunto.
- **TC-18:** Cálculo de recargo por huéspedes adicionales en reserva múltiple si se supera la capacidad base conjunta.
- **TC-19:** Aviso obligatorio y consentimiento expreso de política de tratamiento de datos personales (Ley 1581 de 2012).
- **TC-20:** Cancelación del flujo IA y liberación automática de candados en memoria.

### Flujo 3: Redirección Oficial a Google Reviews (TC-21 a TC-30)
Valida la redirección transparente e imparcial hacia el perfil oficial de Google Reviews sin almacenamiento privado local.

- **TC-21:** Emisión de mensaje formal con enlace a Google Reviews al elegir la opción 3 del menú.
- **TC-22:** Validación de URL canónica limpia permanente sin tokens efímeros de sesión (`g2lb`, `ssta`, `ts`).
- **TC-23:** Resolución dinámica y configurable del enlace mediante la variable `GOOGLE_REVIEWS_URL`.
- **TC-24:** Reseteo inmediato de la sesión a estado `menu` y paso `esperando_opcion` para navegación continua.
- **TC-25:** Reconocimiento flexible de palabras clave (`"reseña"`, `"opiniones"`, `"calificar"`, `"google"`).
- **TC-26:** Activación de vista previa de enlace (`preview_url: true`) en el payload de mensajería para WhatsApp.
- **TC-27:** Desacoplamiento total de tablas locales de reseña para certificar imparcialidad y reputación abierta.
- **TC-28:** Detección de comandos de retorno al menú principal ("menú", "hola").
- **TC-29:** Compatibilidad hacia atrás para entradas numéricas legacy 5 (Consultar) y 6 (Agente).
- **TC-30:** Validación de tono formal sin pictogramas informales ni emojis en la comunicación.

### Flujo 4: Consulta, Pago de Saldo y Cancelación (TC-31 a TC-40)
Valida la gestión de reservas confirmadas bajo la nomenclatura oficial `TS-XXXX`.

- **TC-31:** Consulta exitosa con prefijo estandarizado `TS-XXXX` (Torre Satori).
- **TC-32:** Consulta insensible a mayúsculas/minúsculas o sin guion (`ts-1234`, `TS1234`).
- **TC-33:** Rechazo de código de reserva menor a 4 caracteres o inexistente en base de datos.
- **TC-34:** Consulta de reserva con saldo pendiente (habilitación de opciones 1 Pagar saldo y 2 Cancelar).
- **TC-35:** Consulta de reserva 100% pagada (presentación exclusiva de cancelación y retorno).
- **TC-36:** Liquidación de saldo pendiente al 100% (actualización a estado `paid` y saldo restante a $0.00).
- **TC-37:** Política de reembolso con más de 72h antes del check-in (reembolso del 100% de lo abonado).
- **TC-38:** Política de reembolso entre 24h y 72h antes del check-in (reembolso del 50% de lo abonado).
- **TC-39:** Política de reembolso con menos de 24h antes del check-in (0% de reembolso / penalidad total).
- **TC-40:** Doble confirmación de cancelación: respuesta "No" preserva la reserva intacta.

### Flujo 5: Escalamiento a Secretaria / Atención Humana (TC-41 a TC-50)
Valida la transferencia fluida de conversaciones complejas a recepción humana.

- **TC-41:** Activación de atención humana por palabras clave en cualquier momento ("agente", "recepcionista", "humano", "secretaria").
- **TC-42:** Activación mediante la opción de agente del Menú Principal (la 5 en V9; la 6 heredada de V8 sigue enrutando igual). Ejecuta el código real del nodo evaluador.
- **TC-43:** Bloqueo de respuestas automáticas del bot mientras la bandera `agent_active` sea `true`.
- **TC-44:** Comandos de escape ("menú", "hola", "inicio") desactivan el modo agente y devuelven el control al bot.
- **TC-45:** Generación de evento de notificación para el panel web de recepción.
- **TC-46:** Formato sobrio del mensaje de espera al huésped sin emojis.
- **TC-47:** Persistencia del estado `agent_active` en la sesión de Redis.
- **TC-48:** Manejo silencioso de mensajes consecutivos del huésped durante la espera sin respuestas duplicadas.
- **TC-49:** Expiración de inactividad de sesión establecida en 10 minutos (600 segundos).
- **TC-50:** Cierre limpio y normalización de la sesión tras finalizar la atención humana.

### Bloque ITIL 4: Garantías de Calidad y Concurrencia (TC-51 a TC-55)
Valida la resiliencia transaccional y la prevención absoluta de sobreventa (sobreventa = 0).

- **TC-51:** Doble Candado en Redis: Concurrencia en milisegundo 0 con `Promise.all` (`SET NX EX 900`). Garantiza que ante solicitudes simultáneas solo un cliente obtenga el bloqueo.
- **TC-52:** Doble Candado en PostgreSQL: Verificación en capa de persistencia final mediante aislamiento transaccional (`countConflictingBookings = 0`).
- **TC-53:** Prueba de rendimiento y estrés: Ráfaga de 50 consultas concurrentes de disponibilidad resueltas en menos de 500ms.
- **TC-54:** Tarifas dinámicas con eventos especiales: Aplicación de descuentos y recargos porcentuales estacionales.
- **TC-55:** Cálculo estricto de reembolso sobre el monto efectivamente pagado (`paid_amount`). Caso crítico: ante una reserva de $500.000 con $250.000 abonados cancelada a tiempo, se reembolsan exactamente $250.000 (el 100% de lo pagado), nunca los $500.000 del valor total de la estadía.

### Novedades del Flujo V9 (TC-56 a TC-65)
Valida el código real de los nodos del flujo V9: integración con Wompi, fechas en un solo mensaje, reasignación de habitaciones con mascota, validación de acompañantes y el contrato de seguridad con el servidor central.

- **TC-64:** Todas las llamadas del flujo a la API central envían la llave de servicio `X-Service-Key` tomada de `SATORI_SERVICE_KEY`.
- **TC-65:** El documento del titular viaja a la API al consultar (encabezado `X-Guest-Document`), pagar el saldo, cancelar y revertir una reserva por fallo de Wompi; la verificación ya no se hace dentro de n8n.

---

## Guía de Ejecución

### Ejecución Completa por Consola
Ejecuta los 65 casos de prueba con salida formateada para terminal:

```bash
node tests/chatbot/suite_pruebas_chatbot_v8.js
```

### Ejecución Filtrada por Flujo o Caso Unitario

Para ejecutar exclusivamente un flujo funcional específico:
```bash
# Ejecutar solo Flujo 2 (Reserva con IA):
node tests/chatbot/suite_pruebas_chatbot_v8.js --flow 2

# Ejecutar solo Bloque ITIL 4:
node tests/chatbot/suite_pruebas_chatbot_v8.js --flow itil
```

Para ejecutar un caso de prueba individual:
```bash
node tests/chatbot/suite_pruebas_chatbot_v8.js --test TC-55
```

Para generar salida estructurada en formato JSON (ideal para tuberías CI/CD o subagentes):
```bash
node tests/chatbot/suite_pruebas_chatbot_v8.js --flow 4 --json
```

### Integración Programática para Agentes de IA

Cualquier script o agente autónomo puede importar la suite y evaluar resultados en memoria:

```javascript
const { runTestSuite, runTestCase } = require('./tests/chatbot/suite_pruebas_chatbot_v8.js');

async function evaluarCalidad() {
  // Ejecutar el flujo de cancelacion y reembolso
  const reporte = await runTestSuite({ flow: '4', json: true });

  if (reporte.success) {
    console.log(`Verificacion completada: ${reporte.passed}/${reporte.total} pruebas aprobadas.`);
  } else {
    console.error(`Fallos detectados: ${reporte.failed} pruebas con error.`);
  }
}

evaluarCalidad();
```

### Verificación de Integridad de Flujo n8n

Para asegurar que el flujo [V9_ChatbotReservas.json](../../flows/n8n/V9_ChatbotReservas.json) mantenga 100% de coherencia topológica:

```bash
# Validar conexiones, nodos huérfanos y reglas de conmutación:
python3 tests/chatbot/verify_n8n_flow_integrity.py
```

---

## Políticas y Reglas del Negocio Validadas

1. **Prefijo Oficial de Reserva:** Toda reserva generada y consultada responde a la convención `TS-XXXX` (Torre Satori), eliminando cualquier nomenclatura provisional previa.
2. **Cálculo de Reembolso sobre lo Abonado:** Las políticas de cancelación (RN-03) operan exclusivamente sobre el dinero que el huésped ingresó efectivamente a la cuenta del hotel (`paid_amount`). Jamás se emiten reembolsos calculados sobre saldos pendientes por cobrar.
3. **Mecanismo de Doble Candado:**
   - **Candado Rápido (Redis):** Bloqueo en memoria por 15 minutos (900 segundos) para impedir que dos personas seleccionen la misma habitación en WhatsApp.
   - **Candado Firme (PostgreSQL):** Bloqueo transaccional a nivel de base de datos que garantiza 0 sobreventas incluso ante interrupciones de red o fallos de concurrencia.
4. **Protección de Datos Personales:** Cumplimiento riguroso del aviso de privacidad según la Ley 1581 de 2012 en el primer contacto con el asistente de Inteligencia Artificial.
5. **Caducidad de Sesiones:** El tiempo de espera máximo por inactividad del huésped está calibrado en 10 minutos (600 segundos), tras lo cual se liberan las habitaciones reservadas temporalmente para permitir nuevas reservas.

---

## Chatbot V9 — Cobro de la reserva con Wompi y Flujo Principal

El flujo principal y único en operación es [V9_ChatbotReservas.json](../../flows/n8n/V9_ChatbotReservas.json). Cuenta con el cobro de la reserva conectado a la pasarela Wompi y redirección oficial a Google Reviews. Al finalizar la reserva genera un link de pago por el 50% o el 100% del total, según la modalidad elegida.

| Archivo | Propósito |
| :--- | :--- |
| `test_pago_wompi_v9.js` | 11 pruebas en memoria (W-01 a W-11) que ejecutan el código real de los nodos del V9. Con `--live` se suman 5 pruebas reales contra la API de Wompi (L-01 a L-05). |
| `test_e2e_reserva_wompi_v9.js` | E2E con el stack levantado: conversación completa → reserva pendiente de pago → link en Wompi (por el 50%) → evento firmado → reserva confirmada con el 50% abonado. Crea y desactiva un link real. |
| `verify_n8n_flow_integrity.py` | Validador topológico del flujo n8n V9. |

```bash
node tests/chatbot/test_pago_wompi_v9.js [--live]
python3 tests/chatbot/verify_n8n_flow_integrity.py flows/n8n/V9_ChatbotReservas.json
node tests/chatbot/test_e2e_reserva_wompi_v9.js
```

**Pruebas en vivo contra la API:** el servidor central exige autenticación. Los scripts `test_*.js` de integración toman `SATORI_SERVICE_KEY` de la variable de entorno o, si no existe, del archivo `.env` de la raíz (`lib/env.js`), y llegan a la API en `localhost:8080` y a n8n en `localhost:5678` (se pueden cambiar con `API_HOST`, `API_PORT`, `N8N_HOST` y `N8N_PORT`). Requieren el entorno levantado (`./scripts/start-dev.sh`) y acceso a Docker para leer Redis:

```bash
node tests/chatbot/test_cancelacion_reembolso.js
```

**Resultado esperado en V9:** como el cobro es con Wompi, una reserva recién creada por el chatbot queda en `pending_payment` / `pending` con `paid_amount = 0`; pasa a `confirmed` / `partial` (o `paid`) solo cuando llega el evento firmado de Wompi.

---

## Integración Continua

El flujo de GitHub Actions (`.github/workflows/ci.yml`) ejecuta sin necesidad de servicios externos: `verify_n8n_flow_integrity.py`, `suite_pruebas_chatbot_v8.js` y `test_pago_wompi_v9.js`. Las pruebas `test_*.js` en vivo no se ejecutan en CI porque necesitan n8n, Redis y la API.

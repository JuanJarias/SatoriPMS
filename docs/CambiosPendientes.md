# Cambios Pendientes desde el Último Push

- **Rama actual:** `chore/comprehensive-review-and-fixes`
- **Rama remota de referencia (`@{u}`):** `origin/main` (commit `633def8`, tras fusión del Pull Request `#109`)
- **Commits locales acumulados (`git log origin/main..HEAD`):** `5`
- **Nota de reinicio:** El historial previo hasta el commit `633def8` (`#109`) ya se encuentra en el repositorio remoto y registrado en [`docs/modulos/EstadoActual.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/EstadoActual.md), por lo que este archivo organiza los cinco commits de la revisión integral.

---

## Commit 1: Configuración Maestra del Proyecto e Ignorados de Git

- **Mensaje del commit:** `chore(config): add master project guidelines and ignore local directory metadata`
- **Estado:** Commiteado, sin push
- **Archivos afectados:**
  - `GEMINI.md` (nuevo)
  - `.gitignore` (modificado)
  - `docs/cambios_commit.md` (eliminado, reemplazado por `docs/CambiosPendientes.md`)
- **Descripción de los cambios y motivo:**
  - Se incorpora el archivo `GEMINI.md` con las directrices maestras de análisis incremental, estructura obligatoria de `EstadoActual.md`, funcionamiento de `CambiosPendientes.md` y reglas de redacción para el cliente.
  - Se añade `.directory` a `.gitignore` para evitar que los metadatos visuales del gestor de archivos local contaminen el árbol de trabajo.
  - Se retira el archivo antiguo `docs/cambios_commit.md` tras su sustitución por `docs/CambiosPendientes.md`.

---

## Commit 2: Correcciones en Backend, Semillas SQL, Flujo Chatbot V8, Pruebas e Integración Continua

- **Mensaje del commit:** `fix(core): align refund over paid amount, add immediate Redis unlock, fix V8 flow options and update CI to Java 21`
- **Estado:** Commiteado, sin push
- **Archivos afectados:**
  - `apps/api/src/main/java/com/satoripms/api/booking/BookingBatchRequestDto.java` (modificado)
  - `apps/api/src/main/java/com/satoripms/api/booking/BookingService.java` (modificado)
  - `apps/api/src/main/java/com/satoripms/api/booking/BookingController.java` (modificado)
  - `apps/web/src/pages/ReservasDebug.tsx` (modificado)
  - `db/seed/dev_seed.sql` (modificado)
  - `apps/api/src/main/resources/db/migration/V2__seed_rooms.sql.example` (modificado)
  - `apps/api/src/main/resources/db/migration/V3__seed_products.sql.example` (eliminado)
  - `apps/api/src/main/resources/db/migration/V6__seed_products.sql.example` (nuevo)
  - ` tests/chatbot/build_v8_chatbot_flow.py` (modificado)
  - `flows/n8n/V8_ChatbotReservas.json` (modificado)
  - `tests/chatbot/test_cancelacion_reembolso.js` (modificado)
  - `tests/chatbot/test_pago_saldo_restante.js` (modificado)
  - `tests/chatbot/test_escalamiento_agente_humano.js` (modificado)
  - `.github/workflows/ci.yml` (modificado)
- **Descripción de los cambios y motivo:**
  - **Reembolso sobre monto pagado y canal de origen en Backend:** En `BookingService.getReservationDetailsByCode` se corrige el cálculo de `estimatedRefund` para que aplique los porcentajes (`100%`, `50%`, `0%`) sobre `totalPaidAmount` (`paid_amount`) en lugar de `totalGroupPrice`. Además, se añade el campo opcional `source` en `BookingBatchRequestDto` y `ReservasDebug.tsx` para registrar `"web"` cuando la reserva proviene de la aplicación web y `"chatbot"` por defecto.
  - **Liberación inmediata de bloqueos temporales en Redis:** Se añade el método `releaseTemporaryLocks` en `BookingService` y el endpoint `POST /api/bookings/unlock` en `BookingController` para liberar al instante los intervalos bloqueados en Redis sin esperar los 15 minutos del TTL.
  - **Semillas SQL y plantillas Flyway:** Se corrige `INSERT INTO system_user` por `INSERT INTO system_users` en `db/seed/dev_seed.sql`, se actualiza `V2__seed_rooms.sql.example` con las 9 habitaciones de referencia del hotel y se renombra `V3__seed_products.sql.example` a `V6__seed_products.sql.example` para evitar colisión de versión con `V3__align_id_types_with_jpa.sql`.
  - **Flujo Chatbot V8 (`V8_ChatbotReservas.json` — 83 nodos) y pruebas:** Se corrige la inversión entre las opciones `5` (`Revisar o Cancelar`) y `6` (`Hablar con agente`), se añade el aviso de privacidad (Ley 1581 de 2012) antes de capturar datos personales en los flujos guiado e IA, se incluye el desglose explícito de tarifa base + recargo por persona adicional tanto en `H Procesar Reserva Paso` como en `H Resumen y Pago IA`, y se conecta el llamado a `POST /api/bookings/unlock` al cancelar el pago, reiniciar con `menu` o limpiar sesiones inactivas. Se actualizan los tres scripts de prueba afectados.
  - **Integración Continua (`.github/workflows/ci.yml`):** Se reemplaza la configuración de Node.js/NestJS para `apps/api` por un job de Java 21 (`temurin`) con caché de Maven que ejecuta `mvn -B test` y `mvn -B package -DskipTests`.

---

## Commit 3: Documentación Funcional de Presentación y Especificaciones de Módulos

- **Mensaje del commit:** `docs(modules): rewrite root and module specifications in client-friendly format`
- **Estado:** Commiteado, sin push
- **Archivos afectados:**
  - `README.md` (modificado)
  - `docs/README.md` (modificado)
  - `docs/modulos/GeneralidadesNucleo.md` (modificado)
  - `docs/modulos/Chatbot.md` (modificado)
  - `docs/modulos/AplicacionWeb.md` (modificado)
  - `docs/modulos/BackendAPI.md` (modificado)
  - `docs/modulos/Database.md` (modificado)
  - `docs/modulos/Seguridad.md` (modificado)
  - `docs/modulos/Infraestructura.md` (modificado)
  - `docs/modulos/TiendaInventario.md` (modificado)
  - `docs/modulos/FacturacionFinanzas.md` (modificado)
  - `docs/modulos/ResenasFidelizacion.md` (modificado)
  - `docs/modulos/GestionProyecto.md` (modificado)
  - `docs/modulos/DiseñoUXUI.md` (modificado)
- **Descripción de los cambios y motivo:**
  - Se reescriben `README.md` y `docs/README.md` como cartas de presentación claras y concisas para la raíz del proyecto y la carpeta `docs/`.
  - Se reescriben los 12 documentos de especificación en `docs/modulos/` conforme a la sección 12.C de `GEMINI.md`: sin fragmentos de código, sin nombres de funciones, sin códigos internos (`HU-*`, `CU-*`, `RN-*`) y sin emojis, documentando cómo debe funcionar el sistema completo (incluyendo las 9 habitaciones de referencia, la creación/edición/eliminación controlada de habitaciones por el Administrador, la programación de eventos especiales y descuentos, la liberación inmediata de bloqueos y el reembolso sobre el monto realmente pagado).

---

## Commit 4: Reestructuración de Diagramas y Alineación del Modelo Presupuestal

- **Mensaje del commit:** `docs(diagrams,budget): restructure Mermaid diagrams and align budget docs and xlsx with client rules`
- **Estado:** Commiteado, sin push
- **Archivos afectados:**
  - `docs/Diagramas/README.md` (modificado)
  - `docs/Diagramas/01_Infraestructura_Servicios.md` (modificado)
  - `docs/Diagramas/02_Flujo_Reserva_WhatsApp.md` (modificado)
  - `docs/Diagramas/03_Concurrencia_Doble_Candado.md` (modificado)
  - `docs/Diagramas/04_Gestion_Operativa_Recepcion.md` (modificado)
  - `docs/Diagramas/05_Ciclo_Vida_Reserva.md` (modificado)
  - `docs/Presupuesto/Presupuesto_SatoriPMS.xlsx` (modificado)
  - `docs/Presupuesto/Presupuesto.md` (modificado)
  - `docs/Presupuesto/Actividad4_Crisis_Presupuestal.md` (modificado)
- **Descripción de los cambios y motivo:**
  - Se rediseñan los 5 diagramas Mermaid y su índice en `docs/Diagramas/` para que reflejen con exactitud la arquitectura real, los estados en minúscula, el desbloqueo inmediato en Redis, el reembolso sobre lo pagado y la gestión de las 9 habitaciones y eventos especiales, redactados en lenguaje apto para el cliente.
  - Se actualiza `docs/Presupuesto/Presupuesto_SatoriPMS.xlsx` reemplazando los códigos internos (`HU-*`, `HUT-*`, `CU-*`, `RN-*`, `DoD`, `Guion 3`) por identificadores limpios (`REQ-01` a `REQ-32`) y descripciones en español claro que incluyen la administración de las 9 habitaciones y los eventos especiales, conservando intactas sus 684 fórmulas.
  - Se reescriben `Presupuesto.md` y `Actividad4_Crisis_Presupuestal.md` priorizando las cifras oficiales de `Presupuesto_SatoriPMS.xlsx` (`$24.685.000 COP` CAPEX, `$289.842 COP/mes` OPEX, `$28.163.100 COP` TCO Año 1, 9 habitaciones, 150 puntos) y aplicando la regla de redacción para el cliente.

---

## Commit 5: Actualización de los Documentos de Seguimiento del Proyecto

- **Mensaje del commit:** `docs(tracking): update EstadoActual.md and CambiosPendientes.md after comprehensive review`
- **Estado:** Commiteado, sin push
- **Archivos afectados:**
  - `docs/modulos/EstadoActual.md` (modificado)
  - `docs/CambiosPendientes.md` (nuevo)
- **Descripción de los cambios y motivo:**
  - Se redacta `docs/modulos/EstadoActual.md` con las 6 secciones obligatorias de la sección 12.B de `GEMINI.md`, incluyendo el cuadro resumen con vocabulario estricto de la sección 8, los 16 puntos de estado general, el reconocimiento explícito de los elementos pendientes en la aplicación web y en el flujo V8, el registro de cambios y el registro de decisiones.
  - Se crea `docs/CambiosPendientes.md` con la segmentación propuesta de los cambios acumulados desde el último push.

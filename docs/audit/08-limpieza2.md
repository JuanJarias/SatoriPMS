# Propuesta de Segunda Limpieza y Saneamiento (Fase 3)

**Fecha:** 2026-11-10  
**Rama:** `migracion-fastapi`  
**Estado:** Propuesta para revisión (DETENIDO antes de ejecución).

---

## 1. Tabla de Elementos Evaluados para la Segunda Limpieza

| Ruta | Por qué sobra o requiere acción | Evidencia | Acción Propuesta |
| :--- | :--- | :--- | :---: |
| `docs/modulos/Manual_Recepcion.html` | **Documento duplicado:** Es 100% idéntico byte por byte a `docs/Presentaciones/Manual_Recepcion.html`. | `diff -u` entre ambas rutas no muestra diferencias. Sobra en `docs/modulos/`. | **ELIMINAR** |
| `flows/n8n/pastVersions/V1_ChatbotReservas.json` | **Obsoleto / Stack prohibido:** Versión histórica antigua del chatbot con múltiples nodos Redis. | `V1_ChatbotReservas.json:109` contiene nodos `n8n-nodes-base.redis`. V8 es la versión activa. | **MOVER** a `docs/legacy-ref/n8n-past-versions/` |
| `flows/n8n/pastVersions/V2_ChatbotReservas.json` | **Obsoleto / Stack prohibido:** Versión histórica antigua del chatbot con múltiples nodos Redis. | `V2_ChatbotReservas.json` contiene nodos `n8n-nodes-base.redis`. | **MOVER** a `docs/legacy-ref/n8n-past-versions/` |
| `flows/n8n/pastVersions/V3_ChatbotReservas.json` | **Obsoleto / Stack prohibido:** Versión histórica antigua del chatbot con múltiples nodos Redis. | `V3_ChatbotReservas.json` contiene nodos `n8n-nodes-base.redis`. | **MOVER** a `docs/legacy-ref/n8n-past-versions/` |
| `flows/n8n/pastVersions/V4_ChatbotReservas.json` | **Obsoleto / Stack prohibido:** Versión histórica antigua del chatbot con múltiples nodos Redis. | `V4_ChatbotReservas.json` contiene nodos `n8n-nodes-base.redis`. | **MOVER** a `docs/legacy-ref/n8n-past-versions/` |
| `flows/n8n/pastVersions/V5_ChatbotReservas.json` | **Obsoleto / Stack prohibido:** Versión histórica antigua del chatbot con múltiples nodos Redis. | `V5_ChatbotReservas.json` contiene nodos `n8n-nodes-base.redis`. | **MOVER** a `docs/legacy-ref/n8n-past-versions/` |
| `flows/n8n/pastVersions/V6_ChatbotReservas.json` | **Obsoleto / Stack prohibido:** Versión histórica antigua del chatbot con múltiples nodos Redis. | `V6_ChatbotReservas.json` contiene nodos `n8n-nodes-base.redis`. | **MOVER** a `docs/legacy-ref/n8n-past-versions/` |
| `flows/n8n/pastVersions/V7_ChatbotReservas.json` | **Obsoleto / Stack prohibido:** Versión histórica antigua del chatbot con múltiples nodos Redis. | `V7_ChatbotReservas.json:560` contiene 5 nodos activos de Redis. | **MOVER** a `docs/legacy-ref/n8n-past-versions/` |
| `docs/Diagramas/01_Infraestructura_Servicios.md` | **Documento obsoleto:** Diagrama de infraestructura que describe arquitectura Java 21, Spring Boot 3.3, Redis 7 y Flyway. | Líneas 42 ("Java 21"), 47 ("Redis 7"), 48 ("Flyway"). | **MOVER** a `docs/legacy-ref/diagramas/` |
| `docs/Diagramas/02_Flujo_Reserva_WhatsApp.md` | **Documento obsoleto:** Diagrama de secuencia con candados Redis y endpoints Spring Boot. | Diagrama Mermaid con interacción hacia Redis y Spring. | **MOVER** a `docs/legacy-ref/diagramas/` |
| `docs/Diagramas/03_Concurrencia_Doble_Candado.md` | **Documento obsoleto:** Especifica la arquitectura descartada de doble candado (Redis TTL + PostgreSQL GiST). | Diagrama Mermaid basado en validación previa en Redis. | **MOVER** a `docs/legacy-ref/diagramas/` |
| `docs/modulos/BackendAPI.md` | **Documento obsoleto:** Especificación funcional con referencias a llaves Redis (`lock:room:{roomId}:intervals`) y Spring. | Líneas 47-54 detallan llaves Redis en memoria. | **MOVER** a `docs/legacy-ref/modulos/` |
| `docs/modulos/Database.md` | **Documento obsoleto / Rutas rotas:** Referencia estados en minúsculas en inglés (`pending_payment`, `finished`) y rutas inexistentes a Flyway (`apps/api/src/main/resources/db/migration/`). | Líneas 50-54 y líneas 93-100 con rutas absolutas locales a Flyway. | **MOVER** a `docs/legacy-ref/modulos/` |
| `apps/api/src/main/resources/db/migration/` | **Directorios huérfanos vacíos:** Carpetas residuales en el disco local tras la eliminación de los archivos Java en git. | `find apps/api` muestra árboles vacíos no versionados. | **ELIMINAR** (limpieza local de carpetas vacías) |
| `.gitignore` | **Incoherencia de stack:** Contiene secciones obsoletas de Java/Gradle (`.gradle/`, `target/`, `*.jar`, `*.class`) y rutas Flyway inexistentes (`apps/api/.../V*__seed_*.sql`). | Líneas 14-21 y 46-47 de `.gitignore`. | **ADAPTAR** (remover Java/Flyway, mantener Python/Node/Vite) |
| `.env.example` | **Incoherencia de stack:** Declara variable obsoleta de WebSocket (`VITE_WS_URL=ws://localhost:8080`) proveniente de Spring STOMP descartado. | Línea 46 de `.env.example`. | **ADAPTAR** (eliminar `VITE_WS_URL`) |
| `start-dev.sh` | **Incoherencia documental:** Mensaje de inicio anuncia URL de Swagger Spring Boot (`/swagger-ui/index.html`) en lugar de FastAPI (`/docs`). | Línea 203 de `start-dev.sh`. | **ADAPTAR** (actualizar a `/docs`) |
| `tests/chatbot/test_asistente_ia_autonomo.js` | Comentario menciona "Tiempo para bloqueo temporal en Redis", pero el test es funcional para n8n. | Línea 116 de `test_asistente_ia_autonomo.js`. | **CONSERVAR** (comentario menor a limpiar en M3) |
| `tests/chatbot/test_*.js` (7 scripts) | Pruebas de integración de WhatsApp y n8n con Node.js puro y http. Útiles para verificación de M3. | 7 scripts válidos en JavaScript sin dependencias Java. | **CONSERVAR** |
| `tests/chatbot/verify_n8n_flow_integrity.py` | Script Python que valida estructura y sintaxis de los flujos n8n. | Ejecución Python 3.12 funcional. | **CONSERVAR** |
| `flows/n8n/V8_ChatbotReservas.json` | Flujo activo del chatbot (83 nodos). Las referencias a Redis se adaptarán en M3. | Archivo clasificado como ADAPTAR en M3. | **CONSERVAR** (sin tocar hasta M3) |
| `tests/chatbot/build_v8_chatbot_flow.py` | Generador del flujo n8n. Las referencias a Redis se adaptarán en M3. | Archivo clasificado como ADAPTAR en M3. | **CONSERVAR** (sin tocar hasta M3) |
| `apps/web/` (Todo el frontend TypeScript) | Código fuente React 18 + Vite + TS. Compila limpiamente sin errores de tipos. | `npm run build` exitoso (0 errores, 81 módulos transformados). | **CONSERVAR** |
| `docs/Presentaciones/Manual_Recepcion.html` | Manual original de recepción para el personal del hotel en Sevilla. | Archivo original de presentación. | **CONSERVAR** |
| `docs/Actividades/` y `docs/Presupuesto/` | Documentos y entregables académicos de la materia correspondientes a actividades previas. | Archivos PDF y Markdown de evaluación del curso. | **CONSERVAR** |

---

## 2. Resumen del Conteo Propuesto

* **ELIMINAR:** **2 ítems** (1 archivo duplicado en git `docs/modulos/Manual_Recepcion.html` + 1 árbol de directorios huérfanos vacíos en disco `apps/api/src`).
* **MOVER a `docs/legacy-ref/`:** **12 archivos** (7 flujos n8n históricos `V1..V7` a `docs/legacy-ref/n8n-past-versions/` + 3 diagramas de arquitectura Java/Redis a `docs/legacy-ref/diagramas/` + 2 módulos con especificación legacy a `docs/legacy-ref/modulos/`).
* **ADAPTAR:** **3 archivos de configuración** (`.gitignore`, `.env.example`, `start-dev.sh` eliminando residuos de Java/WebSocket/Swagger).
* **CONSERVAR:** **Frontend completo** (`apps/web`), flujo activo n8n (`V8_ChatbotReservas.json`), scripts de testing n8n (`tests/chatbot/`), archivo de presentación original y entregables académicos.

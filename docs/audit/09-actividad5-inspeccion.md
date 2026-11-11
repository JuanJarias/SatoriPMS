# Inspección y Plan de Acción: Actividad 5 (Transición del Servicio - ITIL 4)

**Fecha:** 2026-11-11  
**Rama:** `migracion-fastapi`  
**Archivos inspeccionados:**
1. `ACTIVIDAD 5. Entregable transición del servicio (Operaciones).pdf` (Guía oficial de la rúbrica del curso).
2. `Actividad5_Transicion_Servicio.md` (Documento integrador en la raíz y en `docs/Actividades/`).
3. `index.html` (Presentación ejecutiva interactiva de 36 diapositivas en la raíz, 5.526 líneas) y `docs/Presentaciones/Actividad5_Transicion_Servicio.html`.

---

## 1. Diagnóstico de la Inspección

### A. Conformidad con la Guía de la Actividad 5 (ITIL 4)
El documento integrador `Actividad5_Transicion_Servicio.md` cumple de manera sobresaliente con la estructura académica requerida por el profesor en los **8 componentes obligatorios**:
* **Componente 1:** Definición del servicio y alcance (Propósito, hotel en Sevilla, 9 habs, MVP, marcha blanca).
* **Componente 2:** Plan de despliegue e implementación (Arquitectura de 4 contenedores, secuencia, responsables, rollback).
* **Componente 3:** Gestión y autorización de cambios (Registro de cambios CHG-01 a CHG-03, evaluación de impacto).
* **Componente 4:** Validación y pruebas del servicio (Pruebas funcionales, integración, seguridad, rendimiento, recuperación, UAT).
* **Componente 5:** Preparación de la operación y soporte (SLA, canales de soporte, escalamiento L1/L2/L3, respaldos).
* **Componente 6:** Gestión del conocimiento y transferencia (Manuales, credenciales seguras en variables de entorno, capacitación).
* **Componente 7:** Comunicación y puesta en servicio (Partes interesadas, canales, cronograma de inducción).
* **Componente 8:** Aceptación y cierre de la transición (Defectos conocidos, riesgos abiertos, decisión: autorizado en marcha blanca).

---

### B. Hallazgo Crítico: Divergencia Absoluta de Stack Tecnológico
Tanto el informe (`Actividad5_Transicion_Servicio.md`) como la presentación visual interactiva (`index.html`) fueron elaborados con la **arquitectura tecnológica legada (prohibida en Sprint 5)**:

| Elemento del Entregable | Estado Actual en Actividad 5 (`index.html` y `.md`) | Estado Real Requerido (FastAPI / Sprint 5) |
| :--- | :--- | :--- |
| **Backend Central** | Java 21 + Spring Boot 3.3.5 con Maven Multi-stage | **Python 3.12 + FastAPI + Pydantic + Uvicorn** |
| **Capa de Candado Rápido** | Servidor Redis 7 Alpine con scripts Lua y TTL 15m | **PostgreSQL 16 nativo (`EXCLUDE USING gist`)** con `expires_at` (sin Redis) |
| **Control de Base de Datos** | Migraciones automáticas Flyway (scripts `V1` a `V7`) | **Alembic con SQLAlchemy 2.0 async** |
| **Arquitectura Anti-Sobreventa** | "Doble Candado Concurrente (Redis Lua + PostgreSQL GIST)" | **Candado Relacional Atómico GiST** (misma transacción expira vencidos e inserta) |
| **Variables de Entorno** | `REDIS_HOST`, `REDIS_PORT`, `SPRING_PROFILES_ACTIVE` | `DATABASE_URL`, `JWT_SECRET`, `PAYMENT_WEBHOOK_SECRET` |
| **Verificación de Salud** | Healthcheck a Redis (`redis-cli ping`) y Spring Actuator | Endpoint `/api/v1/health` en FastAPI y `pg_isready` en Postgres |
| **Procedimiento de Rollback** | Reversión de imagen Spring Boot y restauración Flyway | Rollback con `alembic downgrade -1` y reversión de imagen FastAPI |
| **Diapositivas Afectadas en `index.html`** | Diapositivas 5, 6, 10, 11, 12, 13, 14, 15, 17, 18, 21, 23 | Reemplazo de SVG interactivos, textos y métricas técnicas |

---

## 2. Plan de Acción Detallado para Replantear la Entrega

### Fase A: Actualización del Documento Integrador (`Actividad5_Transicion_Servicio.md`)
1. **Componente 1 (Alcance):** Ajustar la ficha técnica a FastAPI, PostgreSQL 16 con `btree_gist`, React 18 Vite y n8n sin Redis.
2. **Componente 2 (Despliegue):** Reemplazar los diagramas ASCII y tablas de contenedores eliminando `satori-redis`, sustituyendo Spring Boot por FastAPI y Flyway por Alembic.
3. **Componente 3 (Cambios):**
   * Replantear el cambio `CHG-02`: en lugar de "limpieza en memoria de Redis", documentar la **"Expiración atómica de bloqueos temporales e inline filtering en PostgreSQL"** (la disponibilidad ignora bloqueos vencidos en tiempo real).
4. **Componente 4 (Pruebas):** Actualizar las evidencias de pruebas de seguridad y recuperación:
   * Reemplazar scripts Lua por pruebas de concurrencia en `pytest` contra la restricción `EXCLUDE USING gist`.
   * Reemplazar logs de excepciones Spring por capturas HTTP 409 Conflict y validación de firma HMAC `X-Hub-Signature-256`.
5. **Componente 5 y 6 (Operación y Soporte):**
   * Eliminar procedimientos de mantenimiento de Redis.
   * Documentar comandos operativos de FastAPI (`alembic upgrade head`, monitoreo de `/api/v1/health`).
6. **Sincronización:** Reflejar estos cambios en `docs/Actividades/Actividad5_Transicion_Servicio.md`.

---

### Fase B: Replanteamiento de las Diapositivas (`index.html`)
`index.html` es una pieza visual de alta calidad (36 diapositivas con SVG interactivos y CSS personalizado). El plan consiste en preservar la estética y estructura de navegación, modificando quirúrgicamente el contenido técnico:

1. **Slide 5 (Arquitectura de Servicios):**
   * Modificar el diagrama SVG para mostrar: Web React -> n8n -> FastAPI Backend -> PostgreSQL 16 (eliminando la caja de Redis 7).
2. **Slide 6 (Solución Anti-Sobreventa):**
   * Cambiar el concepto de "Doble Candado (Redis + GIST)" a **"Candado Relacional Atómico (PostgreSQL 16 GiST + Expiración Inline)"**.
3. **Slide 10 y 11 (Componentes Desplegados e Infraestructura):**
   * Reemplazar "Spring Boot 3.3.5 / Java 21" por "FastAPI / Python 3.12".
   * Reemplazar "Caché y Bloqueo Redis 7" por "Motor Transaccional PostgreSQL 16 en Supabase".
4. **Slide 12 (Evolución de Base de Datos):**
   * Cambiar "Historial de Migraciones Flyway V1-V7" por **"Gestión de Esquema Versionado con Alembic y Extensión btree_gist"**.
5. **Slide 13 y 14 (Variables de Entorno y Secuencia de Despliegue):**
   * Sustituir variables de Spring/Redis por las de FastAPI/Supabase/Alembic.
6. **Slide 17 y 18 (Gestión de Cambios CHG-01 a CHG-03):**
   * Adaptar la justificación técnica de la gestión de bloqueos sin Redis.
7. **Slide 21 y 23 (Pruebas de Seguridad y Concurrencia):**
   * Actualizar diagramas de secuencia mostrando el rechazo HTTP 409 por violación de exclusión GiST de PostgreSQL.
8. **Sincronización:** Actualizar el archivo raíz `index.html` y la copia en `docs/Presentaciones/Actividad5_Transicion_Servicio.html`.

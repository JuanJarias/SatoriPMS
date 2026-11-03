# Cambios del Commit — Reorganización de Estructura Documental, Diagramas Oficiales y Sincronización con GitHub Projects

> Este documento recoge únicamente los cambios incluidos en el commit actual. Se redacta antes de cada push al repositorio.

---

## 🏗️ Reorganización de Carpetas y Nomenclatura del Proyecto

1. **Estructuración Temática en `docs/`:**
   - Creada carpeta `docs/Presupuesto/`: centraliza `Presupuesto_SatoriPMS.xlsx` (modelo oficial con 684 fórmulas), `Presupuesto.md` (memoria técnica) y `Actividad4_Crisis_Presupuestal.md` (gestión de crisis del 30%).
   - Creada carpeta `docs/Diagramas/`: catálogo oficial de diagramas visuales en Mermaid.
   - Creada carpeta `docs/Reuniones/`: almacena minutas y acuerdos con el cliente (`ReunionCliente.md`).
   - Creada carpeta `docs/Actividades/`: reubicado el archivo de requerimientos académicos (`ACTIVIDAD 4 (Escenarios de Crisis Presupuestal).pdf`) fuera de la raíz del proyecto.
   - Actualizado `docs/README.md`: transformado en el índice maestro navegable de la documentación del sistema.

2. **Estandarización PascalCase en Módulos (`docs/modulos/`):**
   - Renombrado `docs/modulos/Tienda_Inventario.md` $\rightarrow$ `docs/modulos/TiendaInventario.md`.
   - Renombrado `docs/modulos/estado_actual.md` $\rightarrow$ `docs/modulos/EstadoActual.md`.
   - Actualizados todos los enlaces y referencias en `README.md` principal para apuntar a las nuevas rutas y nombres normalizados.

---

## 📊 Incorporación de Diagramas Oficiales (`docs/Diagramas/`)

Se elaboraron y publicaron 5 diagramas arquitectónicos y de flujos de negocio en formato Mermaid sin solapamiento de texto, con cajas estilizadas y paleta de color institucional:

1. **`01_Infraestructura_Servicios.md`:** Topología completa de contenedores en Docker Compose (Spring Boot :8080, React :5173, n8n :5678, PostgreSQL :5432, Redis :6379), redes privadas (`satori-network`), volúmenes de persistencia y conexiones externas (Meta WhatsApp, Gemini Flash Lite, Cloudflare y MercadoPago).
2. **`02_Flujo_Reserva_WhatsApp.md`:** Diagrama de secuencia integral del ciclo de reserva conversacional: interpretación con IA, consulta de inventario, bloqueo de 15 min, selección de abono (50% / 100%) y confirmación en PostgreSQL.
3. **`03_Concurrencia_Doble_Candado.md`:** Flujo de prevención de overbooking en 2 niveles (Nivel 1 preventivo en memoria con `RedisLockService` y Nivel 2 estructural con `EXCLUDE USING gist` en PostgreSQL 16).
4. **`04_Gestion_Operativa_Recepcion.md`:** Secuencia de la App Web en recepción: sincronización bidireccional mediante WebSockets STOMP, check-in, cobro de saldos (`/pay-remaining`), check-out y liquidación de consumos de tienda (RN-04).
5. **`05_Ciclo_Vida_Reserva.md`:** Máquina de estados finita de una reserva (`DRAFT_LOCK` $\rightarrow$ `CONFIRMED` $\rightarrow$ `CHECKED_IN` $\rightarrow$ `CHECKED_OUT`), con la escala oficial de reembolsos y penalizaciones por cancelación (RN-03).
6. **`README.md` (Índice de Diagramas):** Catálogo con descripciones, convenciones de visualización y enlaces directos.

---

## 🔄 Sincronización con GitHub Projects #2

1. **Alineación de Cronograma en `docs/modulos/GestionProyecto.md`:**
   - Sincronizados los 5 Sprints oficiales del proyecto con fechas, duraciones y estados según el tablero [GitHub Projects #2](https://github.com/users/JuanJarias/projects/2):
     * Sprint 1 (23/09 al 02/10/2026, 10 d) [Done]
     * Sprint 2 (03/10 al 16/10/2026, 14 d) [Done]
     * Sprint 3 (17/10 al 30/10/2026, 14 d) [In Progress / Cierre]
     * Sprint 4 (31/10 al 13/11/2026, 14 d) [Backlog]
     * Sprint 5 (14/11 al 27/11/2026, 14 d) [Backlog]
2. **Contextualización de Crisis en `Actividad4_Crisis_Presupuestal.md`:**
   - La crisis del 30% de sobrecosto (+180 h / +45 SP / +$6.300.000 COP) se sitúa en el cierre del Sprint 3 al probar la concurrencia entre recepción web y WhatsApp.
   - Las 9 historias aplazadas a Fase 2 corresponden con exactitud matemática a las issues reales de Finanzas, Tienda y Reseñas del **Sprint 4** de GitHub Projects #2 (`HU-07`, `HU-13`, `CU-06`, `HU-01`, `CU-05`, `CU-07`, `HU-14`, `HU-12`, `HU-10`), preservando intacto el núcleo transaccional.

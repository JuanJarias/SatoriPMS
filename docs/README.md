# Documentación SatoriPMS (n8n + PostgreSQL + Redis)

Documentación ágil: vive junto al código y se actualiza en el mismo cambio que modifica un flujo, sin burocracia extra.

| # | Documento | Para qué sirve |
|---|-----------|-----------------|
| 01 | [Arquitectura de infraestructura](01-arquitectura-infraestructura.md) | Cómo interactúan n8n, workers, Redis y PostgreSQL |
| 02 | [Registro maestro de flujos](02-registro-maestro-flujos.md) | Inventario rápido de todos los workflows |
| 03 | [Guía de diseño modular](03-guia-diseno-modular.md) | Reglas para construir flujos pequeños, con Sticky Notes y contrato de sesión |
| 04 | [Seguridad y credenciales](04-seguridad-credenciales.md) | Cómo se manejan los secretos y las credenciales usadas |
| 05 | [Manejo de errores y resiliencia](05-manejo-errores.md) | Validación, reintentos y ramas de error |
| 06 | [Roadmap: WhatsApp Flows](06-roadmap-whatsapp-flows.md) | Idea futura (formularios nativos con selector de fechas) — no implementada |
| — | [sql/001_reservas.sql](sql/001_reservas.sql) | Tablas `reservas` y `habitaciones` usadas por el flujo V2 |

## Notas de importación de los flujos entregados

- **`V2_ChatbotReserva.json`**: toma como base el V1 (no lo reemplaza ni lo modifica). Al importarlo en n8n:
  1. Reasignar la credencial de Postgres (buscar el placeholder `POSTGRES_CRED_ID` en los nodos `PG Buscar Disponibilidad` y `PG Guardar Reserva PAGADA`).
  2. Confirmar que la credencial `Redis account` apunte a la instancia correcta.
  3. Ejecutar `docs/sql/001_reservas.sql` contra la base de datos antes de activar el flujo.
  4. El flujo se importa **inactivo** (`active: false`) a propósito, para poder revisarlo antes de ponerlo en producción junto al V1.
- **`V2_InactivityManager.json`**: workflow independiente, disparado por un `Schedule Trigger` cada 1 minuto. Revisa todas las claves `session:*` en Redis; a los 10 minutos de inactividad envía un aviso por WhatsApp, y si pasa 1 minuto más sin actividad, borra la sesión (el usuario vuelve a empezar desde cero en su próximo mensaje). También requiere reasignar la credencial `Redis account`.

## Qué cambió respecto al V1 (resumen funcional)

- **Salida del escalamiento**: escribir *menú* (o "hola", "inicio", etc.) ahora saca al usuario del modo "atendido por agente" aunque `agent_active` siga en `true` en la sesión.
- **Reserva completa hasta `PAGADA`**: se añadió selección real de habitación (consulta a `habitaciones` en Postgres), captura de datos del huésped, resumen de confirmación, simulación de pago y guardado final en la tabla `reservas` con `estado = 'PAGADA'`.
- **Botones y listas interactivas**: el menú principal y la selección de habitación usan mensajes de tipo `list` (hasta 10 opciones); la confirmación y el pago usan `reply buttons` (hasta 3 opciones). El nodo `Construir Payload WhatsApp` arma el JSON correcto según `response_type` (`text` | `buttons` | `list`).
- **Inactividad**: flujo separado (`V2_InactivityManager.json`) en lugar de mezclarlo dentro del chatbot, siguiendo la regla de una responsabilidad por flujo.
- **WhatsApp Flows (formularios nativos con selector de fechas)**: quedó registrado como idea futura en el roadmap del proyecto, sin implementarse todavía — no se tocó nada del flujo actual para esto.

# Estado Actual del Proyecto (SatoriPMS)

Este documento resume el progreso real del proyecto a un alto nivel.

## ✅ Lo que Funciona
- **Infraestructura:** Docker Compose despliega Postgres, Redis, n8n y la API de Spring Boot de forma interconectada.
- **Base de Datos:** Flyway ejecuta las migraciones correctamente (crea esquemas, inserta datos semilla). La restricción atómica anti-solapamiento (`EXCLUDE`) está activa.
- **API Backend:**
  - Consulta de disponibilidad (`/api/rooms/availability`).
  - Bloqueo temporal en Redis (`/api/bookings/lock`).
  - Creación de reserva (batch) en BD (`/api/bookings/confirm`).
- **App Web (Debug):** Vista en tiempo real de reservas conectada a la BD mediante React Query. Creación manual de reservas desde el frontend habilitada y funcional.
- **Chatbot (Flujo V5/V6):** 
  - Soporta sesión conversacional en Redis (`session:<wa_id>`).
  - Permite hacer reserva guiada paso a paso.
  - Soporta la selección de *múltiples habitaciones* simultáneas en el chat (Ej: "1, 2").
  - Confirma la reserva guardando en BD exitosamente (como `pending_payment`).
  - Escalamiento a agente (cambio de estado en Redis).

## ❌ Lo que NO Funciona (o aún no implementado)
- **Cobros Reales:** El chatbot salta el paso de pago. No hay integración finalizada de MercadoPago.
- **Asistente IA 100% Autónomo:** El módulo de IA que toma control absoluto de la reserva (HU-09) aún no está en el flujo. La IA actualmente solo extrae datos (normalización).
- **Flujo de Revisar/Cancelar:** En desarrollo para la V6. El usuario necesita un método para cancelar vía chatbot.
- **Reseñas:** Opciones de menú presentes, pero lógicas inactivas.
- **Diseño App Web:** El frontend actual es funcional (debug) pero carece del diseño UX/UI final (Tailwind).

## 🔜 Próximos Pasos (Falta)
1. Integrar MercadoPago Sandbox al flujo de n8n (Crear preferencia de pago y retornar el link al usuario).
2. Desarrollar el Sub-flujo de "Revisar o Cancelar reserva" (requiere pedir el UUID de reserva y validarlo en BD).
3. Desarrollar el modo de reserva guiado 100% por IA.
4. Extender la App Web para gestionar el catálogo de productos (Tienda).

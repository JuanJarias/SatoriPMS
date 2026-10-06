# Cambios del Commit — Sprint 2 (28/09 – 09/10/2026)

> Este documento recoge únicamente los cambios incluidos en el commit actual. Se redacta antes de cada push al repositorio.

---

## 🐛 Bugs Solucionados

1. **Error 403 en confirmación de reservas (`SecurityConfig.java`):** Se corrigió una coma sobrante en `List.of(...)` que impedía la compilación limpia de Spring Security, dejando activo el rechazo 403 en `/api/bookings/confirm` y rutas relacionadas.

2. **Serialización doble del payload en n8n:** El nodo `API Confirmar Reserva` enviaba `JSON.stringify($json.payload)` (string) en lugar del objeto JSON real. Corregido para pasar `$json.payload` directamente, permitiendo que Axios serialice correctamente el cuerpo de la petición.

3. **Auto-bloqueo al confirmar reserva (`BookingService`):** El servicio rechazaba su propia confirmación porque leía el lock de Redis (puesto por el propio flujo) como un conflicto. Corregido para verificar colisiones reales solo en PostgreSQL y validar el `lockToken` del usuario en Redis.

4. **Filtro de nombres cortos de acompañantes:** Se cambió `.filter(n => n.length > 2)` a `.filter(n => n.length > 2)` en el nodo de validación de acompañantes, para admitir nombres cortos e iniciales sin relajar la exigencia de la cantidad exacta ($N - 1$ nombres).

5. **Modelo de Gemini inexistente:** La URL del nodo de IA en n8n apuntaba a `gemini-3.8-flash` (modelo que no existe, devolvía 404). Corregida a `gemini-2.0-flash`.

6. **Constraint de `payment_status`:** El service intentaba escribir valores como `refund_pending` o `no_refund` que no están permitidos por el `CHECK` de PostgreSQL (`pending`, `paid`, `refunded`, `partial`). Corregido para usar solo los valores válidos.

---

## 🆕 Añadidos y Mejoras

- **Compilación ultrarrápida (Host + Docker):** Se rediseñó el `Dockerfile` y `start-dev.sh` para compilar el JAR en el host con Maven local (~3 segundos) y montarlo en una imagen JRE ligera, eliminando los ~5 minutos de descarga de dependencias dentro de Docker.

- **Endpoints de Consulta y Cancelación de Reservas (Backend):**
  - `GET /api/bookings/group/{code}` → devuelve `ReservationDetailsDto` con datos completos de la reserva y cálculo de política de reembolso (RN-03).
  - `POST /api/bookings/group/{code}/cancellation` → cambia estado a `cancelled`, libera habitaciones y devuelve `CancellationResponseDto` con porcentaje y monto estimado de reembolso.
  - Nuevos DTOs: `ReservationDetailsDto.java`, `CancellationResponseDto.java`.
  - Nuevo método en `BookingRepository`: `findByReservationGroupCodePrefix`.

- **Subflujo "Revisar o Cancelar Reserva" en V6 (n8n):** Implementado el flujo conversacional completo: solicitud del código único de reserva, consulta al backend, presentación de detalles (sin estados internos de habitación), cálculo y presentación de la política de reembolso aplicable, doble confirmación y ejecución de la cancelación.

- **Privacidad de conversaciones:** Se añadió la carpeta `chat/` a `.gitignore` para que los registros locales de conversaciones no se suban al repositorio.

- **Limpieza de infraestructura de tunnels:** Se eliminó `docker-compose.tunnel.yml` y toda referencia a Ngrok y Zrok en scripts y configuración. El entorno de desarrollo es 100% local.

- **Estructura documental de módulos:** Se reorganizaron los archivos en `docs/modulos/` eliminando los prefijos numéricos de los nombres de archivo. Se actualizaron todos los módulos con la descripción funcional completa del proyecto según el Documento Maestro y las decisiones tomadas durante el sprint.

---

## 📌 Planteado por Hacer (Siguientes Tareas)

- **Pagos MercadoPago Sandbox:** Añadir nodo HTTP en V6 para generar un link de pago y endpoint de webhook en Spring Boot para confirmar el pago y actualizar el estado de la reserva a `confirmed`/`paid`.
- **Reseñas persistidas:** Migrar `ReviewController` a entidad JPA + `ReviewRepository` real.
- **Panel de habitaciones y check-in/out:** Vistas de la aplicación web pendientes para Sprint 3.

---

## 💡 Nombre sugerido para el commit

```
feat(sprint2): reserva en BD, cancelación con reembolso y pipeline rápido
```

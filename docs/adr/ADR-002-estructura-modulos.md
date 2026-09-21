# ADR-002: Estructura de módulos del backend

- **Estado**: Aceptado
- **Fecha**: Sprint 1 — semana del 14/09/2026

## Contexto

Con 3 desarrolladores trabajando en paralelo, la estructura de módulos determina la frecuencia de conflictos de merge.

## Decisión

Organizar el backend **por dominio** (siguiendo las épicas), no por capa técnica.

```
src/
  reservas/       # CU-01, CU-02, CU-08, RN-01, RN-02, RN-03
  habitaciones/   # HU-03, estados de habitación, disponibilidad
  estancias/      # CU-03 (check-in), CU-04 (check-out)
  finanzas/       # CU-06, HU-01, HU-07, HU-13
  tienda/         # CU-05, CU-07, HU-14
  resenas/        # HU-02, HU-04, HU-10, HU-12
  identidad/      # HU-05, HU-11, HU-15
  realtime/       # Gateway WebSocket, publicación de eventos
  integraciones/  # WhatsApp Cloud API, MercadoPago, n8n
```

## Consecuencias

- Cada issue de GitHub toca una sola carpeta → menos conflictos de merge
- Los módulos son cohesivos con las épicas → trazabilidad directa

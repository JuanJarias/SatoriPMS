# ADR-001: Stack tecnológico de SatoriPMS

- **Estado**: Pendiente de decisión (Sprint 1, TASK-03)
- **Fecha**: Sprint 1 — semana del 14/09/2026
- **Autores**: JuanJarias, Gafoxx, Esteban-GV

## Contexto

El proyecto SatoriPMS requiere decidir el stack tecnológico antes de comenzar a implementar. Las decisiones clave son el motor de base de datos y el framework de backend.

## Decisiones

### Base de datos: PostgreSQL 16 ✅

**Motivo**: PostgreSQL es el único motor que permite implementar la restricción de exclusión (`EXCLUDE USING gist`) que previene físicamente la doble reserva — la causa raíz del problema del negocio.

```sql
CONSTRAINT sin_solape EXCLUDE USING gist (
  habitacion_id WITH =, estancia WITH &&
) WHERE (estado IN ('confirmada','en_curso'))
```

### Orquestación del chatbot: n8n autoalojado ✅

**Motivo**: Nodo nativo de WhatsApp Cloud API, flujos conversacionales visuales y auditables, soporte de AI Agent con herramientas.

**Regla crítica**: n8n orquesta la conversación; **nunca implementa reglas de negocio**. RN-01, RN-02, RN-03 viven en el backend.

### Backend: [PENDIENTE — decidir en TASK-03]

Opciones:
- **Spring Boot (Java)**: mejor para transacciones y concurrencia, más ceremonia
- **NestJS (TypeScript)**: un solo lenguaje en todo el stack, más rápido para prototipar

### Frontend: React + Vite + TypeScript + Tailwind + TanStack Query ✅

**Motivo**: Responsive real, caché que se reconcilia con eventos WebSocket.

## Consecuencias

- La restricción de exclusión de PostgreSQL es la garantía de consistencia del sistema
- Redis complementa con el bloqueo temporal de 15 minutos (RN-02)
- La decisión de backend determina el lenguaje de todos los componentes del servidor

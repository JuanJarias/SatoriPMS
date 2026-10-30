# Documentación Oficial — Torre Satori PMS

Bienvenido al repositorio documental de **SatoriPMS**, el Property Management System diseñado para automatizar y centralizar la operación del hotel boutique Torre Satori en Sevilla (Valle del Cauca).

Este directorio organiza todo el conocimiento técnico, arquitectónico, presupuestal y de gestión del proyecto en carpetas especializadas.

---

## Estructura de la Documentación

```
docs/
├── modulos/               # Documentación modular de los 14 componentes del sistema
├── Diagramas/             # Diagramas oficiales de arquitectura, infraestructura y flujos
├── Presupuesto/           # Presupuesto oficial en Excel, memorias de costeo y plan de crisis
├── Reuniones/             # Minutas y actas de reuniones con el cliente / stakeholder
├── Actividades/           # Guías académicas y requerimientos del curso (PI2)
├── cambios_commit.md      # Registro cronológico detallado de cambios por commit
└── README.md              # Este índice
```

---

## 1. Módulos de Arquitectura y Negocio ([`modulos/`](modulos/))

Documentación exhaustiva de las reglas de negocio, endpoints y diseños de cada componente bajo nomenclatura estandarizada:

| Módulo | Archivo | Descripción |
|---|---|---|
| **01. Generalidades y Núcleo** | [`GeneralidadesNucleo.md`](modulos/GeneralidadesNucleo.md) | Contexto, problema de negocio, alcance del MVP, épicas y reglas RN-01 a RN-04. |
| **02. Chatbot WhatsApp** | [`Chatbot.md`](modulos/Chatbot.md) | Especificación de los flujos conversacionales en n8n y comandos interactivos. |
| **03. Aplicación Web** | [`AplicacionWeb.md`](modulos/AplicacionWeb.md) | Vistas, componentes y diseño del panel de recepción y administración. |
| **04. Backend API** | [`BackendAPI.md`](modulos/BackendAPI.md) | Endpoints REST en Spring Boot 3.3, contratos DTO y arquitectura hexagonal. |
| **05. Base de Datos** | [`Database.md`](modulos/Database.md) | Modelo entidad-relación, migraciones Flyway V1-V5 y restricciones de integridad. |
| **06. Seguridad y Permisos** | [`Seguridad.md`](modulos/Seguridad.md) | Autenticación JWT, control de acceso por roles y Ley 1581 de protección de datos. |
| **07. Infraestructura** | [`Infraestructura.md`](modulos/Infraestructura.md) | Contenedores Docker, variables de entorno, puertos y políticas de red. |
| **08. Tienda e Inventario** | [`TiendaInventario.md`](modulos/TiendaInventario.md) | Catálogo de productos, cobro de consumos a la habitación y rotación de stock. |
| **09. Facturación y Finanzas** | [`FacturacionFinanzas.md`](modulos/FacturacionFinanzas.md) | Reportes contables, libro de egresos y cálculo de liquidación de recepcionistas. |
| **10. Reseñas y Fidelización** | [`ResenasFidelizacion.md`](modulos/ResenasFidelizacion.md) | Captura de opiniones, persistencia de calificaciones y enlace a Google Reviews. |
| **11. Gestión del Proyecto** | [`GestionProyecto.md`](modulos/GestionProyecto.md) | Marco Scrum, cronograma oficial reorganizado, roles y matriz de riesgos. |
| **12. Diseño UX/UI** | [`DiseñoUXUI.md`](modulos/DiseñoUXUI.md) | Guía de estilos, paleta de colores, tipografías y diseño adaptativo. |
| **13. Estado Actual** | [`EstadoActual.md`](modulos/EstadoActual.md) | **Memoria viva:** Qué está construido, qué está probado y qué está pendiente. |

---

## 2. Diagramas Técnicos y de Flujos ([`Diagramas/`](Diagramas/))

Catálogo de diagramas visuales en Mermaid con iconos y convenciones de color:

* [`01_Infraestructura_Servicios.md`](Diagramas/01_Infraestructura_Servicios.md): Topología Docker, puertos y servicios externos.
* [`02_Flujo_Reserva_WhatsApp.md`](Diagramas/02_Flujo_Reserva_WhatsApp.md): Ciclo conversacional completo con IA, disponibilidad y abonos.
* [`03_Concurrencia_Doble_Candado.md`](Diagramas/03_Concurrencia_Doble_Candado.md): Arquitectura de prevención de overbooking en 2 niveles (Redis + PostgreSQL).
* [`04_Gestion_Operativa_Recepcion.md`](Diagramas/04_Gestion_Operativa_Recepcion.md): Operación de recepción web, WebSockets, check-in y check-out.
* [`05_Ciclo_Vida_Reserva.md`](Diagramas/05_Ciclo_Vida_Reserva.md): Máquina de estados finita y reglas de cancelación RN-03.

---

## 3. Presupuesto y Modelo Financiero ([`Presupuesto/`](Presupuesto/))

Herramientas financieras y de gestión de costos según los lineamientos del Guion 3:

* [`Presupuesto_SatoriPMS.xlsx`](Presupuesto/Presupuesto_SatoriPMS.xlsx): Libro Excel auditado con 5 hojas funcionales y 684 fórmulas dinámicas (0 errores `#REF!`).
* [`Presupuesto.md`](Presupuesto/Presupuesto.md): Informe técnico de costeo, desglose CAPEX vs OPEX, análisis de retorno (Payback de 13,7 meses) y matriz de supuestos.
* [`Actividad4_Crisis_Presupuestal.md`](Presupuesto/Actividad4_Crisis_Presupuestal.md): Plan de contingencia ante crisis de sobrecosto del 30%, alineado al tablero oficial de GitHub Projects #2.

---

## 4. Reuniones y Actas de Acuerdos ([`Reuniones/`](Reuniones/))

* [`ReunionCliente.md`](Reuniones/ReunionCliente.md): Minuta de la sesión de validación con el cliente y stakeholder (6 de octubre de 2026), con enlaces a transcripción y grabación.

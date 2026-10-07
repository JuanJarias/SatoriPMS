# Cambios del Commit — Fix Chatbot Router y Documentación README

> Este documento recoge únicamente los cambios incluidos en el commit actual. Se redacta antes de cada push al repositorio.

---

## 🐛 Bugs Solucionados

1. **Desbloqueo de estados intermedios en n8n (`V6_ChatbotReservas.json`):**
   - El nodo `Enrutar por Estado1` no tenía rutas asignadas para los estados conversacionales del flujo de reserva (`reserva:seleccion_habitacion`, `reserva:huespedes`, `reserva:nombre`, `reserva:identificacion`, `reserva:mascota`, `reserva:acompanantes`, `reserva:confirmacion`).
   - Al llegar a estos pasos, los mensajes caían fuera de los switches y el chatbot se quedaba congelado sin responder.
   - Se mapearon adecuadamente hacia `H Normalizar Paso Reserva` y `H Normalizar Huespedes e Identidad` y se sincronizó el flujo activo en n8n.

2. **Resolución de conflicto en túnel público Zrok (`409 Conflict` / `Bad Gateway`):**
   - El share previo había quedado huérfano en el controller de zrok impidiendo vincular el tráfico entrante de Meta a n8n.
   - Se liberó el share zombi y se reconectó el túnel reservado `n8n-chatbot.shares.zrok.io` en modo headless hacia el puerto 5678, restableciendo el endpoint con respuesta `200 OK`.

---

## 🆕 Añadidos y Mejoras

- **Reestructuración y Mejora Integral del `README.md`:**
   - Documentación exhaustiva con arquitectura de componentes, tabla de servicios Docker y puertos expuestos.
   - Guía de inicio rápido con `./start-dev.sh`.
   - Navegación clara hacia los documentos funcionales y técnicos de los módulos en `docs/modulos/`.

---

## 💡 Nombre sugerido para el commit

```
fix(n8n): enrutar estados de reserva y actualizar documentacion del README
```

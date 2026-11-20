# Guía Paso a Paso para la Demo en Vivo (Fedora + zrok2 + WhatsApp + Wompi + SatoriPMS)

Checklist operativo diseñado específicamente para **este portátil Fedora** en la rama `integracion-fastapi`, con verificaciones previas, errores comunes y **Plan B local** sin internet.

---

## 1. Preparación HOY / Antes de dormir (una sola vez)

### A. Permisos de Docker en Fedora
Tu usuario (`jjarias`) aún no pertenece al grupo `docker`. Ejecuta **una vez**:
```bash
sudo usermod -aG docker "$USER"
newgrp docker
docker info >/dev/null && echo "Docker listo sin sudo"
```

### B. Instalar y autenticar `zrok2`
En este equipo `zrok2` todavía no está instalado ni habilitado:
1. Descarga el binario Linux (`amd64`) desde [releases de zrok](https://github.com/openzrok/zrok/releases) e instálalo en `/usr/local/bin/zrok2` (con `chmod +x`).
2. Habilita tu cuenta:
   ```bash
   zrok2 enable <TU_ZROK_ENABLE_TOKEN>
   ```
3. **Clave para evitar conflicto de dominio (`409` / permiso denegado):**
   - El valor actual de `N8N_PUBLIC_URL` en `.env` solo lo puede abrir la cuenta `zrok2` que reservó ese nombre.
   - Si usas tu propia cuenta `zrok2`, reserva un nombre nuevo una sola vez:
     ```bash
     zrok2 reserve public http://127.0.0.1:5678 -n satoridemofinal
     ```
     y actualiza `N8N_PUBLIC_URL=https://<share_asignado>.shares.zrok.io/` en `.env`.

### C. Configurar llaves reales de Wompi en `.env`
Los valores `...xxxxxxxx` del ejemplo **no sirven**. Edita `.env` y reemplaza por las llaves reales (Consola Wompi → *Desarrolladores → Programación*):
```env
WOMPI_ENABLED=true
WOMPI_API_URL=https://production.wompi.co/v1
WOMPI_CHECKOUT_URL=https://checkout.wompi.co/l/
WOMPI_PUBLIC_KEY=pub_prod_...
WOMPI_PRIVATE_KEY=prv_prod_...
WOMPI_EVENTS_SECRET=prod_events_...
WOMPI_INTEGRITY_SECRET=prod_integrity_...
WOMPI_LINK_EXPIRATION_HOURS=24
```
> **Ojo con Producción vs Sandbox:** con llaves `pub_prod_` / `prv_prod_` en `production.wompi.co`, el cobro es **real** (puedes probar con Nequi por el monto mínimo o usar llaves de pruebas `pub_test_` / `prv_test_` + `WOMPI_API_URL=https://sandbox.wompi.co/v1` + `WOMPI_ENVIRONMENT=sandbox` para tarjetas ficticias `4242...`).  
> En la consola de Wompi (*Desarrolladores → Seguimiento / Eventos*), verifica que la URL de eventos apunte a:  
> **`https://<tu-share>.shares.zrok.io/webhook/wompi-events`**

---

## 2. Dos horas antes de la exposición (Día de la demo)

1. **Renovar `WHATSAPP_TOKEN` en Meta Developers (caduca cada 24 h):**
   - Entra a Meta for Developers → *WhatsApp → API Setup* → genera el token temporal nuevo y pégalo en `WHATSAPP_TOKEN=` en `.env`.
   - Si la app sigue en **Modo Desarrollo**, confirma que **todos los celulares** que enviarán mensajes durante la exposición estén agregados en la lista de *Destinatarios autorizados (To)* en *API Setup*.
   - Confirma en *WhatsApp → Configuración → Webhook*:
     - **Callback URL:** `https://<tu-share>.shares.zrok.io/webhook/whatsapp-webhook`
     - **Verify token:** exactamente el valor de `WHATSAPP_VERIFY_TOKEN` en `.env`.
     - Campo **`messages`** marcado como **Suscrito**.

2. **Arrancar toda la pila con un solo comando:**
   ```bash
   ./scripts/start-dev.sh --sync-flow --open
   ```
   > **Nota crítica si editaste `.env` cuando los contenedores ya estaban arriba:** `n8n` y `api` no releen `.env` en caliente. Fuerza su recreación con:
   > ```bash
   > docker compose --profile n8n up -d --force-recreate api n8n
   > ./scripts/sync-n8n-flow.sh
   > ```

3. **Diagnóstico previo completo antes de salir al escenario:**
   ```bash
   ./scripts/status-dev.sh
   ```
   Confirma **en verde `[OK]`**:
   - Contenedores `satori_postgres`, `satori_api`, `satori_n8n` (`running` / `healthy`).
   - Túnel `zrok2` activo (`[OK]` con URL pública de `N8N_PUBLIC_URL`).
   - `Token válido` en WhatsApp y `App suscrita` a la WABA.

---

## 3. Reglas de oro para evitar errores en vivo

1. **Probar UNA reserva completa antes de entrar al salón** y luego cancelarla (o limpiar datos de prueba) para confirmar que Gemini + PostgreSQL + zrok2 + Wompi + Meta responden en `< 4 s`.
2. **En n8n (`http://localhost:5678`) no edites nodos durante la demo** sin volver a correr `./scripts/sync-n8n-flow.sh`: n8n `2.47.3` ejecuta la versión cacheada en memoria si no cambia `versionId`.
3. **Si Meta no responde pero el flujo ejecutó en verde:** recuerda que los nodos `Enviar Mensaje WhatsApp*` usan `continueRegularOutput`. Abre la ejecución en `http://localhost:5678` → *Executions* para ver el JSON de error exacto de Meta (casi siempre `401` token vencido o número no autorizado en lista de pruebas).
4. **Si el navegador muestra datos viejos:** no uses `reset-dev.sh` en plena presentación (borra toda la base). Usa simplemente `Ctrl+Shift+R` en el navegador o inicia/cierra sesión (`admin / admin123` y `recepcion / recepcion123`).
5. **Revisa también `WhatsApp & Bot` en la web (`http://localhost:5173`):** si probaste `*agente*` o `5` en el ensayo, recuerda reactivar el bot desde la web (**Reactivar Bot IA**) o enviar `menu` / `hola` por WhatsApp; de lo contrario el bot permanece en silencio atendido por humano.

---

## 4. Plan B interactivo para el cliente (si falla internet, `zrok2` o Meta)

Si en el salón bloquean el túnel o vence el token de Meta, el **cliente sí puede probar todas las pantallas y reservas directamente en el navegador (`http://localhost:5173`)**:

### Cómo inicializar todo desde cero en Plan B (sin `zrok2` ni Meta)

1. **Requisitos previos (solo una vez en el portátil):**
   - Permisos de Docker activos en tu usuario (`sudo usermod -aG docker "$USER" && newgrp docker`).
   - En `.env`: `JWT_SECRET` (≥ 32 caracteres), `SATORI_SERVICE_KEY`, `DATABASE_URL=postgresql+psycopg://...` y `COMPOSE_PROFILES=n8n` (opcional `GOOGLE_PLACES_API_KEY` si habrá WiFi para ver reseñas).

2. **Opción A — Arrancar todo limpio sin túnel (conservando datos actuales):**
   ```bash
   ./scripts/stop-dev.sh
   ./scripts/start-dev.sh --no-tunnel --sync-flow --open
   ./scripts/status-dev.sh --no-meta
   ```

3. **Opción B — Reiniciar la base de datos 100% desde cero (recomendado antes de exponer si hiciste pruebas):**
   Borra reservas, ventas y sesiones anteriores, deja intactas las **9 habitaciones reales**, el catálogo inicial y las cuentas `admin / admin123` y `recepcion / recepcion123`, conservando tu usuario de n8n:
   ```bash
   ./scripts/reset-dev.sh --keep-n8n -y
   ./scripts/start-dev.sh --no-tunnel --sync-flow --open
   ./scripts/status-dev.sh --no-meta
   ```
   > **Si necesitas borrar absolutamente todo (incluido n8n e imagen Docker de la API):** usa `./scripts/reset-dev.sh --images -y` seguido de `./scripts/start-dev.sh --no-tunnel --sync-flow --open` *(tendrás que abrir `http://localhost:5678` una vez para crear el usuario dueño de n8n).*

4. **Comprobación rápida de 10 segundos tras arrancar:**
   - Web abierta en `http://localhost:5173` (entra con `admin / admin123`).
   - Bot n8n `V10` activo contra PostgreSQL:
     ```bash
     node tests/chatbot/test_e2e_v9_completo.js
     node tests/chatbot/test_escalamiento_agente_humano.js
     ```

### Qué SÍ funciona al 100% para que el cliente pruebe en Plan B
1. **Operación hotelera completa en PostgreSQL:** Habitaciones `1–9` (crear, editar, eliminar), Calendario semanal, Reservas manuales (con **bloqueo automático 409** ante solapes y cancelación con reembolso RN-03), Llegadas (Check-in), Salidas (Check-out consolidando consumos).
2. **Tienda Torre Satori & Salgados Café:** crear/editar/eliminar productos como Admin (**+ Nuevo producto** / **Editar** / **Eliminar** en `Tienda Hotel`), vender en efectivo o cargar a la habitación, y pedidos de cafetería a cocina/folio.
3. **Gerencia:** Resumen financiero real, registro y anulación de egresos, eventos y descuentos especiales por noche, descarga real de **Excel (`.xlsx`)**, gestión de usuarios y **Logs de Auditoría inmutables**.
4. **Chatbot (experiencia visual + flujo real en backend):**
   - **Para el cliente (visual e interactivo):** pestaña **WhatsApp & Bot → Simulador Sandbox**, donde recorre paso a paso fechas, huéspedes, mascota, elige entre las 9 habitaciones reales y **crea una reserva real en PostgreSQL** que aparece al instante en **Reservas** y **Calendario**.
   - **Para demostrar n8n `V10` + IA + PostgreSQL sin Meta:**
     ```bash
     node tests/chatbot/test_e2e_v9_completo.js
     node tests/chatbot/test_escalamiento_agente_humano.js
     ```
     y mostrar en la pestaña **WhatsApp & Bot → Sesiones WhatsApp** cómo aparece la sesión en PostgreSQL, alternar **Pausar Bot / Reactivar Bot IA** y responder manualmente desde recepción.

### Limitaciones exactas del Plan B (sin Meta / sin Wompi / sin internet)
| Capacidad | En modo Vivo (`zrok2` + Meta + Wompi) | En Plan B local / sin internet |
|---|---|---|
| **WhatsApp desde celular real** | El huésped escribe desde su teléfono y recibe respuestas reales en WhatsApp. | **No llega al teléfono físico** porque `graph.facebook.com` requiere internet, `WHATSAPP_TOKEN` vigente y túnel público. |
| **Pasarela Wompi real** | Abre el enlace real `checkout.wompi.co/l/...` y el webhook `transaction.updated` confirma la reserva. | **No abre el checkout externo** ni recibe webhooks desde Wompi; se muestra la reserva en `PENDIENTE_PAGO` / Simulador y se confirma desde recepción. |
| **Google Places Reseñas** | Consulta reseñas reales desde Google Places API. | **Sí funciona en Plan B** (no usa `zrok2` ni Meta): requiere solo internet normal + `GOOGLE_PLACES_API_KEY` en `.env` (queda en caché en `api` si se abre antes). |

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

## 4. Plan B local (si falla el WiFi del salón, `zrok2` o Meta)

Si en el salón bloquean puertos o cae Meta/Wompi, **todo el PMS + chatbot n8n + PostgreSQL funcionan 100% local sin internet**:

1. **Panel web completo en vivo (`http://localhost:5173`):**
   - Muestra **Habitaciones `1–9`**, **Calendario**, creación de reserva manual, **error real 409** al solapar fechas (`EXCLUDE USING gist`), carga de **Tienda / Salgados Café**, exportación real **`.xlsx`** y **Logs de Auditoría**.
   - Usa la pestaña **WhatsApp & Bot → Simulador Sandbox** para demostrar la experiencia móvil paso a paso creando una reserva real en PostgreSQL.
2. **Prueba E2E real del flujo n8n `V10` directo contra `localhost:5678` (sin Meta ni túnel):**
   ```bash
   node tests/chatbot/test_e2e_v9_completo.js
   node tests/chatbot/test_escalamiento_agente_humano.js
   ```
3. **Simular confirmación de pago Wompi firmada (si hay acceso al botón/terminal sin pasarela real):**
   - Desde **WhatsApp & Bot** o terminal con `X-Service-Key` puedes confirmar pago externo sobre el código `TS-XXXX` generado y ver reflejada la transición `PENDIENTE_PAGO → CONFIRMADA` al instante por SSE en la web.

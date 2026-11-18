# Chatbot de Reservas V9 — Cobro con Wompi

`V9_ChatbotReservas.json` es el flujo V8 (`../V8_ChatbotReservas.json`, que no se modificó) con el **cobro de la reserva conectado a Wompi**. El script `tests/chatbot/build_v9_chatbot_flow.py` lo genera a partir del V8, así que el resto del flujo es idéntico byte a byte: menú, reserva guiada, reserva con IA, reseñas, consulta/cancelación/pago de saldo, escalamiento e inactividad.

```bash
python3 tests/chatbot/build_v9_chatbot_flow.py   # regenera el V9 desde el V8
```

## Qué cambia respecto al V8

| Nodo | Cambio |
| :--- | :--- |
| `API Confirmar Reserva` | Ahora conecta con `H Preparar Cobro Wompi`; antes iba directo a `H Reserva Exitosa`. |
| `H Preparar Cobro Wompi` *(nuevo)* | Calcula el valor a cobrar según la modalidad elegida: **50% de anticipo** o **100%**, en centavos COP. Arma el request del link: un solo uso, vencimiento y `sku` = código `TS-XXXX`. |
| `¿Generar Link Wompi?` *(nuevo)* | Solo cobra si la reserva quedó confirmada, `WOMPI_ENABLED` no es `false`, existe la llave privada y el monto es ≥ $1.500. |
| `Wompi Crear Link de Pago` *(nuevo)* | `POST {WOMPI_API_URL}/payment_links` con `Authorization: Bearer WOMPI_PRIVATE_KEY`. |
| `¿Link Wompi Creado?` → `H Datos Registro Link Wompi` → `Redis Registrar Link Wompi` *(nuevos)* | Guardan `wompi:link:<id>` → `{wa_id, código, modalidad, monto}` para asociar después los eventos de pago con el huésped. |
| `H Reserva Exitosa` | Envía el resumen con el **enlace `https://checkout.wompi.co/l/<id>`**. Si Wompi falla, le pide al huésped escribir *agente*. |

Este es el mensaje que recibe el huésped:

```
*¡Tu reserva ha sido registrada con éxito!*

• Código de reserva: *TS-1A2B*
• Total de la estadía: *$580.000*
• Valor a pagar ahora: *$290.000* _(Anticipo del 50%)_
• Saldo pendiente: *$290.000* _(se paga al momento del check-in)_

*Realiza tu pago de forma segura con Wompi:*
https://checkout.wompi.co/l/AbC123
...
```

### Confirmación de pago (nuevo punto de entrada)

`Webhook Eventos Wompi` (`POST /webhook/wompi-events`) → `H Verificar Evento Wompi` → `¿Evento Wompi Válido?` → `Redis Obtener Link Wompi` → `H Mensaje Estado Pago Wompi` → `¿Notificar Huésped Pago?` → `Enviar Estado Pago WhatsApp`.

- La firma se valida con SHA-256 según la [documentación de eventos de Wompi](https://docs.wompi.co/docs/colombia/eventos/): `SHA256(valores de signature.properties + timestamp + WOMPI_EVENTS_SECRET)`. El SHA-256 está implementado en JavaScript puro, así que no hace falta habilitar `crypto` en n8n.
- Si el evento es válido y su estado es `APPROVED`, `DECLINED`, `ERROR` o `VOIDED`, el huésped recibe el resultado por WhatsApp.

## Variables de entorno (`.env`, nunca en el repositorio)

| Variable | Uso |
| :--- | :--- |
| `WOMPI_PRIVATE_KEY` | Crear links de pago (`prv_prod_...`). |
| `WOMPI_EVENTS_SECRET` | Validar la firma de los eventos (`prod_events_...`). |
| `WOMPI_PUBLIC_KEY`, `WOMPI_INTEGRITY_SECRET` | Reservadas para Web Checkout/Widget; los links de pago no las usan. |
| `WOMPI_API_URL` | `https://production.wompi.co/v1` (sandbox: `https://sandbox.wompi.co/v1`). |
| `WOMPI_CHECKOUT_URL` | Base del enlace: `https://checkout.wompi.co/l/`. |
| `WOMPI_LINK_EXPIRATION_HOURS` | Vigencia del link (24 h por defecto). |
| `WOMPI_REDIRECT_URL` | Opcional: página a la que vuelve el huésped tras pagar. |
| `WOMPI_ENABLED` | `false` para desactivar el cobro sin cambiar el flujo. |

## Despliegue

1. Completa las variables `WOMPI_*` en `.env` y reinicia n8n (`docker compose up -d n8n`).
2. Importa `V9_ChatbotReservas.json` en n8n. Viene **inactivo** porque usa los mismos webhooks de WhatsApp que el V8: **desactiva el V8 y activa el V9**.
3. En el panel de Wompi (*Desarrolladores → Seguimiento de transacciones*), configura la **URL de eventos** como `{N8N_PUBLIC_URL}/webhook/wompi-events`.

## Pruebas

```bash
node tests/chatbot/test_pago_wompi_v9.js           # 11 pruebas en memoria con el código real de los nodos
node tests/chatbot/test_pago_wompi_v9.js --live    # + crea, valida y desactiva un link real en Wompi
python3 tests/chatbot/verify_n8n_flow_integrity.py flows/n8n/v9-wompi/V9_ChatbotReservas.json
API_HOST=localhost node tests/chatbot/test_e2e_reserva_wompi_v9.js   # E2E con el stack levantado
```

## Limitación conocida (backend)

`POST /api/bookings/confirm` sigue registrando el pago (`paid_amount`, `payment_status`) en el momento de confirmar, igual que en el V8, porque el backend no se modificó. El V9 cobra con Wompi y avisa al huésped, pero la conciliación automática en la base de datos (dejar la reserva en `pending` hasta que llegue el evento `APPROVED`) necesita un endpoint nuevo en la API.

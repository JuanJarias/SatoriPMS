#!/usr/bin/env python3
"""
Generador determinista del flujo n8n V9 (Chatbot de Reservas + cobro con Wompi).

Parte del flujo V8 (flows/n8n/V8_ChatbotReservas.json), que NO se modifica, y aplica
exclusivamente el parche del cobro de la reserva:

  1. Tras "API Confirmar Reserva" se calcula el valor a cobrar segun la modalidad que
     eligio el huesped (50% de anticipo o 100%) y se crea un Link de Pago en Wompi
     (POST /v1/payment_links, llave privada).
  2. El link se registra en Redis (wompi:link:<id>) para poder asociar los eventos de
     Wompi con el huesped de WhatsApp.
  3. "H Reserva Exitosa" envia el resumen de la reserva junto con el enlace de pago.
  4. Nuevo punto de entrada "Webhook Eventos Wompi" (POST /webhook/wompi-events):
     valida la firma SHA-256 del evento con el secreto de eventos y notifica al huesped
     por WhatsApp cuando la transaccion queda APPROVED / DECLINED / ERROR / VOIDED.

Todos los demas nodos, conexiones y webhooks del V8 quedan identicos.

Uso:
    python3 tests/chatbot/build_v9_chatbot_flow.py
"""
import copy
import json
import os
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'flows', 'n8n', 'V8_ChatbotReservas.json')
DST_DIR = os.path.join(ROOT, 'flows', 'n8n', 'v9-wompi')
DST = os.path.join(DST_DIR, 'V9_ChatbotReservas.json')

NS = uuid.UUID('6f1c7a52-9d0e-4f43-9b8e-2b9f0c1a5e77')


def nid(name):
    return str(uuid.uuid5(NS, name))


REDIS_CRED = {"redis": {"id": "nbnU5viNmZNWAOZ9", "name": "Redis account"}}

# ─────────────────────────────────────────────────────────────────────────────
# Codigo JS de los nodos nuevos / modificados
# ─────────────────────────────────────────────────────────────────────────────

JS_PREPARAR_COBRO = r"""// V9 · Prepara el cobro de la reserva en Wompi segun la modalidad elegida (50% o 100%).
const api = $input.first().json || {};
const env = (typeof $env !== 'undefined' && $env) ? $env : {};

const source = (() => {
  try { return $('H Procesar Reserva Paso').first().json; } catch (e) {}
  try { return $('H Normalizar IA').first().json; } catch (e) {}
  return {};
})();
const payload = source.payload || {};

const confirmed = Boolean(api.reservationGroupId);
const code = api.code || (confirmed ? ('TS-' + String(api.reservationGroupId).replace(/-/g, '').slice(-4).toUpperCase()) : null);
const totalPrice = Number(api.totalPrice || 0);
const isPartial = api.paymentStatus === 'partial' || payload.paymentOption === 'deposit';
// Valor a cobrar ahora: lo que la API registro para la modalidad elegida
// (deposit = 50% del total, full = 100% del total).
let amountToCharge = api.paidAmount != null ? Number(api.paidAmount) : (isPartial ? totalPrice / 2 : totalPrice);
if (!(amountToCharge > 0)) amountToCharge = isPartial ? totalPrice / 2 : totalPrice;
const amountInCents = Math.round(amountToCharge * 100);

const enabled = String(env.WOMPI_ENABLED == null ? 'true' : env.WOMPI_ENABLED).toLowerCase() !== 'false';
const hasKey = Boolean(env.WOMPI_PRIVATE_KEY);
const hours = Math.max(1, Number(env.WOMPI_LINK_EXPIRATION_HOURS || 24));
const expiresAt = new Date(Date.now() + hours * 3600 * 1000).toISOString();

const optionLabel = isPartial ? 'Anticipo 50%' : 'Pago total 100%';
const stay = (payload.checkIn && payload.checkOut) ? ` (${payload.checkIn} a ${payload.checkOut})` : '';
const wompiRequest = {
  name: `Reserva ${code || ''} - Torre Satori`.trim().slice(0, 60),
  description: `${optionLabel} de la reserva ${code || ''}${stay}`.slice(0, 250),
  single_use: true,
  collect_shipping: false,
  currency: 'COP',
  amount_in_cents: amountInCents,
  expires_at: expiresAt,
  sku: String(code || '').slice(0, 36)
};
if (env.WOMPI_REDIRECT_URL) wompiRequest.redirect_url = env.WOMPI_REDIRECT_URL;

let skipReason = null;
if (!confirmed) skipReason = 'reserva_no_confirmada';
else if (!enabled) skipReason = 'wompi_deshabilitado';
else if (!hasKey) skipReason = 'sin_llave_privada';
else if (!(amountInCents >= 150000)) skipReason = 'monto_invalido';

return [{
  json: {
    wa_id: source.wa_id || payload.waId || '',
    sender_name: source.sender_name || payload.guestName || 'Huésped',
    reservation_code: code,
    payment_option: isPartial ? 'deposit' : 'full',
    total_price: totalPrice,
    amount_to_charge: amountInCents / 100,
    amount_in_cents: amountInCents,
    expires_at: expiresAt,
    wompi_should_charge: skipReason === null,
    wompi_skip_reason: skipReason,
    wompi_request: wompiRequest
  }
}];"""

JS_RESERVA_EXITOSA = r"""// V9 · Resumen de la reserva + enlace de pago Wompi.
const apiResponse = (() => { try { return $('API Confirmar Reserva').first().json || {}; } catch (e) { return {}; } })();
const prep = (() => { try { return $('H Preparar Cobro Wompi').first().json || {}; } catch (e) { return {}; } })();
const wompi = (() => { try { return $('Wompi Crear Link de Pago').first().json || {}; } catch (e) { return {}; } })();
const source = (() => {
  try { return $('H Procesar Reserva Paso').first().json; } catch (e) {}
  try { return $('H Normalizar IA').first().json; } catch (e) {}
  return {};
})();

const wa_id = source.wa_id || prep.wa_id || '';
const sender_name = source.sender_name || prep.sender_name || 'Huésped';
const cop = (n) => '$' + Number(n || 0).toLocaleString('es-CO', { maximumFractionDigits: 0 });

const linkId = wompi && wompi.data && wompi.data.id ? String(wompi.data.id) : null;
const checkoutBase = String((typeof $env !== 'undefined' && $env && $env.WOMPI_CHECKOUT_URL) || 'https://checkout.wompi.co/l/').replace(/\/?$/, '/');
const paymentUrl = linkId ? checkoutBase + linkId : null;

let text = '';
if (apiResponse.reservationGroupId) {
  const code = prep.reservation_code || apiResponse.code || ('TS-' + String(apiResponse.reservationGroupId).replace(/-/g, '').slice(-4).toUpperCase());
  const total = apiResponse.totalPrice != null ? Number(apiResponse.totalPrice) : Number(prep.total_price || 0);
  const toPay = prep.amount_to_charge != null ? Number(prep.amount_to_charge) : Number(apiResponse.paidAmount || 0);
  const isPartial = prep.payment_option ? prep.payment_option === 'deposit' : apiResponse.paymentStatus === 'partial';
  const pending = Math.max(0, total - toPay);

  text = `*¡Tu reserva ha sido registrada con éxito!*\n\n` +
         `• Código de reserva: *${code}*\n` +
         `• Total de la estadía: *${cop(total)}*\n` +
         `• Valor a pagar ahora: *${cop(toPay)}* ${isPartial ? '_(Anticipo del 50%)_' : '_(Pago total 100%)_'}\n`;
  if (isPartial) {
    text += `• Saldo pendiente: *${cop(pending)}* _(se paga al momento del check-in)_\n`;
  }

  if (paymentUrl) {
    let vence = '';
    try {
      vence = new Date(prep.expires_at).toLocaleString('es-CO', { timeZone: 'America/Bogota', dateStyle: 'short', timeStyle: 'short', hourCycle: 'h23' });
    } catch (e) { vence = ''; }
    text += `\n*Realiza tu pago de forma segura con Wompi:*\n${paymentUrl}\n\n` +
            `Puedes pagar con tarjeta, PSE, Nequi o Bancolombia. ` +
            `El enlace es de un solo uso${vence ? ' y vence el *' + vence + '*' : ''}. ` +
            `Te confirmaremos por este chat cuando recibamos el pago.\n\n`;
  } else {
    text += `\nEn este momento no pudimos generar tu enlace de pago. ` +
            `Escribe *agente* y nuestro equipo de recepción te lo enviará en breve.\n\n`;
  }

  text += `Conserva tu código *${code}* para cualquier consulta.\n` +
          `¡Te esperamos en *Torre Satori*!\n\n` +
          `Escribe *menú* para volver al inicio.`;
} else {
  let errorMsg = apiResponse.error || apiResponse.message || apiResponse.detail;
  if (errorMsg && typeof errorMsg === 'object') errorMsg = errorMsg.message || JSON.stringify(errorMsg);
  if (!errorMsg) errorMsg = JSON.stringify(apiResponse);
  text = `Lo sentimos, no pudimos completar tu reserva.\nMotivo: ${errorMsg}.\n\nSi el tiempo de 15 minutos expiró, las habitaciones se liberaron automáticamente. Escribe *menú* para intentar de nuevo.`;
}

return [{
  json: {
    wa_id,
    sender_name,
    response_text: text,
    response_payload: { type: 'text', text: { body: text, preview_url: Boolean(paymentUrl) } },
    payment_url: paymentUrl,
    wompi_link_id: linkId,
    locks_confirmed: Boolean(apiResponse.reservationGroupId),
    session: { state: 'menu', step: 'esperando_opcion', agent_active: false,
               wa_id, sender_name, reservation_draft: {} }
  }
}];"""

JS_REGISTRO_LINK = r"""// V9 · Datos del link para registrarlo en Redis (wompi:link:<id>).
const prep = $('H Preparar Cobro Wompi').first().json;
const link = ($input.first().json && $input.first().json.data) || {};
const hours = Math.max(1, Number(($env && $env.WOMPI_LINK_EXPIRATION_HOURS) || 24));
return [{
  json: {
    redis_key: 'wompi:link:' + link.id,
    redis_ttl: hours * 3600 + 3 * 86400,
    redis_value: JSON.stringify({
      link_id: link.id,
      wa_id: prep.wa_id,
      sender_name: prep.sender_name,
      reservation_code: prep.reservation_code,
      payment_option: prep.payment_option,
      amount_in_cents: prep.amount_in_cents,
      expires_at: prep.expires_at,
      created_at: new Date().toISOString()
    })
  }
}];"""

# SHA-256 en JS puro: evita depender de NODE_FUNCTION_ALLOW_BUILTIN=crypto en n8n
# y no deja el secreto de eventos en los datos de ejecucion de nodos intermedios.
JS_VERIFICAR_EVENTO = r"""// V9 · Verifica la firma de un evento de Wompi (SHA-256 con el secreto de eventos).
// https://docs.wompi.co/docs/colombia/eventos/
function sha256Hex(ascii) {
  const bytes = unescape(encodeURIComponent(ascii));
  const K = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  let H = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  const l = bytes.length;
  const words = [];
  for (let i = 0; i < l; i++) words[i >> 2] |= bytes.charCodeAt(i) << (24 - (i % 4) * 8);
  words[l >> 2] |= 0x80 << (24 - (l % 4) * 8);
  words[(((l + 8) >> 6) + 1) * 16 - 1] = l * 8;
  const rotr = (x, n) => (x >>> n) | (x << (32 - n));
  for (let i = 0; i < words.length; i += 16) {
    const w = new Array(64);
    for (let t = 0; t < 64; t++) {
      if (t < 16) w[t] = words[i + t] | 0;
      else {
        const s0 = rotr(w[t-15], 7) ^ rotr(w[t-15], 18) ^ (w[t-15] >>> 3);
        const s1 = rotr(w[t-2], 17) ^ rotr(w[t-2], 19) ^ (w[t-2] >>> 10);
        w[t] = (w[t-16] + s0 + w[t-7] + s1) | 0;
      }
    }
    let [a, b, c, d, e, f, g, h] = H;
    for (let t = 0; t < 64; t++) {
      const S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
      const ch = (e & f) ^ (~e & g);
      const t1 = (h + S1 + ch + K[t] + w[t]) | 0;
      const S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
      const maj = (a & b) ^ (a & c) ^ (b & c);
      const t2 = (S0 + maj) | 0;
      h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = b; b = a; a = (t1 + t2) | 0;
    }
    H = [(H[0]+a)|0,(H[1]+b)|0,(H[2]+c)|0,(H[3]+d)|0,(H[4]+e)|0,(H[5]+f)|0,(H[6]+g)|0,(H[7]+h)|0];
  }
  return H.map(x => (x >>> 0).toString(16).padStart(8, '0')).join('');
}

const raw = $input.first().json || {};
const evt = (raw.body && typeof raw.body === 'object') ? raw.body : raw;
const secret = (typeof $env !== 'undefined' && $env && $env.WOMPI_EVENTS_SECRET) || '';
const data = evt.data || {};
const tx = data.transaction || {};
const sig = evt.signature || {};
const props = Array.isArray(sig.properties) ? sig.properties : [];

const pick = (obj, path) => path.split('.').reduce((acc, k) => (acc == null ? undefined : acc[k]), obj);
const concatenated = props.map(p => { const v = pick(data, p); return v == null ? '' : String(v); }).join('')
  + String(evt.timestamp == null ? '' : evt.timestamp) + secret;
const computed = sha256Hex(concatenated);
const received = String(sig.checksum || (raw.headers && (raw.headers['x-event-checksum'] || raw.headers['X-Event-Checksum'])) || '');

const valid = Boolean(secret) && props.length > 0 && received.length === 64 && computed.toLowerCase() === received.toLowerCase();
const FINAL = ['APPROVED', 'DECLINED', 'ERROR', 'VOIDED'];
const status = String(tx.status || '').toUpperCase();

return [{
  json: {
    valid,
    invalid_reason: valid ? null : (!secret ? 'sin_secreto_eventos' : (!props.length ? 'sin_firma' : 'checksum_no_coincide')),
    event: evt.event || null,
    environment: evt.environment || null,
    transaction_id: tx.id || null,
    status,
    amount_in_cents: Number(tx.amount_in_cents || 0),
    reference: tx.reference || null,
    payment_method_type: tx.payment_method_type || null,
    payment_link_id: tx.payment_link_id || null,
    should_notify: valid && evt.event === 'transaction.updated' && Boolean(tx.payment_link_id) && FINAL.includes(status),
    redis_key: tx.payment_link_id ? 'wompi:link:' + tx.payment_link_id : null
  }
}];"""

JS_MENSAJE_PAGO = r"""// V9 · Mensaje al huesped segun el estado final de la transaccion Wompi.
const ev = $('H Verificar Evento Wompi').first().json;
const raw = $input.first().json || {};
let link = {};
try { link = typeof raw.value === 'string' ? JSON.parse(raw.value) : (raw.value || {}); } catch (e) { link = {}; }

const cop = (n) => '$' + Number(n || 0).toLocaleString('es-CO', { maximumFractionDigits: 0 });
const amount = cop(ev.amount_in_cents / 100);
const code = link.reservation_code || 'de tu reserva';
const METHODS = { CARD: 'tarjeta', NEQUI: 'Nequi', PSE: 'PSE', BANCOLOMBIA_TRANSFER: 'Bancolombia', BANCOLOMBIA_QR: 'QR Bancolombia', DAVIPLATA: 'Daviplata' };
const method = METHODS[ev.payment_method_type] || ev.payment_method_type || '';

let text = '';
if (ev.status === 'APPROVED') {
  text = `*¡Pago recibido!*\n\n` +
         `Confirmamos el pago de *${amount}*${method ? ' con ' + method : ''} para la reserva *${code}*.\n` +
         `• Transacción Wompi: ${ev.transaction_id}\n` +
         (link.payment_option === 'deposit' ? `• Recuerda que el saldo restante se paga al momento del check-in.\n` : `• Tu estadía quedó pagada en su totalidad.\n`) +
         `\n¡Te esperamos en *Torre Satori*! Escribe *menú* si necesitas algo más.`;
} else {
  const estados = { DECLINED: 'rechazado', ERROR: 'no pudo procesarse', VOIDED: 'anulado' };
  text = `Tu pago de *${amount}* para la reserva *${code}* fue *${estados[ev.status] || ev.status}*.\n\n` +
         `Puedes intentarlo nuevamente con otro medio de pago o escribir *agente* para que recepción te ayude.`;
}

return [{
  json: {
    wa_id: link.wa_id || null,
    notify: Boolean(link.wa_id),
    status: ev.status,
    reservation_code: link.reservation_code || null,
    transaction_id: ev.transaction_id,
    response_text: text
  }
}];"""


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de nodos
# ─────────────────────────────────────────────────────────────────────────────

def code_node(name, js, pos):
    return {"parameters": {"jsCode": js}, "id": nid(name), "name": name,
            "type": "n8n-nodes-base.code", "typeVersion": 2, "position": pos}


def if_bool_node(name, expr, pos, cid):
    return {
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                "conditions": [{
                    "id": cid, "leftValue": expr, "rightValue": "",
                    "operator": {"type": "boolean", "operation": "true", "singleValue": True}
                }],
                "combinator": "and"
            },
            "looseTypeValidation": True,
            "options": {}
        },
        "id": nid(name), "name": name, "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": pos
    }


def whatsapp_node(name, pos):
    return {
        "parameters": {
            "method": "POST",
            "url": "={{ 'https://graph.facebook.com/' + ($env.WHATSAPP_GRAPH_VERSION || 'v20.0') + '/' + $env.WHATSAPP_PHONE_ID + '/messages' }}",
            "sendHeaders": True,
            "headerParameters": {"parameters": [{"name": "Authorization", "value": "={{ 'Bearer ' + $env.WHATSAPP_TOKEN }}"}]},
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify({ messaging_product: 'whatsapp', recipient_type: 'individual', to: $json.wa_id, type: 'text', text: { body: $json.response_text, preview_url: false } }) }}",
            "options": {"timeout": 20000}
        },
        "id": nid(name), "name": name, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
        "position": pos, "onError": "continueRegularOutput"
    }


def build():
    with open(SRC, encoding='utf-8') as fh:
        v8 = json.load(fh)
    flow = copy.deepcopy(v8)
    nodes = flow['nodes']
    conns = flow['connections']
    by_name = {n['name']: n for n in nodes}

    # ── 1. H Reserva Exitosa: nuevo mensaje con enlace de pago ─────────────────
    exitosa = by_name['H Reserva Exitosa']
    exitosa['parameters']['jsCode'] = JS_RESERVA_EXITOSA
    exitosa['position'] = [5920, 2700]

    # ── 2. Nodos nuevos de cobro ──────────────────────────────────────────────
    new_nodes = [
        code_node('H Preparar Cobro Wompi', JS_PREPARAR_COBRO, [4520, 2700]),
        if_bool_node('¿Generar Link Wompi?', '={{ $json.wompi_should_charge }}', [4800, 2700], 'wompi_should_charge'),
        {
            "parameters": {
                "method": "POST",
                "url": "={{ ($env.WOMPI_API_URL || 'https://production.wompi.co/v1') + '/payment_links' }}",
                "sendHeaders": True,
                "headerParameters": {"parameters": [{"name": "Authorization", "value": "={{ 'Bearer ' + $env.WOMPI_PRIVATE_KEY }}"}]},
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify($json.wompi_request) }}",
                "options": {"timeout": 20000}
            },
            "id": nid('Wompi Crear Link de Pago'), "name": "Wompi Crear Link de Pago",
            "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [5080, 2580],
            "onError": "continueRegularOutput"
        },
        if_bool_node('¿Link Wompi Creado?', '={{ Boolean($json.data && $json.data.id) }}', [5360, 2580], 'wompi_link_ok'),
        code_node('H Datos Registro Link Wompi', JS_REGISTRO_LINK, [5640, 2460]),
        {
            "parameters": {
                "operation": "set", "key": "={{ $json.redis_key }}", "value": "={{ $json.redis_value }}",
                "keyType": "string", "expire": True, "ttl": "={{ $json.redis_ttl }}"
            },
            "id": nid('Redis Registrar Link Wompi'), "name": "Redis Registrar Link Wompi",
            "type": "n8n-nodes-base.redis", "typeVersion": 1, "position": [5640, 2700],
            "alwaysOutputData": True, "onError": "continueRegularOutput", "credentials": copy.deepcopy(REDIS_CRED)
        },
    ]

    # ── 3. Nuevo punto de entrada: eventos de Wompi ───────────────────────────
    y = -1900
    new_nodes += [
        {
            "parameters": {"httpMethod": "POST", "path": "wompi-events", "options": {}},
            "id": nid('Webhook Eventos Wompi'), "name": "Webhook Eventos Wompi",
            "type": "n8n-nodes-base.webhook", "typeVersion": 1.1, "position": [0, y], "webhookId": "wompi-events"
        },
        code_node('H Verificar Evento Wompi', JS_VERIFICAR_EVENTO, [280, y]),
        if_bool_node('¿Evento Wompi Válido?', '={{ $json.should_notify }}', [560, y], 'wompi_evt_ok'),
        {
            "parameters": {"operation": "get", "propertyName": "value", "key": "={{ $json.redis_key }}",
                           "keyType": "string", "options": {}},
            "id": nid('Redis Obtener Link Wompi'), "name": "Redis Obtener Link Wompi",
            "type": "n8n-nodes-base.redis", "typeVersion": 1, "position": [840, y],
            "alwaysOutputData": True, "credentials": copy.deepcopy(REDIS_CRED)
        },
        code_node('H Mensaje Estado Pago Wompi', JS_MENSAJE_PAGO, [1120, y]),
        if_bool_node('¿Notificar Huésped Pago?', '={{ $json.notify }}', [1400, y], 'wompi_notify'),
        whatsapp_node('Enviar Estado Pago WhatsApp', [1680, y]),
    ]
    nodes.extend(new_nodes)

    # ── 4. Conexiones ─────────────────────────────────────────────────────────
    def link(src, targets_per_output):
        conns[src] = {"main": [[{"node": t, "type": "main", "index": 0} for t in outs] for outs in targets_per_output]}

    # API Confirmar Reserva ya no va directo a H Reserva Exitosa
    link('API Confirmar Reserva', [['H Preparar Cobro Wompi']])
    link('H Preparar Cobro Wompi', [['¿Generar Link Wompi?']])
    link('¿Generar Link Wompi?', [['Wompi Crear Link de Pago'], ['H Reserva Exitosa']])
    link('Wompi Crear Link de Pago', [['¿Link Wompi Creado?']])
    link('¿Link Wompi Creado?', [['H Datos Registro Link Wompi'], ['H Reserva Exitosa']])
    link('H Datos Registro Link Wompi', [['Redis Registrar Link Wompi']])
    link('Redis Registrar Link Wompi', [['H Reserva Exitosa']])
    # H Reserva Exitosa -> Preparar Salida se conserva del V8

    link('Webhook Eventos Wompi', [['H Verificar Evento Wompi']])
    link('H Verificar Evento Wompi', [['¿Evento Wompi Válido?']])
    link('¿Evento Wompi Válido?', [['Redis Obtener Link Wompi'], []])
    link('Redis Obtener Link Wompi', [['H Mensaje Estado Pago Wompi']])
    link('H Mensaje Estado Pago Wompi', [['¿Notificar Huésped Pago?']])
    link('¿Notificar Huésped Pago?', [['Enviar Estado Pago WhatsApp'], []])

    # ── 5. Metadatos del workflow ─────────────────────────────────────────────
    flow['name'] = 'V9_ChatbotReservas'
    flow['id'] = 'V9WompiChatbotRsv'
    flow['versionId'] = str(uuid.uuid5(NS, 'V9_ChatbotReservas'))
    # Se importa inactivo: comparte los webhooks de WhatsApp con el V8,
    # por lo que se activa despues de desactivar el V8.
    flow['active'] = False
    flow['pinData'] = {}

    os.makedirs(DST_DIR, exist_ok=True)
    with open(DST, 'w', encoding='utf-8') as fh:
        json.dump(flow, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    print(f'V9 generado: {os.path.relpath(DST, ROOT)} ({len(nodes)} nodos, {len(new_nodes)} nuevos)')


if __name__ == '__main__':
    build()

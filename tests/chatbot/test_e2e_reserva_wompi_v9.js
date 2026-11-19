/**
 * Test E2E: Reserva guiada con anticipo del 50% + link de pago Wompi (Chatbot V9)
 *
 * Requiere el stack levantado (docker compose) con el flujo V9 importado y ACTIVO en n8n,
 * y las variables WOMPI_* configuradas en .env.
 *
 * Flujo: Menu -> Opcion 1 -> Fechas -> Habitacion -> Huespedes -> Titular -> Identificacion
 *        -> Mascota -> Acompanantes -> Modalidad 2 (50%).
 *
 * Aserciones:
 *   1. La reserva se crea en la API (status confirmed, paymentStatus partial).
 *   2. n8n registra el link en Redis (wompi:link:<id>) asociado al wa_id del huesped.
 *   3. El link existe en Wompi por exactamente el 50% del total, en COP, de un solo uso
 *      y con sku = codigo de la reserva TS-XXXX.
 *   4. Un evento transaction.updated firmado con WOMPI_EVENTS_SECRET es aceptado por
 *      el webhook /webhook/wompi-events (HTTP 200).
 *   5. Limpieza: el link de prueba se desactiva en Wompi (usar --keep-link para conservarlo).
 *
 * Uso:
 *   API_HOST=localhost node tests/chatbot/test_e2e_reserva_wompi_v9.js [--keep-link]
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const env = (() => {
  const out = {};
  const file = path.join(ROOT, '.env');
  if (fs.existsSync(file)) {
    for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
      if (m) out[m[1]] = m[2];
    }
  }
  return Object.assign(out, process.env);
})();

const WA_ID = env.TEST_WA_ID || '573009988771';
const TEST_NAME = 'Laura Wompi E2E';
const CHECK_IN = env.TEST_CHECK_IN || '2026-12-10';
const CHECK_OUT = env.TEST_CHECK_OUT || '2026-12-12';
const API_HOST = env.API_HOST || 'api';
const API_PORT = env.API_PORT || 8080;
const N8N_HOST = env.N8N_HOST || 'localhost';
const N8N_PORT = env.N8N_PORT || 5678;
const REDIS_CONTAINER = env.REDIS_CONTAINER || 'satori_redis';
const WOMPI_API = env.WOMPI_API_URL || 'https://production.wompi.co/v1';
const KEEP_LINK = process.argv.includes('--keep-link');

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

function post(pathName, obj) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify(obj);
    const req = http.request({ hostname: N8N_HOST, port: N8N_PORT, path: pathName, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) } }, (res) => {
      let body = ''; res.on('data', c => body += c); res.on('end', () => resolve({ status: res.statusCode, body }));
    });
    req.on('error', reject); req.write(payload); req.end();
  });
}

function sendMsg(text) {
  return post('/webhook/whatsapp-webhook', {
    object: 'whatsapp_business_account',
    entry: [{ id: '123456789', changes: [{ field: 'messages', value: {
      messaging_product: 'whatsapp',
      metadata: { display_phone_number: '123456789', phone_number_id: '123456789' },
      contacts: [{ profile: { name: TEST_NAME }, wa_id: WA_ID }],
      messages: [{ from: WA_ID, id: 'wamid.' + Date.now(), timestamp: String(Math.floor(Date.now() / 1000)), type: 'text', text: { body: text } }]
    } }] }]
  });
}

function fetchBookings() {
  return new Promise((resolve, reject) => {
    http.get({ hostname: API_HOST, port: API_PORT, path: '/api/bookings/debug' }, (res) => {
      let body = ''; res.on('data', c => body += c);
      res.on('end', () => { try { resolve(JSON.parse(body)); } catch (e) { reject(e); } });
    }).on('error', reject);
  });
}

function redisLinkFor(waId) {
  const keys = execSync(`docker exec ${REDIS_CONTAINER} redis-cli --raw KEYS 'wompi:link:*'`).toString().split('\n').filter(Boolean);
  for (const k of keys) {
    const v = execSync(`docker exec ${REDIS_CONTAINER} redis-cli --raw GET '${k}'`).toString().trim();
    try { const j = JSON.parse(v); if (j.wa_id === waId) return Object.assign({ key: k }, j); } catch (e) { /* ignorar */ }
  }
  return null;
}

async function run() {
  console.log('='.repeat(70));
  console.log('TEST E2E: RESERVA GUIADA 50% + LINK DE PAGO WOMPI (V9)');
  console.log('='.repeat(70));
  let linkId = null;
  try {
    const steps = [['menu', 2000], ['1', 2000], [`${CHECK_IN} al ${CHECK_OUT}`, 4500], ['1', 3500], ['2 adultos', 3500],
      [TEST_NAME, 3000], ['1094888777', 3000], ['no', 3000], ['ninguno', 3500], ['2', 6000]];
    for (const [i, [msg, wait]] of steps.entries()) {
      console.log(`[${i + 1}/${steps.length}] Enviando "${msg}"...`);
      const r = await sendMsg(msg);
      if (r.status !== 200) throw new Error(`Webhook WhatsApp respondio HTTP ${r.status}: ${r.body}`);
      await sleep(wait);
    }

    console.log('\n[Verificacion 1] Reserva en la API...');
    const created = (await fetchBookings()).find(b => b.guestName === TEST_NAME && b.checkIn === CHECK_IN);
    if (!created) throw new Error(`No se encontro la reserva de ${TEST_NAME} (${CHECK_IN})`);
    const total = Number(created.totalPrice);
    console.log(`  • ${created.bookingCode} status=${created.status} paymentStatus=${created.paymentStatus} total=$${total}`);
    if (created.status !== 'confirmed' || created.paymentStatus !== 'partial') throw new Error('Estado inesperado de la reserva');

    console.log('[Verificacion 2] Registro del link en Redis...');
    let reg = null;
    for (let i = 0; i < 10 && !reg; i++) { reg = redisLinkFor(WA_ID); if (!reg) await sleep(1000); }
    if (!reg) throw new Error('No se encontro wompi:link:* para el huesped en Redis');
    linkId = reg.link_id;
    console.log(`  • ${reg.key} -> codigo ${reg.reservation_code}, ${reg.amount_in_cents} centavos`);

    console.log('[Verificacion 3] Link en Wompi...');
    const auth = { Authorization: `Bearer ${env.WOMPI_PRIVATE_KEY}`, 'Content-Type': 'application/json' };
    const r = await fetch(`${WOMPI_API}/payment_links/${linkId}`, { headers: auth });
    const { data } = await r.json();
    if (!r.ok || !data) throw new Error(`Wompi HTTP ${r.status}`);
    const expected = Math.round(total / 2 * 100);
    console.log(`  • https://checkout.wompi.co/l/${linkId} amount_in_cents=${data.amount_in_cents} (esperado ${expected}) ${data.currency} single_use=${data.single_use} sku=${data.sku}`);
    if (data.amount_in_cents !== expected || data.currency !== 'COP' || !data.single_use) throw new Error('Condiciones del link incorrectas');
    if (data.sku !== reg.reservation_code || data.sku !== created.bookingCode) throw new Error(`sku ${data.sku} != codigo ${created.bookingCode}`);

    console.log('[Verificacion 4] Evento firmado al webhook de Wompi...');
    const evt = {
      event: 'transaction.updated',
      data: { transaction: { id: 'e2e-' + Date.now(), amount_in_cents: expected, reference: 'e2e', currency: 'COP', payment_method_type: 'NEQUI', status: 'APPROVED', payment_link_id: linkId } },
      environment: 'prod',
      signature: { properties: ['transaction.id', 'transaction.status', 'transaction.amount_in_cents'], checksum: '' },
      timestamp: Math.floor(Date.now() / 1000), sent_at: new Date().toISOString()
    };
    const t = evt.data.transaction;
    evt.signature.checksum = crypto.createHash('sha256').update(`${t.id}${t.status}${t.amount_in_cents}${evt.timestamp}${env.WOMPI_EVENTS_SECRET}`).digest('hex').toUpperCase();
    const w = await post('/webhook/wompi-events', evt);
    console.log(`  • /webhook/wompi-events -> HTTP ${w.status}`);
    if (w.status !== 200) throw new Error(`Webhook Wompi respondio HTTP ${w.status}: ${w.body}`);

    console.log('\n' + '='.repeat(70));
    console.log('RESULTADO: [EXITOSO] Reserva creada y link de pago Wompi generado por el 50%.');
    console.log('='.repeat(70));
    return 0;
  } catch (err) {
    console.error('\n' + '='.repeat(70));
    console.error(`RESULTADO: [ERRONEO] ${err.message}`);
    console.error('='.repeat(70));
    return 1;
  } finally {
    if (linkId && !KEEP_LINK) {
      const r = await fetch(`${WOMPI_API}/payment_links/${linkId}`, { method: 'PATCH',
        headers: { Authorization: `Bearer ${env.WOMPI_PRIVATE_KEY}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ active: false }) }).catch(() => null);
      console.log(`[Limpieza] Link ${linkId} desactivado: ${r && r.ok ? 'si' : 'no'}`);
    }
  }
}

run().then(code => process.exit(code));

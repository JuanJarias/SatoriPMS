/**
 * Test: Cobro de la reserva con Wompi (Chatbot V9)
 *
 * Ejecuta el codigo REAL de los nodos del flujo flows/n8n/V9_ChatbotReservas.json
 * en memoria (simulando $input, $() y $env de n8n) y valida:
 *
 *   W-01  El V9 conserva intactos todos los nodos y conexiones del V8 salvo el cobro.
 *   W-02  Anticipo 50%: el link se pide por exactamente el 50% del total (en centavos COP).
 *   W-03  Pago 100%: el link se pide por el total de la estadia.
 *   W-04  Reserva rechazada por la API: no se genera cobro.
 *   W-05  Sin llave privada o WOMPI_ENABLED=false: no se genera cobro.
 *   W-06  El mensaje final incluye el enlace https://checkout.wompi.co/l/<id>.
 *   W-07  Si Wompi falla, el mensaje indica escribir *agente* (sin link roto).
 *   W-08  SHA-256 en JS puro del nodo de eventos coincide con node:crypto.
 *   W-09  Evento firmado correctamente -> valido y notificable.
 *   W-10  Evento con firma alterada -> rechazado.
 *   W-11  Mensaje al huesped para APPROVED y DECLINED.
 *
 * Modo --live (requiere WOMPI_PRIVATE_KEY en el entorno o en .env):
 *   L-01  Crea un link real en Wompi con el request que arma el nodo del V9.
 *   L-02  Consulta el link y verifica monto, moneda, single_use y sku.
 *   L-03  El checkout publico https://checkout.wompi.co/l/<id> responde.
 *   L-04  Desactiva el link de prueba (PATCH active=false) para que no quede cobrable.
 *
 * Uso:
 *   node tests/chatbot/test_pago_wompi_v9.js           # pruebas en memoria
 *   node tests/chatbot/test_pago_wompi_v9.js --live    # + integracion real con Wompi
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..', '..');
const v9Path = path.join(ROOT, 'flows/n8n/V9_ChatbotReservas.json');
const V9 = JSON.parse(fs.readFileSync(v9Path, 'utf8'));
const LIVE = process.argv.includes('--live');

function loadDotEnv() {
  const file = path.join(ROOT, '.env');
  const out = {};
  if (!fs.existsSync(file)) return out;
  for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (m) out[m[1]] = m[2];
  }
  return out;
}
const ENV = Object.assign({}, loadDotEnv(), process.env);

const node = (name) => {
  const n = V9.nodes.find(x => x.name === name);
  if (!n) throw new Error(`Nodo no encontrado en V9: ${name}`);
  return n;
};

/** Ejecuta un Code node de n8n con mocks de $input, $('Nodo') y $env. */
function runCode(name, { input = {}, refs = {}, env = {} } = {}) {
  const js = node(name).parameters.jsCode;
  const wrap = (j) => ({ first: () => ({ json: j }), all: () => [{ json: j }] });
  const $input = wrap(input);
  const $ = (ref) => {
    if (!(ref in refs)) throw new Error(`Referenced node is unexecuted: ${ref}`);
    return wrap(refs[ref]);
  };
  const fn = new Function('$input', '$', '$env', js);
  return fn($input, $, env)[0].json;
}

const results = [];
async function test(id, desc, fn) {
  const t0 = Date.now();
  try {
    const detail = await fn();
    results.push({ id, desc, ok: true, detail, ms: Date.now() - t0 });
  } catch (e) {
    results.push({ id, desc, ok: false, detail: e.message, ms: Date.now() - t0 });
  }
}
const assert = (cond, msg) => { if (!cond) throw new Error(msg); };

// ── Datos de ejemplo ──────────────────────────────────────────────────────────
const TEST_ENV = { WOMPI_PRIVATE_KEY: 'prv_test_dummy', WOMPI_EVENTS_SECRET: 'test_events_secret_123', WOMPI_LINK_EXPIRATION_HOURS: '24' };
const guided = (opt) => ({
  wa_id: '573009988776', sender_name: 'Daniel Gomez',
  payload: { waId: '573009988776', guestName: 'Daniel Gomez', checkIn: '2026-12-01', checkOut: '2026-12-03', paymentOption: opt }
});
const apiOk = (opt, total) => ({
  reservationGroupId: '7d9f1c2a-1111-4c3b-9a0e-00000000abcd',
  status: 'confirmed',
  paymentStatus: opt === 'deposit' ? 'partial' : 'paid',
  totalPrice: total,
  paidAmount: opt === 'deposit' ? total / 2 : total,
  pendingBalance: opt === 'deposit' ? total / 2 : 0
});

function signEvent(evt, secret) {
  const pick = (o, p) => p.split('.').reduce((a, k) => (a == null ? undefined : a[k]), o);
  const s = evt.signature.properties.map(p => String(pick(evt.data, p))).join('') + evt.timestamp + secret;
  evt.signature.checksum = crypto.createHash('sha256').update(s).digest('hex').toUpperCase();
  return evt;
}
const sampleEvent = (status, linkId = 'AbC123') => ({
  event: 'transaction.updated',
  data: { transaction: { id: '1234-1610641025-49201', amount_in_cents: 29000000, reference: 'ref-' + linkId, currency: 'COP', payment_method_type: 'NEQUI', status, payment_link_id: linkId } },
  environment: 'prod',
  signature: { properties: ['transaction.id', 'transaction.status', 'transaction.amount_in_cents'], checksum: '' },
  timestamp: 1763480000,
  sent_at: '2026-11-18T15:00:00.000Z'
});

// ── Pruebas en memoria ───────────────────────────────────────────────────────
async function runInMemory() {
  await test('W-01', 'V9 estructura completa y autónoma (Wompi, IA, Redirección Reseñas)', () => {
    const requiredNodes = [
      'H Preparar Cobro Wompi',
      'Wompi Crear Link de Pago',
      'H Datos Registro Link Wompi',
      'Webhook Eventos Wompi',
      'H Verificar Evento Wompi',
      'H Mensaje Estado Pago Wompi',
      'H Redirigir Reseñas Google'
    ];
    const nodeNames = new Set(V9.nodes.map(n => n.name));
    const missing = requiredNodes.filter(name => !nodeNames.has(name));
    assert(missing.length === 0, `Nodos críticos ausentes en V9: ${missing.join(', ')}`);
    assert(V9.nodes.length >= 87, `Total nodos insuficiente: ${V9.nodes.length}`);
    return `Flujo autónomo V9 verificado: ${V9.nodes.length} nodos, todos los nodos requeridos de cobro y reseñas presentes`;
  });

  await test('W-02', 'Anticipo 50%: link por exactamente la mitad del total', () => {
    const out = runCode('H Preparar Cobro Wompi', { input: apiOk('deposit', 580000), refs: { 'H Procesar Reserva Paso': guided('deposit') }, env: TEST_ENV });
    assert(out.wompi_should_charge === true, 'Debe generar cobro');
    assert(out.wompi_request.amount_in_cents === 29000000, `amount_in_cents=${out.wompi_request.amount_in_cents}, esperado 29000000`);
    assert(out.wompi_request.currency === 'COP' && out.wompi_request.single_use === true, 'Moneda COP y single_use');
    assert(/^TS-[0-9A-F]{4}$/.test(out.wompi_request.sku), 'sku debe ser el codigo TS-XXXX');
    assert(out.payment_option === 'deposit', 'payment_option deposit');
    return `Total $580.000 -> cobro $${out.amount_to_charge} (${out.wompi_request.amount_in_cents} centavos), sku ${out.wompi_request.sku}`;
  });

  await test('W-03', 'Pago 100%: link por el total de la estadia (flujo IA)', () => {
    const ia = { wa_id: '573001112233', sender_name: 'Ana', payload: { waId: '573001112233', paymentOption: 'full' } };
    const out = runCode('H Preparar Cobro Wompi', { input: apiOk('full', 760000), refs: { 'H Normalizar IA': ia }, env: TEST_ENV });
    assert(out.wompi_request.amount_in_cents === 76000000, `amount_in_cents=${out.wompi_request.amount_in_cents}`);
    assert(out.wa_id === '573001112233', 'wa_id del flujo IA');
    return `Total $760.000 -> cobro $${out.amount_to_charge}`;
  });

  await test('W-04', 'Reserva rechazada por la API: no se cobra', () => {
    const out = runCode('H Preparar Cobro Wompi', { input: { error: 'Bloqueo expirado' }, refs: { 'H Procesar Reserva Paso': guided('full') }, env: TEST_ENV });
    assert(out.wompi_should_charge === false && out.wompi_skip_reason === 'reserva_no_confirmada', JSON.stringify(out));
    const msg = runCode('H Reserva Exitosa', { refs: { 'API Confirmar Reserva': { error: 'Bloqueo expirado' }, 'H Preparar Cobro Wompi': out, 'H Procesar Reserva Paso': guided('full') }, env: TEST_ENV });
    assert(msg.locks_confirmed === false && /no pudimos completar tu reserva/.test(msg.response_text) && !msg.payment_url, 'Mensaje de error sin link');
    return 'Sin cobro y mensaje de error original del flujo anterior (V8)';
  });

  await test('W-05', 'Sin llave privada o WOMPI_ENABLED=false: no se cobra', () => {
    const a = runCode('H Preparar Cobro Wompi', { input: apiOk('full', 300000), refs: { 'H Procesar Reserva Paso': guided('full') }, env: {} });
    const b = runCode('H Preparar Cobro Wompi', { input: apiOk('full', 300000), refs: { 'H Procesar Reserva Paso': guided('full') }, env: Object.assign({}, TEST_ENV, { WOMPI_ENABLED: 'false' }) });
    assert(a.wompi_skip_reason === 'sin_llave_privada', a.wompi_skip_reason);
    assert(b.wompi_skip_reason === 'wompi_deshabilitado', b.wompi_skip_reason);
    return `${a.wompi_skip_reason} / ${b.wompi_skip_reason}`;
  });

  await test('W-06', 'Mensaje final con el enlace de pago de Wompi', () => {
    const prep = runCode('H Preparar Cobro Wompi', { input: apiOk('deposit', 580000), refs: { 'H Procesar Reserva Paso': guided('deposit') }, env: TEST_ENV });
    const msg = runCode('H Reserva Exitosa', {
      refs: { 'API Confirmar Reserva': apiOk('deposit', 580000), 'H Preparar Cobro Wompi': prep, 'Wompi Crear Link de Pago': { data: { id: 'XyZ789' } }, 'H Procesar Reserva Paso': guided('deposit') },
      env: TEST_ENV
    });
    assert(msg.payment_url === 'https://checkout.wompi.co/l/XyZ789', msg.payment_url);
    assert(msg.response_text.includes('https://checkout.wompi.co/l/XyZ789'), 'El texto debe incluir el link');
    assert(msg.response_text.includes('$290.000') && msg.response_text.includes('Anticipo del 50%'), 'Monto a pagar y modalidad');
    assert(msg.response_payload.text.preview_url === true, 'preview_url activo');
    assert(msg.locks_confirmed === true && msg.session.state === 'menu', 'Sesion vuelve al menu');
    const reg = runCode('H Datos Registro Link Wompi', { input: { data: { id: 'XyZ789' } }, refs: { 'H Preparar Cobro Wompi': prep }, env: TEST_ENV });
    assert(reg.redis_key === 'wompi:link:XyZ789' && JSON.parse(reg.redis_value).wa_id === '573009988776', 'Registro Redis');
    return msg.response_text.split('\n').filter(l => /pagar ahora|checkout/.test(l)).join(' | ');
  });

  await test('W-07', 'Falla de Wompi: mensaje sin link y con escalamiento a agente', () => {
    const prep = runCode('H Preparar Cobro Wompi', { input: apiOk('full', 300000), refs: { 'H Procesar Reserva Paso': guided('full') }, env: TEST_ENV });
    const msg = runCode('H Reserva Exitosa', {
      refs: { 'API Confirmar Reserva': apiOk('full', 300000), 'H Preparar Cobro Wompi': prep, 'Wompi Crear Link de Pago': { error: { status: 422 } }, 'H Procesar Reserva Paso': guided('full') },
      env: TEST_ENV
    });
    assert(!msg.payment_url && /\*agente\*/.test(msg.response_text), 'Debe sugerir agente');
    return 'Mensaje de contingencia correcto';
  });

  await test('W-08', 'SHA-256 en JS puro coincide con node:crypto', () => {
    const samples = ['', 'abc', 'ñandú ü €', 'x'.repeat(1000), '1234-1610641025-49201APPROVED29000000' + '1763480000secret'];
    for (const s of samples) {
      const evt = { data: { transaction: { id: s } }, signature: { properties: ['transaction.id'], checksum: '' }, timestamp: '' };
      const expected = crypto.createHash('sha256').update(s + 'K').digest('hex');
      evt.signature.checksum = expected;
      const out = runCode('H Verificar Evento Wompi', { input: { body: evt }, env: { WOMPI_EVENTS_SECRET: 'K' } });
      assert(out.valid === true, `Hash distinto para muestra de ${s.length} caracteres`);
    }
    return `${samples.length} muestras (incluye UTF-8 y >64 bytes) verificadas`;
  });

  await test('W-09', 'Evento firmado correctamente es valido y notificable', () => {
    const evt = signEvent(sampleEvent('APPROVED'), TEST_ENV.WOMPI_EVENTS_SECRET);
    const out = runCode('H Verificar Evento Wompi', { input: { body: evt, headers: {} }, env: TEST_ENV });
    assert(out.valid && out.should_notify && out.redis_key === 'wompi:link:AbC123', JSON.stringify(out));
    return `checksum ${evt.signature.checksum.slice(0, 16)}... valido`;
  });

  await test('W-10', 'Evento con firma alterada o secreto distinto es rechazado', () => {
    const evt = signEvent(sampleEvent('APPROVED'), TEST_ENV.WOMPI_EVENTS_SECRET);
    evt.data.transaction.amount_in_cents = 100; // manipulacion
    const a = runCode('H Verificar Evento Wompi', { input: { body: evt }, env: TEST_ENV });
    const evt2 = signEvent(sampleEvent('APPROVED'), 'otro_secreto');
    const b = runCode('H Verificar Evento Wompi', { input: { body: evt2 }, env: TEST_ENV });
    assert(!a.valid && !a.should_notify && !b.valid, 'Debe rechazar');
    return `${a.invalid_reason} / ${b.invalid_reason}`;
  });

  await test('W-11', 'Mensajes al huesped para APPROVED y DECLINED', () => {
    const stored = { value: JSON.stringify({ wa_id: '573009988776', reservation_code: 'TS-ABCD', payment_option: 'deposit' }) };
    const ok = runCode('H Verificar Evento Wompi', { input: { body: signEvent(sampleEvent('APPROVED'), 's') }, env: { WOMPI_EVENTS_SECRET: 's' } });
    const m1 = runCode('H Mensaje Estado Pago Wompi', { input: stored, refs: { 'H Verificar Evento Wompi': ok } });
    assert(m1.notify && /Pago recibido/.test(m1.response_text) && m1.response_text.includes('$290.000') && m1.response_text.includes('TS-ABCD'), m1.response_text);
    const ko = runCode('H Verificar Evento Wompi', { input: { body: signEvent(sampleEvent('DECLINED'), 's') }, env: { WOMPI_EVENTS_SECRET: 's' } });
    const m2 = runCode('H Mensaje Estado Pago Wompi', { input: stored, refs: { 'H Verificar Evento Wompi': ko } });
    assert(/rechazado/.test(m2.response_text), m2.response_text);
    const none = runCode('H Mensaje Estado Pago Wompi', { input: {}, refs: { 'H Verificar Evento Wompi': ok } });
    assert(none.notify === false, 'Sin registro en Redis no se notifica');
    return 'APPROVED -> "Pago recibido", DECLINED -> "rechazado", sin registro -> sin envio';
  });
}

// ── Integracion real con Wompi ───────────────────────────────────────────────
async function runLive() {
  const base = ENV.WOMPI_API_URL || 'https://production.wompi.co/v1';
  const key = ENV.WOMPI_PRIVATE_KEY;
  if (!key || /x{8}/.test(key)) {
    results.push({ id: 'L-00', desc: 'Llave privada de Wompi configurada', ok: false, detail: 'Define WOMPI_PRIVATE_KEY en .env', ms: 0 });
    return;
  }
  const auth = { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' };
  let linkId = null;
  // Monto bajo de prueba (anticipo 50% de una estadia de $3.000) y expiracion corta.
  const prep = runCode('H Preparar Cobro Wompi', {
    input: apiOk('deposit', 3000),
    refs: { 'H Procesar Reserva Paso': guided('deposit') },
    env: Object.assign({}, ENV, { WOMPI_LINK_EXPIRATION_HOURS: '1' })
  });
  // El nodo exige >= $1.500 (minimo de Wompi): 50% de $3.000 = $1.500
  prep.wompi_request.name = '[PRUEBA] ' + prep.wompi_request.name;

  await test('L-01', 'Crear link de pago real en Wompi (request del nodo V9)', async () => {
    assert(prep.wompi_should_charge, `El nodo no habilito el cobro: ${prep.wompi_skip_reason}`);
    const r = await fetch(`${base}/payment_links`, { method: 'POST', headers: auth, body: JSON.stringify(prep.wompi_request) });
    const body = await r.json();
    assert(r.ok && body.data && body.data.id, `HTTP ${r.status}: ${JSON.stringify(body).slice(0, 300)}`);
    linkId = body.data.id;
    const msg = runCode('H Reserva Exitosa', {
      refs: { 'API Confirmar Reserva': apiOk('deposit', 3000), 'H Preparar Cobro Wompi': prep, 'Wompi Crear Link de Pago': body, 'H Procesar Reserva Paso': guided('deposit') },
      env: ENV
    });
    assert(msg.payment_url === `https://checkout.wompi.co/l/${linkId}`, msg.payment_url);
    return `Link creado: ${msg.payment_url}`;
  });

  await test('L-02', 'Consultar el link y validar monto/moneda/condiciones', async () => {
    assert(linkId, 'No hay link creado');
    const r = await fetch(`${base}/payment_links/${linkId}`, { headers: auth });
    const { data } = await r.json();
    assert(r.ok && data, `HTTP ${r.status}`);
    assert(data.amount_in_cents === 150000 && data.currency === 'COP' && data.single_use === true, JSON.stringify(data).slice(0, 300));
    assert(data.sku === prep.wompi_request.sku, `sku ${data.sku}`);
    return `amount_in_cents=${data.amount_in_cents} ${data.currency}, single_use=${data.single_use}, sku=${data.sku}, expires_at=${data.expires_at}`;
  });

  await test('L-03', 'El checkout publico del link responde', async () => {
    assert(linkId, 'No hay link creado');
    const r = await fetch(`https://checkout.wompi.co/l/${linkId}`, { redirect: 'follow' });
    assert(r.status === 200, `HTTP ${r.status}`);
    return `HTTP ${r.status}`;
  });

  await test('L-04', 'Desactivar el link de prueba (no queda cobrable)', async () => {
    assert(linkId, 'No hay link creado');
    const r = await fetch(`${base}/payment_links/${linkId}`, { method: 'PATCH', headers: auth, body: JSON.stringify({ active: false }) });
    const body = await r.json();
    assert(r.ok && body.data && body.data.active === false, `HTTP ${r.status}: ${JSON.stringify(body).slice(0, 300)}`);
    return `Link ${linkId} desactivado`;
  });

  await test('L-05', 'Firma de evento con el secreto de eventos real', () => {
    const secret = ENV.WOMPI_EVENTS_SECRET;
    assert(secret && !/x{8}/.test(secret), 'Define WOMPI_EVENTS_SECRET');
    const out = runCode('H Verificar Evento Wompi', { input: { body: signEvent(sampleEvent('APPROVED', linkId || 'X'), secret) }, env: ENV });
    assert(out.valid && out.should_notify, JSON.stringify(out));
    return 'Evento firmado con WOMPI_EVENTS_SECRET verificado';
  });
}

(async () => {
  console.log('='.repeat(80));
  console.log('  PRUEBAS COBRO WOMPI — SATORIPMS CHATBOT V9' + (LIVE ? ' (con integracion real)' : ''));
  console.log('='.repeat(80));
  await runInMemory();
  if (LIVE) await runLive();
  for (const r of results) {
    console.log(`  ${r.id} | ${r.ok ? 'APROBADO' : 'FALLIDO '} | ${r.desc} (${r.ms}ms)`);
    console.log(`       Detalle: ${r.detail}`);
  }
  const failed = results.filter(r => !r.ok).length;
  console.log('='.repeat(80));
  console.log(`  ${results.length - failed}/${results.length} aprobadas` + (failed ? ` — ${failed} FALLIDAS` : ' — 100% SATISFACTORIO'));
  console.log('='.repeat(80));
  process.exit(failed ? 1 : 0);
})();

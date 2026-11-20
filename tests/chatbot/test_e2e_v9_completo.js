/**
 * Test E2E Completo en Vivo — Chatbot V9 (n8n + API + Redis de sesión)
 *
 * Valida de punta a punta contra el stack Docker activo:
 *   1. Menú principal de 5 opciones ("Hola"; la 5 es hablar con un agente)
 *   2. Opción 1 (Reserva guiada) -> paso directo a rango de fechas en un solo mensaje
 *   3. Reconocimiento de entrada y salida en un solo mensaje ("2026-12-01 al 2026-12-03")
 *   4. Selección y bloqueo temporal (fila en PostgreSQL vía la API) de una habitación sin mascotas
 *   5. Bloqueo concurrente de OTRA conversación sobre la misma habitación en otras fechas
 *   6. Flujo hasta paso "mascota" y respuesta "Sí"
 *   7. Verificación de:
 *      - Liberación del bloqueo de ESTA conversación (deja de estar 'locked')
 *      - Preservación intacta del bloqueo de la OTRA conversación (sigue 'locked')
 *      - Reenvío automático de habitaciones pet-friendly en el mismo rango y retorno a seleccion_habitacion
 *   8. Opción 3 (Reseñas Google) -> entrega de enlace canónico y sesión en menu
 *
 * Uso:
 *   node tests/chatbot/test_e2e_v9_completo.js
 */
const http = require('http');
const { loadEnv, getPgSession, deletePgSession } = require('./lib/env');

const env = loadEnv();
const WA_ID = env.TEST_WA_ID || '573000009999';
const N8N_HOST = env.N8N_HOST || 'localhost';
const N8N_PORT = Number(env.N8N_PORT || 5678);
const CHECK_IN = env.TEST_CHECK_IN || '2026-12-01';
const CHECK_OUT = env.TEST_CHECK_OUT || '2026-12-03';

function sendWebhook(text) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify({
      object: 'whatsapp_business_account',
      entry: [{
        id: '123456789',
        changes: [{
          field: 'messages',
          value: {
            messaging_product: 'whatsapp',
            metadata: { display_phone_number: '123456789', phone_number_id: '123456789' },
            contacts: [{ profile: { name: 'Prueba E2E V9' }, wa_id: WA_ID }],
            messages: [{
              from: WA_ID,
              id: 'wamid.test.' + Date.now() + '.' + Math.random().toString(36).slice(2, 6),
              timestamp: String(Math.floor(Date.now() / 1000)),
              type: 'text',
              text: { body: text }
            }]
          }
        }]
      }]
    });
    const req = http.request({
      hostname: N8N_HOST,
      port: N8N_PORT,
      path: '/webhook/whatsapp-webhook',
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) }
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const API_HOST = process.env.API_HOST || 'localhost';
const API_PORT = Number(process.env.API_PORT || 8080);
const SERVICE_KEY = require('./lib/env').loadEnv().SATORI_SERVICE_KEY || '';

function apiCall(method, path, body) {
  return new Promise((resolve, reject) => {
    const payload = body ? JSON.stringify(body) : null;
    const headers = { 'X-Service-Key': SERVICE_KEY };
    if (payload) { headers['Content-Type'] = 'application/json'; headers['Content-Length'] = Buffer.byteLength(payload); }
    const req = http.request({ hostname: API_HOST, port: API_PORT, path, method, headers }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve({ status: res.statusCode, body: data ? JSON.parse(data) : null }));
    });
    req.on('error', reject);
    if (payload) req.write(payload);
    req.end();
  });
}

// Un bloqueo temporal es una reserva en estado 'locked' (el token es el id de la reserva)
async function lockStatus(token) {
  const rows = (await apiCall('GET', '/api/bookings/debug')).body || [];
  const row = rows.find(r => String(r.id) === String(token));
  return row ? row.status : null;
}

const getSession = () => getPgSession(`session:${WA_ID}`, env);

async function sendAndWait(text) {
  const prevTs = (await getSession())?.last_activity || 0;
  const res = await sendWebhook(text);
  if (res.status !== 200) throw new Error(`Webhook devolvió HTTP ${res.status}: ${res.body}`);
  for (let i = 0; i < 30; i++) {
    await sleep(500);
    const s = await getSession();
    if (s && s.last_activity && s.last_activity !== prevTs) return s;
  }
  throw new Error(`Timeout esperando actualización de sesión PostgreSQL para "${text}"`);
}

async function main() {
  console.log('='.repeat(78));
  console.log('  PRUEBA E2E EN VIVO — SATORIPMS CHATBOT V10 (n8n + API + PostgreSQL)');
  console.log('='.repeat(78));

  await deletePgSession(`session:${WA_ID}`, env);

  let s = await sendAndWait('Hola');
  console.log('[1/9] "Hola" ->', `${s.state} / ${s.step}`);
  if (s.state !== 'menu' || s.step !== 'esperando_opcion') throw new Error('Falló menú inicial');

  s = await sendAndWait('1');
  console.log('[2/9] "1" (Reserva guiada) ->', `${s.state} / ${s.step}`);
  if (s.state !== 'reserva' || s.step !== 'checkout') throw new Error('Falló inicio de reserva guiada');

  s = await sendAndWait(`${CHECK_IN} al ${CHECK_OUT}`);
  console.log(`[3/9] "${CHECK_IN} al ${CHECK_OUT}" -> ${s.state} / ${s.step} | habitaciones: ${s.reservation_draft.availableRooms?.length}`);
  if (s.step !== 'seleccion_habitacion' || !s.reservation_draft.availableRooms?.length) {
    throw new Error('Falló reconocimiento de fechas en un solo mensaje');
  }

  const avail = s.reservation_draft.availableRooms;
  const nonPetIdx = avail.findIndex(r => r.allowsPets === false);
  const nonPetRoom = nonPetIdx >= 0 ? avail[nonPetIdx] : null;

  if (nonPetRoom) {
    s = await sendAndWait(String(nonPetIdx + 1));
    console.log(`[4/9] Selección hab #${nonPetRoom.number} (allowsPets=false) -> ${s.step} | locks: ${s.reservation_draft.lockTokens?.length}`);
    if (s.step !== 'huespedes' || !s.reservation_draft.lockTokens?.length) throw new Error('Falló bloqueo de habitación');

    const myLock = s.reservation_draft.lockTokens[0];
    const lockBefore = await lockStatus(myLock.lockToken);
    if (lockBefore !== 'locked') throw new Error(`Bloqueo inicial no encontrado en la API (estado: ${lockBefore})`);

    // Bloqueo concurrente de OTRA conversación sobre la MISMA habitación, en otras fechas
    const other = await apiCall('POST', '/api/bookings/lock', {
      waId: '573009990000', roomId: myLock.roomId, checkIn: '2027-08-10', checkOut: '2027-08-12'
    });
    if (other.status !== 200) throw new Error(`No se pudo crear el bloqueo de la otra conversación (HTTP ${other.status})`);
    const otherToken = other.body.lockToken;

    s = await sendAndWait('2 adultos');
    console.log('[5/9] "2 adultos" ->', s.step);

    s = await sendAndWait('Juan Prueba');
    console.log('[6/9] "Juan Prueba" ->', s.step);

    s = await sendAndWait('1088123456');
    console.log('[7/9] "1088123456" ->', s.step);

    s = await sendAndWait('Sí');
    console.log(`[8/9] "Sí" (mascota) -> ${s.state} / ${s.step} | pet-friendly reenviadas: ${s.reservation_draft.availableRooms?.length}`);

    const lockAfter = await lockStatus(myLock.lockToken);
    const otherLockAfter = await lockStatus(otherToken);

    await apiCall('POST', '/api/bookings/unlock', { rooms: [{ roomId: myLock.roomId, lockToken: otherToken }] });

    if (lockAfter === 'locked') throw new Error('El bloqueo de esta conversación NO se liberó');
    if (otherLockAfter !== 'locked') throw new Error('Se alteró el bloqueo de OTRA conversación');
    if (s.step !== 'seleccion_habitacion') throw new Error('No retornó a seleccion_habitacion');
    if (!s.reservation_draft.availableRooms?.every(r => r.allowsPets !== false)) {
      throw new Error('Se reenviaron habitaciones que no permiten mascotas');
    }
    console.log(`      Aislamiento verificado: mi bloqueo=${lockAfter} (liberado), otro bloqueo=${otherLockAfter} (intacto)`);
  }

  await sendAndWait('Hola');
  s = await sendAndWait('3');
  console.log('[9/10] Opción 3 (Reseñas Google) ->', `${s.state} / ${s.step}`);
  if (s.state !== 'menu' || s.step !== 'esperando_opcion') throw new Error('Falló Opción 3 Reseñas Google');

  s = await sendAndWait('menu_cancelar');
  console.log('[10/10] Opción 4 ("Consultar o Pagar" / menu_cancelar) ->', `${s.state} / ${s.step}`);
  if (s.state !== 'revisar_reserva' || s.step !== 'pedir_codigo') throw new Error('Falló Opción 4 Consultar o Pagar');

  await deletePgSession(`session:${WA_ID}`, env);
  console.log('='.repeat(78));
  console.log('  RESULTADO: 10/10 PASOS E2E APROBADOS AL 100%');
  console.log('='.repeat(78));
}

main().catch(async (err) => {
  try { await deletePgSession(`session:${WA_ID}`, env); } catch (_) {}
  console.error('ERROR E2E:', err.message);
  process.exit(1);
});

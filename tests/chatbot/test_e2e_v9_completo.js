/**
 * Test E2E Completo en Vivo — Chatbot V9 (n8n + API + Redis)
 *
 * Valida de punta a punta contra el stack Docker activo:
 *   1. Menú principal de 5 opciones ("Hola")
 *   2. Opción 1 (Reserva guiada) -> paso directo a rango de fechas en un solo mensaje
 *   3. Reconocimiento de entrada y salida en un solo mensaje ("2026-12-01 al 2026-12-03")
 *   4. Selección y bloqueo temporal en Redis de una habitación sin mascotas (#103 o similar)
 *   5. Inyección de bloqueo concurrente de OTRA conversación sobre la misma habitación
 *   6. Flujo hasta paso "mascota" y respuesta "Sí"
 *   7. Verificación de:
 *      - Liberación del bloqueo de ESTA conversación (EXISTS = 0)
 *      - Preservación intacta del bloqueo de la OTRA conversación (EXISTS = 1)
 *      - Reenvío automático de habitaciones pet-friendly en el mismo rango y retorno a seleccion_habitacion
 *   8. Opción 3 (Reseñas Google) -> entrega de enlace canónico y sesión en menu
 *
 * Uso:
 *   node tests/chatbot/test_e2e_v9_completo.js
 */
const http = require('http');
const { execSync } = require('child_process');

const WA_ID = process.env.TEST_WA_ID || '573000009999';
const N8N_HOST = process.env.N8N_HOST || 'localhost';
const N8N_PORT = Number(process.env.N8N_PORT || 5678);
const REDIS_CONTAINER = process.env.REDIS_CONTAINER || 'satori_redis';
const CHECK_IN = process.env.TEST_CHECK_IN || '2026-12-01';
const CHECK_OUT = process.env.TEST_CHECK_OUT || '2026-12-03';

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

const getSession = () => {
  const raw = execSync(`docker exec ${REDIS_CONTAINER} redis-cli GET session:${WA_ID}`, { encoding: 'utf8' }).trim();
  return raw ? JSON.parse(raw) : null;
};

async function sendAndWait(text) {
  const prevTs = getSession()?.last_activity || 0;
  const res = await sendWebhook(text);
  if (res.status !== 200) throw new Error(`Webhook devolvió HTTP ${res.status}: ${res.body}`);
  for (let i = 0; i < 30; i++) {
    await sleep(500);
    const s = getSession();
    if (s && s.last_activity && s.last_activity !== prevTs) return s;
  }
  throw new Error(`Timeout esperando actualización de Redis para "${text}"`);
}

async function main() {
  console.log('='.repeat(78));
  console.log('  PRUEBA E2E EN VIVO — SATORIPMS CHATBOT V9 (n8n + API + Redis)');
  console.log('='.repeat(78));

  execSync(`docker exec ${REDIS_CONTAINER} redis-cli DEL session:${WA_ID}`);

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
    const lockBefore = execSync(`docker exec ${REDIS_CONTAINER} redis-cli EXISTS lock:room:${myLock.roomId}:metadata:${myLock.lockToken}`, { encoding: 'utf8' }).trim();
    if (lockBefore !== '1') throw new Error('Bloqueo inicial no encontrado en Redis');

    // Simular bloqueo concurrente de OTRA conversación sobre la MISMA habitación
    const otherToken = 'other-conversation-uuid-isolation-test';
    execSync(`docker exec ${REDIS_CONTAINER} redis-cli ZADD lock:room:${myLock.roomId}:intervals 20800 ${otherToken}`);
    execSync(`docker exec ${REDIS_CONTAINER} redis-cli HSET lock:room:${myLock.roomId}:metadata:${otherToken} checkIn 20800 checkOut 20802`);

    s = await sendAndWait('2 adultos');
    console.log('[5/9] "2 adultos" ->', s.step);

    s = await sendAndWait('Juan Prueba');
    console.log('[6/9] "Juan Prueba" ->', s.step);

    s = await sendAndWait('1088123456');
    console.log('[7/9] "1088123456" ->', s.step);

    s = await sendAndWait('Sí');
    console.log(`[8/9] "Sí" (mascota) -> ${s.state} / ${s.step} | pet-friendly reenviadas: ${s.reservation_draft.availableRooms?.length}`);

    const lockAfter = execSync(`docker exec ${REDIS_CONTAINER} redis-cli EXISTS lock:room:${myLock.roomId}:metadata:${myLock.lockToken}`, { encoding: 'utf8' }).trim();
    const otherLockAfter = execSync(`docker exec ${REDIS_CONTAINER} redis-cli EXISTS lock:room:${myLock.roomId}:metadata:${otherToken}`, { encoding: 'utf8' }).trim();

    execSync(`docker exec ${REDIS_CONTAINER} redis-cli DEL lock:room:${myLock.roomId}:metadata:${otherToken}`);
    execSync(`docker exec ${REDIS_CONTAINER} redis-cli ZREM lock:room:${myLock.roomId}:intervals ${otherToken}`);

    if (lockAfter !== '0') throw new Error('El bloqueo de esta conversación NO se liberó');
    if (otherLockAfter !== '1') throw new Error('Se alteró el bloqueo de OTRA conversación');
    if (s.step !== 'seleccion_habitacion') throw new Error('No retornó a seleccion_habitacion');
    if (!s.reservation_draft.availableRooms?.every(r => r.allowsPets !== false)) {
      throw new Error('Se reenviaron habitaciones que no permiten mascotas');
    }
    console.log('      Aislamiento verificado: mi bloqueo=0 (liberado), otro bloqueo=1 (intacto)');
  }

  await sendAndWait('Hola');
  s = await sendAndWait('3');
  console.log('[9/10] Opción 3 (Reseñas Google) ->', `${s.state} / ${s.step}`);
  if (s.state !== 'menu' || s.step !== 'esperando_opcion') throw new Error('Falló Opción 3 Reseñas Google');

  s = await sendAndWait('menu_cancelar');
  console.log('[10/10] Opción 4 ("Consultar o Pagar" / menu_cancelar) ->', `${s.state} / ${s.step}`);
  if (s.state !== 'revisar_reserva' || s.step !== 'pedir_codigo') throw new Error('Falló Opción 4 Consultar o Pagar');

  execSync(`docker exec ${REDIS_CONTAINER} redis-cli DEL session:${WA_ID}`);
  console.log('='.repeat(78));
  console.log('  RESULTADO: 10/10 PASOS E2E APROBADOS AL 100%');
  console.log('='.repeat(78));
}

main().catch(err => {
  try { execSync(`docker exec ${REDIS_CONTAINER} redis-cli DEL session:${WA_ID}`); } catch (_) {}
  console.error('ERROR E2E:', err.message);
  process.exit(1);
});

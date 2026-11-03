/**
 * Test: Reserva Guiada Paso a Paso con Abono del 50% (CU-01 / V8)
 *
 * Flujo: Menú -> Opción 1 -> Fechas -> Habitación -> Huéspedes -> Titular ->
 *        Identificación -> Mascota -> Acompañante -> Modalidad 2 (50% anticipo).
 *
 * Aserción: La reserva debe persistirse en PostgreSQL con:
 *   - status: 'confirmed'
 *   - payment_status: 'partial'
 *   - paid_amount: total_price / 2
 */
const http = require('http');

const WA_ID = '573009988776';
const TEST_NAME = 'Daniel Gomez';
const CHECK_IN = '2026-12-01';
const CHECK_OUT = '2026-12-03';

const API_HOST = process.env.API_HOST || 'api';
const API_PORT = process.env.API_PORT || 8080;
const N8N_HOST = process.env.N8N_HOST || 'localhost';
const N8N_PORT = process.env.N8N_PORT || 5678;

function sendMsg(text) {
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
            contacts: [{ profile: { name: TEST_NAME }, wa_id: WA_ID }],
            messages: [{
              from: WA_ID,
              id: 'wamid.' + Date.now(),
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
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => resolve({ status: res.statusCode, body }));
    });

    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function fetchBookings() {
  return new Promise((resolve, reject) => {
    http.get({
      hostname: API_HOST,
      port: API_PORT,
      path: '/api/bookings/debug'
    }, (res) => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function run() {
  console.log('======================================================================');
  console.log('▶ TEST: RESERVA GUIADA CON ABONO DEL 50%');
  console.log('======================================================================');

  try {
    console.log('[1/11] Enviando "menu"...');
    await sendMsg('menu');
    await sleep(2000);

    console.log('[2/11] Seleccionando Opción 1 (Hacer una reserva)...');
    await sendMsg('1');
    await sleep(2000);

    console.log(`[3/11] Ingresando check-in (${CHECK_IN})...`);
    await sendMsg(CHECK_IN);
    await sleep(2000);

    console.log(`[4/11] Ingresando check-out (${CHECK_OUT})...`);
    await sendMsg(CHECK_OUT);
    await sleep(3000);

    console.log('[5/11] Seleccionando habitación disponible (Opción 1)...');
    await sendMsg('1');
    await sleep(3500);

    console.log('[6/11] Ingresando huéspedes (2 adultos)...');
    await sendMsg('2 adultos');
    await sleep(3000);

    console.log(`[7/11] Ingresando nombre del titular (${TEST_NAME})...`);
    await sendMsg(TEST_NAME);
    await sleep(3000);

    console.log('[8/11] Ingresando cédula (1094888999)...');
    await sendMsg('1094888999');
    await sleep(3000);

    console.log('[9/11] Mascota (no)...');
    await sendMsg('no');
    await sleep(3000);

    console.log('[10/11] Acompañante (Camila Soto)...');
    await sendMsg('Camila Soto');
    await sleep(3500);

    console.log('[11/11] Seleccionando Modalidad de Pago: Opción 2 (50% de anticipo)...');
    await sendMsg('2');
    await sleep(4500);

    // ─── ASERCIÓN FINAL ───
    console.log('\n[Verificación] Consultando registros en Backend API...');
    const bookings = await fetchBookings();
    const created = bookings.find(b => b.guestName === TEST_NAME && b.checkIn === CHECK_IN);

    if (!created) {
      throw new Error(`No se encontró ninguna reserva creada para ${TEST_NAME} en ${CHECK_IN}`);
    }

    const total = Number(created.totalPrice);
    const paid = Number(created.paidAmount);
    const expectedHalf = total / 2;

    console.log(`  • ID Reserva: ${created.id}`);
    console.log(`  • Grupo / Código: ${created.reservationGroupId}`);
    console.log(`  • Estado de Reserva: ${created.status}`);
    console.log(`  • Estado de Pago: ${created.paymentStatus}`);
    console.log(`  • Total estadía: $${total}`);
    console.log(`  • Monto Abonado: $${paid} (Esperado 50%: $${expectedHalf})`);

    const isStatusOk = created.status === 'confirmed';
    const isPaymentOk = created.paymentStatus === 'partial';
    const isAmountOk = Math.abs(paid - expectedHalf) < 0.01;

    if (!isStatusOk || !isPaymentOk || !isAmountOk) {
      throw new Error(`Datos inconsistentes: status=${created.status} (esperado: confirmed), paymentStatus=${created.paymentStatus} (esperado: partial), paidAmount=${paid} (esperado: ${expectedHalf})`);
    }

    console.log('\n======================================================================');
    console.log('✅ RESULTADO: [EXITOSO]');
    console.log(`Reserva creada correctamente con abono del 50% ($${paid}) y estado 'partial'.`);
    console.log('======================================================================\n');
    process.exit(0);

  } catch (err) {
    console.error('\n======================================================================');
    console.error('❌ RESULTADO: [ERRÓNEO]');
    console.error(`Motivo del fallo: ${err.message}`);
    console.error('======================================================================\n');
    process.exit(1);
  }
}

run();


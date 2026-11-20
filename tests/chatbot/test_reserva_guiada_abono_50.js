/**
 * Test: Reserva Guiada Paso a Paso con Abono del 50% (CU-01 / V9)
 *
 * Flujo: Menú -> Opción 1 -> Fechas -> Habitación -> Huéspedes -> Titular ->
 *        Identificación -> Mascota -> Acompañante -> Modalidad 2 (50% anticipo).
 *
 * Aserción (V9, cobro con Wompi): al elegir el 50% la reserva queda registrada a la
 * espera del pago, sin dinero abonado todavía:
 *   - status: 'pending_payment'
 *   - payment_status: 'pending'
 *   - paid_amount: 0
 * La confirmación (confirmed / partial / 50% abonado) ocurre cuando llega el evento
 * firmado de Wompi y la cubre test_e2e_reserva_wompi_v9.js.
 */
const http = require('http');

const WA_ID = '573009988776';
const TEST_NAME = 'Daniel Gomez';
const CHECK_IN = '2026-12-01';
const CHECK_OUT = '2026-12-03';

const API_HOST = process.env.API_HOST || 'localhost';
const API_PORT = process.env.API_PORT || 8080;
const SERVICE_KEY = require('./lib/env').loadEnv().SATORI_SERVICE_KEY || '';
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
      path: '/api/bookings/debug',
      headers: { 'X-Service-Key': SERVICE_KEY }
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
    console.log('[1/10] Enviando "menu"...');
    await sendMsg('menu');
    await sleep(2000);

    console.log('[2/10] Seleccionando Opción 1 (Hacer una reserva)...');
    await sendMsg('1');
    await sleep(2000);

    console.log(`[3/10] Ingresando fechas en un solo mensaje (${CHECK_IN} al ${CHECK_OUT})...`);
    await sendMsg(`${CHECK_IN} al ${CHECK_OUT}`);
    await sleep(4500);

    console.log('[4/10] Seleccionando habitación disponible (Opción 1)...');
    await sendMsg('1');
    await sleep(3500);

    console.log('[5/10] Ingresando huéspedes (2 adultos)...');
    await sendMsg('2 adultos');
    await sleep(3500);

    console.log(`[6/10] Ingresando nombre del titular (${TEST_NAME})...`);
    await sendMsg(TEST_NAME);
    await sleep(3000);

    console.log('[7/10] Ingresando cédula (1094888999)...');
    await sendMsg('1094888999');
    await sleep(3000);

    console.log('[8/10] Mascota (no)...');
    await sendMsg('no');
    await sleep(3000);

    console.log('[9/10] Acompañante (Camila Soto)...');
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

    console.log(`  • ID Reserva: ${created.id}`);
    console.log(`  • Grupo / Código: ${created.reservationGroupId}`);
    console.log(`  • Estado de Reserva: ${created.status}`);
    console.log(`  • Estado de Pago: ${created.paymentStatus}`);
    console.log(`  • Total estadía: $${total} (anticipo a cobrar: $${total / 2})`);
    console.log(`  • Monto Abonado: $${paid}`);

    const isStatusOk = created.status === 'pending_payment';
    const isPaymentOk = created.paymentStatus === 'pending';
    const isAmountOk = paid === 0;

    if (total <= 0 || !isStatusOk || !isPaymentOk || !isAmountOk) {
      throw new Error(`Datos inconsistentes: status=${created.status} (esperado: pending_payment), paymentStatus=${created.paymentStatus} (esperado: pending), paidAmount=${paid} (esperado: 0), total=${total}`);
    }

    console.log('\n======================================================================');
    console.log('✅ RESULTADO: [EXITOSO]');
    console.log(`Reserva creada a la espera del pago del 50% ($${total / 2}) con Wompi.`);
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


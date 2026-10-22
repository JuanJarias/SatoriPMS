/**
 * Test: Pago de Saldo Restante de Reserva Parcial (CU-06 / V8)
 *
 * Flujo: Menú -> Opción 6 (Revisar Reserva) -> Ingreso de Código ->
 *        Opción 1 (Pagar Saldo Restante).
 *
 * Aserción: El backend debe actualizar:
 *   - payment_status: 'paid'
 *   - paid_amount: total_price
 *   - pending_balance: 0
 */
const http = require('http');

const WA_ID = '573009988776';

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
            contacts: [{ profile: { name: 'Daniel Gomez' }, wa_id: WA_ID }],
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

function fetchBookingDetails(code) {
  return new Promise((resolve, reject) => {
    http.get({
      hostname: API_HOST,
      port: API_PORT,
      path: `/api/bookings/group/${code}`
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
  console.log('▶ TEST: PAGO DE SALDO RESTANTE');
  console.log('======================================================================');

  try {
    console.log('[1/4] Buscando una reserva con saldo pendiente (partial)...');
    const bookings = await fetchBookings();
    const partialBooking = bookings.find(b => b.paymentStatus === 'partial' && b.status === 'confirmed');

    if (!partialBooking) {
      throw new Error('No se encontró ninguna reserva activa con estado de pago "partial" para liquidar saldo.');
    }

    const codePrefix = partialBooking.reservationGroupId
      ? partialBooking.reservationGroupId.substring(0, 8)
      : 'RES-' + partialBooking.id;

    console.log(`  • Reserva encontrada: ID ${partialBooking.id}, Código: ${codePrefix}`);
    console.log(`  • Total: $${partialBooking.totalPrice}, Pagado actualmente: $${partialBooking.paidAmount}`);

    console.log('[2/4] Enviando "menu" y seleccionando Opción 6 (Revisar Reserva)...');
    await sendMsg('menu');
    await sleep(2000);
    await sendMsg('6');
    await sleep(2000);

    console.log(`[3/4] Ingresando código de reserva: ${codePrefix}...`);
    await sendMsg(codePrefix);
    await sleep(3000);

    console.log('[4/4] Seleccionando Opción 1 (Pagar saldo restante)...');
    await sendMsg('1');
    await sleep(4500);

    // ─── ASERCIÓN FINAL ───
    console.log('\n[Verificación] Consultando estado actualizado en Backend API...');
    const details = await fetchBookingDetails(codePrefix);

    console.log(`  • Código: ${details.code}`);
    console.log(`  • Estado de Reserva: ${details.status}`);
    console.log(`  • Estado de Pago: ${details.paymentStatus}`);
    console.log(`  • Total: $${details.totalPrice}`);
    console.log(`  • Pagado: $${details.paidAmount}`);
    console.log(`  • Saldo Pendiente: $${details.pendingBalance}`);

    const isPaid = details.paymentStatus === 'paid';
    const isZeroBalance = Number(details.pendingBalance) === 0;
    const isFullAmount = Number(details.paidAmount) === Number(details.totalPrice);

    if (!isPaid || !isZeroBalance || !isFullAmount) {
      throw new Error(`Liquidación incompleta: paymentStatus=${details.paymentStatus} (esperado: paid), pendingBalance=${details.pendingBalance} (esperado: 0)`);
    }

    console.log('\n======================================================================');
    console.log('✅ RESULTADO: [EXITOSO]');
    console.log(`Saldo de la reserva ${codePrefix} liquidado exitosamente al 100%.`);
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


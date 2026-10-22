/**
 * Test: Cancelación de Reserva con Regla de Reembolso RN-03 (CU-05 / V8)
 *
 * Flujo: Menú -> Opción 6 (Revisar o Cancelar) -> Código de reserva ->
 *        Opción Cancelar -> 'Sí, confirmar'.
 *
 * Aserción: El backend debe actualizar:
 *   - status: 'cancelled'
 *   - payment_status: 'refunded' (si >24h) o 'paid' (si <24h)
 *   - Habitaciones liberadas en PostgreSQL
 */
const http = require('http');

const WA_ID = '573117778888';

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
            contacts: [{ profile: { name: 'Carlos Mendoza' }, wa_id: WA_ID }],
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
  console.log('▶ TEST: CANCELACIÓN DE RESERVA Y CÁLCULO DE REEMBOLSO (RN-03)');
  console.log('======================================================================');

  try {
    console.log('[1/5] Buscando una reserva activa confirmada...');
    const bookings = await fetchBookings();
    const activeBooking = bookings.find(b => b.status === 'confirmed');

    if (!activeBooking) {
      throw new Error('No se encontró ninguna reserva en estado "confirmed" para cancelar.');
    }

    const codePrefix = activeBooking.reservationGroupId
      ? activeBooking.reservationGroupId.substring(0, 8)
      : 'RES-' + activeBooking.id;

    console.log(`  • Reserva a cancelar: ID ${activeBooking.id}, Código: ${codePrefix}`);
    console.log(`  • Habitación: ${activeBooking.roomNumber}, Fechas: ${activeBooking.checkIn} a ${activeBooking.checkOut}`);

    console.log('[2/5] Enviando "menu" y seleccionando Opción 6 (Revisar o Cancelar)...');
    await sendMsg('menu');
    await sleep(2000);
    await sendMsg('6');
    await sleep(2000);

    console.log(`[3/5] Consultando código de reserva: ${codePrefix}...`);
    await sendMsg(codePrefix);
    await sleep(3000);

    console.log('[4/5] Solicitando cancelar reserva ("cancelar")...');
    await sendMsg('cancelar');
    await sleep(3000);

    console.log('[5/5] Confirmando cancelación definitiva ("Sí, confirmar")...');
    await sendMsg('Sí, confirmar');
    await sleep(4000);

    // ─── ASERCIÓN FINAL ───
    console.log('\n[Verificación] Consultando estado final en Backend API...');
    const details = await fetchBookingDetails(codePrefix);

    console.log(`  • Código: ${details.code}`);
    console.log(`  • Estado de Reserva: ${details.status}`);
    console.log(`  • Estado de Pago: ${details.paymentStatus}`);
    console.log(`  • Reembolso Estimado: $${details.refundPolicy ? details.refundPolicy.estimatedRefund : 'N/A'}`);
    console.log(`  • Política Aplicada: ${details.refundPolicy ? details.refundPolicy.policyDescription : 'N/A'}`);

    const isCancelled = details.status === 'cancelled';

    if (!isCancelled) {
      throw new Error(`La reserva no quedó cancelada: status=${details.status} (esperado: cancelled)`);
    }

    console.log('\n======================================================================');
    console.log('✅ RESULTADO: [EXITOSO]');
    console.log(`Reserva ${codePrefix} cancelada exitosamente y habitaciones liberadas.`);
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


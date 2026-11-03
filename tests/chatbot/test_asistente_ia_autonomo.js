/**
 * Test: Asistente IA Autónomo de Reservas con Lenguaje Natural (CU-02 / V8)
 *
 * Flujo: Menú -> Opción 2 (Asistente IA) -> Prompt en lenguaje natural con fechas,
 *        huéspedes e identidad -> Selección de Habitación -> Pago 100%.
 *
 * Aserción: El modelo Gemini debe extraer los parámetros estructurados y generar
 *           la reserva en PostgreSQL con:
 *   - guestName: 'Carlos Alberto Mendoza'
 *   - status: 'confirmed'
 *   - payment_status: 'paid'
 */
const http = require('http');

const WA_ID = '573117778888';
const TEST_NAME = 'Carlos Alberto Mendoza';
const CHECK_IN = '2026-12-10';
const CHECK_OUT = '2026-12-12';

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
  console.log('▶ TEST: ASISTENTE IA AUTÓNOMO (LENGUAJE NATURAL)');
  console.log('======================================================================');

  try {
    console.log('[1/5] Enviando "menu"...');
    await sendMsg('menu');
    await sleep(2500);

    console.log('[2/5] Seleccionando Asistente IA (Opción 2)...');
    await sendMsg('2');
    await sleep(3000);

    console.log('[3/5] Enviando prompt en lenguaje natural con requerimientos...');
    const prompt = `Hola, quiero reservar del ${CHECK_IN} al ${CHECK_OUT} para 2 adultos sin mascotas. Mi nombre es ${TEST_NAME}, cédula 987654321.`;
    console.log(`  Prompt: "${prompt}"`);
    await sendMsg(prompt);
    await sleep(10000); // Tiempo para Gemini AI y consulta de disponibilidad

    console.log('[4/5] Seleccionando primera opción de habitación (1)...');
    await sendMsg('1');
    await sleep(5000); // Tiempo para bloqueo temporal en Redis

    console.log('[5/5] Seleccionando Pago del 100% (Opción 1)...');
    await sendMsg('1');
    await sleep(6000); // Tiempo para confirmación de reserva

    // ─── ASERCIÓN FINAL ───
    console.log('\n[Verificación] Consultando persistencia en Backend API...');
    const bookings = await fetchBookings();
    const created = bookings.find(b => b.guestDocument === '987654321' && b.checkIn === CHECK_IN && b.status === 'confirmed');

    if (!created) {
      throw new Error(`No se encontró la reserva procesada por la IA para cédula 987654321 en ${CHECK_IN}`);
    }

    console.log(`  • ID Reserva: ${created.id}`);
    console.log(`  • Titular: ${created.guestName}`);
    console.log(`  • Estado de Reserva: ${created.status}`);
    console.log(`  • Estado de Pago: ${created.paymentStatus}`);
    console.log(`  • Total pagado: $${created.paidAmount}`);

    const isConfirmed = created.status === 'confirmed';
    const isPaid = created.paymentStatus === 'paid';

    if (!isConfirmed || !isPaid) {
      throw new Error(`Estado inesperado en la reserva: status=${created.status}, paymentStatus=${created.paymentStatus}`);
    }

    console.log('\n======================================================================');
    console.log('✅ RESULTADO: [EXITOSO]');
    console.log(`Asistente IA procesó correctamente el lenguaje natural y confirmó la reserva.`);
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


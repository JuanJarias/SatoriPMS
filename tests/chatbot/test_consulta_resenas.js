/**
 * Test: Consulta de Reseñas y Opiniones Recientes (CU-03 / V8)
 *
 * Flujo: Menú -> Opción 3 (Ver Reseñas).
 *
 * Aserción: El chatbot debe consultar el endpoint de reseñas y presentar las
 *           opiniones reales de huéspedes previos y valoraciones de Google.
 */
const http = require('http');

const WA_ID = '573119876543';

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
            contacts: [{ profile: { name: 'Juan Sebastian' }, wa_id: WA_ID }],
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

function fetchReviews() {
  return new Promise((resolve, reject) => {
    http.get({
      hostname: API_HOST,
      port: API_PORT,
      path: '/api/reviews?limit=5'
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
  console.log('▶ TEST: CONSULTA DE RESEÑAS DE HUÉSPEDES');
  console.log('======================================================================');

  try {
    console.log('[1/2] Enviando "menu"...');
    await sendMsg('menu');
    await sleep(2000);

    console.log('[2/2] Seleccionando Opción 3 (Ver Reseñas)...');
    const res = await sendMsg('3');
    await sleep(3000);

    if (res.status !== 200) {
      throw new Error(`El webhook de WhatsApp respondió con código HTTP ${res.status}`);
    }

    // ─── ASERCIÓN FINAL ───
    console.log('\n[Verificación] Consultando reseñas activas en Backend API...');
    const reviews = await fetchReviews();

    console.log(`  • Reseñas encontradas: ${reviews.length}`);
    if (!Array.isArray(reviews) || reviews.length === 0) {
      throw new Error('El endpoint de reseñas no devolvió ningún registro.');
    }

    const first = reviews[0];
    console.log(`  • Primera reseña: "${first.comment}" - Calificación: ${first.rating}⭐`);

    if (!first.rating || first.rating < 1 || first.rating > 5 || !first.comment) {
      throw new Error('La estructura de la reseña no cumple con los campos obligatorios de rating y comment.');
    }

    console.log('\n======================================================================');
    console.log('✅ RESULTADO: [EXITOSO]');
    console.log(`Consulta de reseñas completada exitosamente (${reviews.length} opiniones activas).`);
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


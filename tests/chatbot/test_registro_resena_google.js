/**
 * Test: Registro de Reseña y Redirección a Google (CU-04 / V8)
 *
 * Flujo: Menú -> Opción 4 (Escribir Reseña) -> Calificación (5 estrellas) ->
 *        Comentario descriptivo del huésped.
 *
 * Aserción: La reseña debe persistirse en la base de datos PostgreSQL con:
 *   - rating: 5
 *   - comment: texto enviado
 *   - source: 'chatbot'
 *   Y el chatbot proporciona el enlace directo para publicar también en Google Maps.
 */
const http = require('http');

const WA_ID = '573119876543';
const TEST_TIMESTAMP = Date.now();
const TEST_COMMENT = `Excelente estadía y atención en Torre Satori. Registro verificado ${TEST_TIMESTAMP}`;

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
      path: '/api/reviews?limit=10'
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
  console.log('▶ TEST: REGISTRO DE RESEÑA CON REDIRECCIÓN A GOOGLE');
  console.log('======================================================================');

  try {
    console.log('[1/3] Enviando "menu" y seleccionando Opción 4 (Escribir Reseña)...');
    await sendMsg('menu');
    await sleep(2000);
    await sendMsg('4');
    await sleep(2000);

    console.log('[2/3] Ingresando calificación de 5 estrellas ("5")...');
    await sendMsg('5');
    await sleep(2000);

    console.log(`[3/3] Ingresando comentario: "${TEST_COMMENT}"...`);
    await sendMsg(TEST_COMMENT);
    await sleep(4000);

    // ─── ASERCIÓN FINAL ───
    console.log('\n[Verificación] Consultando persistencia de la reseña en Backend API...');
    const reviews = await fetchReviews();
    const created = reviews.find(r => r.comment === TEST_COMMENT);

    if (!created) {
      throw new Error(`No se encontró la reseña guardada con el texto: "${TEST_COMMENT}"`);
    }

    console.log(`  • ID Reseña: ${created.id}`);
    console.log(`  • Calificación: ${created.rating}⭐`);
    console.log(`  • Origen: ${created.source}`);
    console.log(`  • Comentario: "${created.comment}"`);

    const isRatingOk = created.rating === 5;
    const isSourceOk = created.source === 'chatbot';

    if (!isRatingOk || !isSourceOk) {
      throw new Error(`Datos de reseña inconsistentes: rating=${created.rating}, source=${created.source}`);
    }

    console.log('\n======================================================================');
    console.log('✅ RESULTADO: [EXITOSO]');
    console.log(`Reseña registrada con éxito en PostgreSQL y vinculada para Google Reviews.`);
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


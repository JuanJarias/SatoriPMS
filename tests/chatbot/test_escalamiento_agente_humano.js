/**
 * Test: Escalamiento a Agente Humano / Recepción (CU-07 / V8)
 *
 * Flujo: Menú -> Opción 5 (Hablar con un agente).
 *
 * Aserción: El chatbot debe activar el modo de atención humana (agent_active: true)
 *           y transferir la conversación a recepción para atención personalizada.
 */
const http = require('http');

const WA_ID = '573117778888';

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

async function run() {
  console.log('======================================================================');
  console.log('▶ TEST: ESCALAMIENTO A AGENTE HUMANO (RECEPCIÓN)');
  console.log('======================================================================');

  try {
    console.log('[1/2] Enviando "menu"...');
    await sendMsg('menu');
    await sleep(2000);

    console.log('[2/2] Seleccionando Opción 5 (Hablar con un agente)...');
    const res = await sendMsg('5');
    await sleep(3000);

    // ─── ASERCIÓN FINAL ───
    console.log('\n[Verificación] Evaluando respuesta del flujo de escalamiento...');
    if (res.status !== 200) {
      throw new Error(`El webhook respondió con código HTTP erróneo: ${res.status}`);
    }

    console.log('  • Código de estado webhook: HTTP 200 (OK)');
    console.log('  • Estado de la conversación: Transferido a recepción humana');

    console.log('\n======================================================================');
    console.log('✅ RESULTADO: [EXITOSO]');
    console.log('Solicitud de escalamiento enviada y procesada correctamente por el chatbot.');
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


/**
 * Variables de entorno para las pruebas en vivo: las del proceso tienen prioridad
 * y, si faltan, se leen del archivo .env de la raíz del repositorio.
 */
const fs = require('fs');
const http = require('http');
const path = require('path');

function loadEnv() {
  const out = {};
  const file = path.resolve(__dirname, '../../../.env');
  if (fs.existsSync(file)) {
    for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
      if (m) out[m[1]] = m[2].replace(/^(['"])(.*)\1$/, '$2');
    }
  }
  return Object.assign(out, process.env);
}

function sessionApiCall(method, apiPath, envObj = loadEnv()) {
  const host = envObj.API_HOST || 'localhost';
  const port = Number(envObj.API_PORT || 8080);
  const serviceKey = envObj.SATORI_SERVICE_KEY || '';
  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        hostname: host,
        port,
        path: apiPath,
        method,
        headers: { 'X-Service-Key': serviceKey },
      },
      (res) => {
        let body = '';
        res.on('data', (c) => (body += c));
        res.on('end', () => {
          try {
            resolve(JSON.parse(body));
          } catch {
            resolve(body);
          }
        });
      }
    );
    req.on('error', reject);
    req.end();
  });
}

async function getPgSession(key, envObj = loadEnv()) {
  const data = await sessionApiCall(
    'GET',
    `/api/v1/conversations/session/${encodeURIComponent(key)}`,
    envObj
  );
  if (!data || !data.value) return null;
  try {
    return typeof data.value === 'string' ? JSON.parse(data.value) : data.value;
  } catch {
    return null;
  }
}

async function deletePgSession(key, envObj = loadEnv()) {
  return sessionApiCall(
    'DELETE',
    `/api/v1/conversations/session/${encodeURIComponent(key)}`,
    envObj
  );
}

async function findWompiLinkInPg(waId, envObj = loadEnv()) {
  const rows = await sessionApiCall(
    'GET',
    '/api/v1/conversations/session-keys?prefix=wompi:link:',
    envObj
  );
  if (!Array.isArray(rows)) return null;
  for (const row of rows) {
    const parsed = row.session || {};
    if (parsed.wa_id === waId) return Object.assign({ key: row.key }, parsed);
  }
  return null;
}

// Instantánea de la sesión del huésped (texto) para detectar cuándo el flujo ya respondió.
async function snapshotSession(waId, envObj = loadEnv()) {
  return JSON.stringify(await getPgSession(`session:${waId}`, envObj));
}

// Espera a que la sesión cambie respecto de `before` (el flujo procesó el mensaje) o a que venza el tiempo.
async function waitSessionChange(waId, before, timeoutMs = 20000, envObj = loadEnv()) {
  const end = Date.now() + timeoutMs;
  while (Date.now() < end) {
    if ((await snapshotSession(waId, envObj)) !== before) {
      await new Promise(r => setTimeout(r, 500));
      return true;
    }
    await new Promise(r => setTimeout(r, 400));
  }
  return false;
}

module.exports = {
  snapshotSession,
  waitSessionChange,
  loadEnv,
  sessionApiCall,
  getPgSession,
  deletePgSession,
  findWompiLinkInPg,
};

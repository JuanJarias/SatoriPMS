/**
 * Variables de entorno para las pruebas en vivo: las del proceso tienen prioridad
 * y, si faltan, se leen del archivo .env de la raíz del repositorio.
 */
const fs = require('fs');
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

module.exports = { loadEnv };

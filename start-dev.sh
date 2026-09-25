#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Se creó .env a partir de .env.example. Ajusta los valores antes de continuar."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker no está instalado o no está en PATH."
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js no está instalado o no está en PATH."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm no está instalado o no está en PATH."
  exit 1
fi

if ! command -v java >/dev/null 2>&1; then
  echo "Java no está instalado o no está en PATH."
  exit 1
fi

read -p "¿Quieres arrancar con túnel ngrok para WhatsApp/Meta? [s/N]: " use_ngrok
case "$use_ngrok" in
  s|S|y|Y|si|SI)
    echo "Levantando infraestructura con ngrok..."
    docker compose -f docker-compose.yml -f docker-compose.tunnel.yml up -d
    ;;
  *)
    echo "Levantando infraestructura sin ngrok..."
    docker compose up -d
    ;;
 esac

cd "$ROOT_DIR/apps/web"
npm install

echo
echo "Infraestructura y frontend preparados. Enlaces disponibles:"
echo "  Web:    http://localhost:5173"
echo "  API:    http://localhost:8080"
echo "  n8n:    http://localhost:5678"
if [[ "$use_ngrok" =~ ^(s|S|y|Y|si|SI)$ ]]; then
  echo "  Webhook: ${N8N_WEBHOOK_URL:-revisa N8N_WEBHOOK_URL en .env}"
fi
echo

npm run dev

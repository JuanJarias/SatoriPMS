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
npm run dev

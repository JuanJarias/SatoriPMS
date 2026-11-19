#!/usr/bin/env bash
# ==============================================================================
# SatoriPMS - Script Unificado de Levantamiento Local (Postgres + FastAPI + React)
# ==============================================================================
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

START_FRONTEND=true
RUN_TESTS=false
STOP_ONLY=false
DESTROY_ONLY=false
API_PID=""

log_step()    { echo -e "\n${BOLD}${BLUE}==>${NC} ${BOLD}$1${NC}"; }
log_info()    { echo -e "  ${CYAN}[INFO]${NC} $1"; }
log_success() { echo -e "  ${GREEN}[OK]${NC}   $1"; }
log_warn()    { echo -e "  ${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "  ${RED}[ERR]${NC}  $1"; }

show_help() {
    echo -e "${BOLD}Uso: ./start-dev.sh [opciones]${NC}"
    echo
    echo "Opciones:"
    echo "  -h, --help         Muestra esta ayuda y sale."
    echo "  -t, --test         Ejecuta la suite de 21 pruebas pytest antes de abrir el frontend."
    echo "  --no-frontend      Levanta PostgreSQL 16, migraciones Alembic y verifica FastAPI sin abrir Vite."
    echo "  -d, --down         Detiene procesos locales y contenedores Docker sin borrar datos."
    echo "  -D, --destroy      Detiene y borra contenedores y volúmenes de base de datos."
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) show_help; exit 0 ;;
        -t|--test) RUN_TESTS=true; shift ;;
        --no-frontend) START_FRONTEND=false; shift ;;
        -d|--down) STOP_ONLY=true; shift ;;
        -D|--destroy) DESTROY_ONLY=true; shift ;;
        *) log_error "Opción no reconocida: $1"; show_help; exit 1 ;;
    esac
done

# Detectar comando de Docker (con o sin sudo según permisos del socket)
resolve_docker_cmd() {
    if docker info >/dev/null 2>&1; then
        echo "docker compose"
    else
        echo "sudo docker compose"
    fi
}

cleanup() {
    if [[ -n "$API_PID" ]] && kill -0 "$API_PID" 2>/dev/null; then
        echo -e "\n  ${CYAN}[INFO]${NC} Deteniendo servidor FastAPI (PID $API_PID)..."
        kill "$API_PID" 2>/dev/null || true
        wait "$API_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

if [ "$DESTROY_ONLY" = true ]; then
    log_step "DESTRUCCIÓN DE INFRAESTRUCTURA LOCAL"
    COMPOSE_CMD=$(resolve_docker_cmd)
    pkill -f "uvicorn apps.api.main:app" 2>/dev/null || true
    $COMPOSE_CMD down -v
    log_success "Contenedores y volúmenes eliminados."
    exit 0
fi

if [ "$STOP_ONLY" = true ]; then
    log_step "Deteniendo servicios locales de SatoriPMS..."
    COMPOSE_CMD=$(resolve_docker_cmd)
    pkill -f "uvicorn apps.api.main:app" 2>/dev/null || true
    $COMPOSE_CMD down
    log_success "Servicios detenidos (datos de PostgreSQL conservados)."
    exit 0
fi

# ── PASO 1: Archivo .env y entorno Python (.venv) ────────────────────────────
log_step "PASO 1: Preparando configuración (.env) y entorno Python (.venv)"
if [ ! -f "$ROOT_DIR/.env" ]; then
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    log_info "Se creó .env automáticamente a partir de .env.example para pruebas locales."
else
    log_success "Archivo .env detectado."
fi

if [ ! -d "$ROOT_DIR/.venv" ]; then
    log_info "Creando entorno virtual .venv e instalando dependencias..."
    python3 -m venv "$ROOT_DIR/.venv"
    "$ROOT_DIR/.venv/bin/pip" install --upgrade pip -q
    "$ROOT_DIR/.venv/bin/pip" install -r "$ROOT_DIR/apps/api/requirements.txt" -q
fi
log_success "Entorno Python (.venv) listo."

# ── PASO 2: PostgreSQL 16 y Migraciones Alembic ──────────────────────────────
log_step "PASO 2: Verificando PostgreSQL 16 (puerto 5432) y migraciones Alembic"
PG_READY=false
if "$ROOT_DIR/.venv/bin/python" -c "import socket; s=socket.create_connection(('127.0.0.1', 5432), 1); s.close()" 2>/dev/null; then
    PG_READY=true
    log_success "PostgreSQL 16 ya está activo en 127.0.0.1:5432."
else
    log_info "Iniciando contenedor postgres:16-alpine con Docker Compose..."
    COMPOSE_CMD=$(resolve_docker_cmd)
    $COMPOSE_CMD up -d postgres
    for _ in {1..20}; do
        if "$ROOT_DIR/.venv/bin/python" -c "import socket; s=socket.create_connection(('127.0.0.1', 5432), 1); s.close()" 2>/dev/null; then
            PG_READY=true
            break
        fi
        sleep 1
    done
fi

if [ "$PG_READY" != true ]; then
    log_error "No se pudo conectar a PostgreSQL en 127.0.0.1:5432."
    exit 1
fi

log_info "Aplicando migraciones Alembic (001 GiST + 002 Users + 003 Conversations)..."
(cd "$ROOT_DIR/apps/api" && "$ROOT_DIR/.venv/bin/alembic" upgrade head)
log_success "Esquema PostgreSQL 16 con btree_gist y 9 habitaciones actualizado."

if [ "$RUN_TESTS" = true ]; then
    log_step "PASO 2.1: Ejecutando suite de 21 pruebas automatizadas (pytest)"
    "$ROOT_DIR/.venv/bin/pytest" -v
fi

# ── PASO 3: Backend FastAPI en puerto 8080 ───────────────────────────────────
log_step "PASO 3: Levantando Backend FastAPI (http://localhost:8080)"
pkill -f "uvicorn apps.api.main:app" 2>/dev/null || true
"$ROOT_DIR/.venv/bin/uvicorn" apps.api.main:app --host 0.0.0.0 --port 8080 > /tmp/satori_api.log 2>&1 &
API_PID=$!

API_READY=false
for _ in {1..25}; do
    if curl -fsS http://127.0.0.1:8080/api/v1/health >/dev/null 2>&1; then
        API_READY=true
        break
    fi
    sleep 0.4
done

if [ "$API_READY" != true ]; then
    log_error "FastAPI no respondió en http://127.0.0.1:8080/api/v1/health. Revisa /tmp/satori_api.log"
    cat /tmp/satori_api.log
    exit 1
fi
HEALTH_JSON=$(curl -fsS http://127.0.0.1:8080/api/v1/health)
log_success "FastAPI activo (PID $API_PID) -> /api/v1/health: $HEALTH_JSON"

if [ "$START_FRONTEND" = false ]; then
    log_info "Modo --no-frontend: verificación de infraestructura completada."
    exit 0
fi

# ── PASO 4: Frontend React + Vite en puerto 5173 ─────────────────────────────
log_step "PASO 4: Levantando Frontend Web React + Vite (http://localhost:5173)"
cd "$ROOT_DIR/apps/web"
if [ ! -d "node_modules" ]; then
    log_info "Instalando paquetes de npm en apps/web..."
    npm install --silent
fi

echo -e "\n${BOLD}${GREEN}======================================================================${NC}"
echo -e "${BOLD}${GREEN}🏨 TORRE SATORI PMS — ENTORNO WEB LOCAL ACTIVO${NC}"
echo -e "${BOLD}${GREEN}======================================================================${NC}"
echo -e "  • ${BOLD}Aplicación Web (React):${NC}   ${CYAN}http://localhost:5173${NC}"
echo -e "  • ${BOLD}Swagger UI (FastAPI):${NC}     ${CYAN}http://localhost:8080/docs${NC}"
echo -e "  • ${BOLD}Healthcheck API:${NC}          ${CYAN}http://localhost:8080/api/v1/health${NC}"
echo -e "  • ${BOLD}Logs del Backend:${NC}         ${CYAN}/tmp/satori_api.log${NC}"
echo -e "----------------------------------------------------------------------"
echo -e "  ${BOLD}Credenciales de Prueba para Iniciar Sesión en la Web:${NC}"
echo -e "  • ${BOLD}Rol Administrador:${NC}  usuario ${YELLOW}admin@gmail.com${NC}         | clave ${YELLOW}admin123${NC}"
echo -e "  • ${BOLD}Rol Recepcionista:${NC}  usuario ${YELLOW}recepcion@satoripms.com${NC} | clave ${YELLOW}recepcion123${NC}"
echo -e "${BOLD}${GREEN}======================================================================${NC}"
echo -e "  ${YELLOW}(Presiona Ctrl + C para detener tanto React como FastAPI)${NC}\n"

npm run dev

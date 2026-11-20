#!/usr/bin/env bash
# ==============================================================================
# SatoriPMS - Funciones compartidas por los scripts de desarrollo
# Uso: source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
# ==============================================================================
# Las variables se definen aquí y las usan los scripts que cargan esta librería.
# shellcheck disable=SC2034

# ── Rutas ────────────────────────────────────────────────────────────────────
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPTS_DIR="$ROOT_DIR/scripts"
WEB_DIR="$ROOT_DIR/apps/web"
ENV_FILE="$ROOT_DIR/.env"
# Estado de procesos locales (PIDs y logs de Vite y del túnel). Ignorado por git.
DEV_DIR="$ROOT_DIR/.dev"
WEB_PID_FILE="$DEV_DIR/web.pid"
WEB_LOG_FILE="$DEV_DIR/web.log"
TUNNEL_PID_FILE="$DEV_DIR/tunnel.pid"
TUNNEL_LOG_FILE="$DEV_DIR/tunnel.log"

# ── Puertos y URLs locales ───────────────────────────────────────────────────
API_PORT=8080
N8N_PORT=5678
WEB_PORT=5173
API_URL="http://localhost:$API_PORT"
N8N_URL="http://localhost:$N8N_PORT"
WEB_URL="http://localhost:$WEB_PORT"

# ── Colores y mensajes ───────────────────────────────────────────────────────
if [ -t 1 ]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'
    CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; BLUE=''; CYAN=''; BOLD=''; DIM=''; NC=''
fi

log_step()    { echo -e "\n${BOLD}${BLUE}==>${NC} ${BOLD}$1${NC}"; }
log_info()    { echo -e "  ${CYAN}[INFO]${NC} $1"; }
log_success() { echo -e "  ${GREEN}[OK]${NC}   $1"; }
log_warn()    { echo -e "  ${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "  ${RED}[ERR]${NC}  $1" >&2; }
die()         { log_error "$1"; exit 1; }

cd "$ROOT_DIR" || exit 1

refuse_root() {
    if [ "${EUID:-$(id -u)}" -eq 0 ]; then
        die "No ejecutes este script como root ni con sudo."
    fi
}

# ── Docker Compose ───────────────────────────────────────────────────────────
COMPOSE=()
detect_compose() {
    if docker compose version >/dev/null 2>&1; then
        COMPOSE=(docker compose)
    elif command -v docker-compose >/dev/null 2>&1; then
        COMPOSE=(docker-compose)
    else
        die "Docker Compose no está disponible ('docker compose' ni 'docker-compose'). En Arch/EndeavourOS: sudo pacman -S docker-compose"
    fi
    if ! docker info >/dev/null 2>&1; then
        die "El demonio de Docker no responde. Inícialo con: sudo systemctl start docker"
    fi
}

compose() { "${COMPOSE[@]}" "$@"; }

# Nombre del proyecto Compose (prefijo de contenedores de red y volúmenes).
compose_project_name() {
    if [ -n "${COMPOSE_PROJECT_NAME:-}" ]; then
        echo "$COMPOSE_PROJECT_NAME"
    else
        basename "$ROOT_DIR" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9_-'
    fi
}

# ── Variables del .env ───────────────────────────────────────────────────────
# Devuelve el último valor asignado a una clave del .env (sin comillas).
env_get() {
    local key="$1"
    [ -f "$ENV_FILE" ] || return 0
    grep -E "^[[:space:]]*${key}=" "$ENV_FILE" | tail -n 1 | cut -d '=' -f2- \
        | sed -e 's/[[:space:]]*$//' -e 's/^"\(.*\)"$/\1/' -e "s/^'\(.*\)'$/\1/"
}

# true si el perfil n8n está activo en COMPOSE_PROFILES.
n8n_enabled() {
    local profiles
    profiles="$(env_get COMPOSE_PROFILES)"
    [[ ",${profiles// /}," == *",n8n,"* ]]
}

# ── Utilidades de red y procesos ─────────────────────────────────────────────
# Código HTTP de una URL (000 si no responde).
http_code() {
    local code
    code="$(curl -s -o /dev/null -m "${2:-5}" -w '%{http_code}' "$1" 2>/dev/null)" || true
    echo "${code:-000}"
}

# Espera a que una URL responda con alguno de los códigos esperados.
# Uso: wait_for_http <url> <timeout_s> <etiqueta> [códigos separados por espacio]
wait_for_http() {
    local url="$1" timeout="$2" label="$3" expected="${4:-200}"
    local elapsed=0 code
    while [ "$elapsed" -lt "$timeout" ]; do
        code="$(http_code "$url" 3)"
        for ok in $expected; do
            if [ "$code" = "$ok" ]; then
                log_success "$label responde (HTTP $code)."
                return 0
            fi
        done
        sleep 2
        elapsed=$((elapsed + 2))
    done
    log_error "$label no respondió en ${timeout}s (último código: $code)."
    return 1
}

pid_alive() {
    local file="$1" pid
    [ -f "$file" ] || return 1
    pid="$(cat "$file" 2>/dev/null)"
    [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

# Detiene el grupo de procesos guardado en un archivo de PID.
stop_pid_group() {
    local file="$1" label="$2" pid
    if ! pid_alive "$file"; then
        rm -f "$file"
        return 1
    fi
    pid="$(cat "$file")"
    kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
    for _ in 1 2 3 4 5 6 7 8 9 10; do
        kill -0 "$pid" 2>/dev/null || break
        sleep 0.5
    done
    kill -KILL -- "-$pid" 2>/dev/null || true
    rm -f "$file"
    log_success "$label detenido (PID $pid)."
    return 0
}

# Lanza un comando en segundo plano, en su propio grupo de procesos.
# Uso: start_background <pid_file> <log_file> <directorio> <comando...>
start_background() {
    local pid_file="$1" log_file="$2" workdir="$3"
    shift 3
    mkdir -p "$DEV_DIR"
    rm -f "$pid_file"
    # setsid puede crear un proceso nuevo, así que el PID lo escribe el propio proceso
    # ya convertido en líder de sesión: así stop_pid_group detiene a todo su grupo.
    (cd "$workdir" && setsid bash -c 'echo $$ >"$0"; exec nohup "$@"' "$pid_file" "$@" \
        >"$log_file" 2>&1 </dev/null &)
    for _ in 1 2 3 4 5 6 7 8 9 10; do
        [ -s "$pid_file" ] && break
        sleep 0.2
    done
    sleep 1
}

# ── Túnel público (zrok2) ────────────────────────────────────────────────────
# Nombre reservado del share a partir de N8N_PUBLIC_URL (https://<nombre>.shares.zrok.io/).
zrok_share_name() {
    local url host
    url="$(env_get N8N_PUBLIC_URL)"
    host="${url#*://}"
    host="${host%%/*}"
    if [[ "$host" == *.shares.zrok.io ]]; then
        echo "${host%%.shares.zrok.io}"
    fi
}

public_n8n_url() {
    local url
    url="$(env_get N8N_PUBLIC_URL)"
    echo "${url%/}"
}

# ── Resumen de enlaces ───────────────────────────────────────────────────────
# Rellena una etiqueta a 22 caracteres (cuenta caracteres, no bytes, para las tildes).
pad_label() {
    local text="$1" width=22
    printf '%s%*s' "$text" $((width - ${#text})) ''
}

status_label() {
    local code="$1"
    case "$code" in
        2??|3??|401|403) echo -e "${GREEN}activo${NC}" ;;
        000) echo -e "${RED}sin respuesta${NC}" ;;
        *) echo -e "${YELLOW}HTTP $code${NC}" ;;
    esac
}

print_links() {
    local public
    public="$(public_n8n_url)"
    echo
    echo -e "${BOLD}${GREEN}══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${GREEN}  SatoriPMS — Enlaces de acceso${NC}"
    echo -e "${BOLD}${GREEN}══════════════════════════════════════════════════════════════════${NC}"
    printf "  %s ${CYAN}%s${NC}  [%b]\n" "$(pad_label "Aplicación web")" "$WEB_URL" "$(status_label "$(http_code "$WEB_URL")")"
    printf "  %s ${CYAN}%s${NC}  [%b]\n" "$(pad_label "Backend (API)")" "$API_URL" "$(status_label "$(http_code "$API_URL/api/v1/health")")"
    printf "  %s ${CYAN}%s${NC}\n" "$(pad_label "Documentación API")" "$API_URL/docs"
    if n8n_enabled; then
        printf "  %s ${CYAN}%s${NC}  [%b]\n" "$(pad_label "n8n (editor local)")" "$N8N_URL" "$(status_label "$(http_code "$N8N_URL/healthz")")"
        if [ -n "$public" ]; then
            printf "  %s ${CYAN}%s${NC}  [%b]\n" "$(pad_label "n8n (público)")" "$public" "$(status_label "$(http_code "$public/healthz" 8)")"
            printf "  %s ${CYAN}%s${NC}\n" "$(pad_label "Webhook WhatsApp")" "$public/webhook/whatsapp-webhook"
            printf "  %s ${CYAN}%s${NC}\n" "$(pad_label "Webhook Wompi")" "$public/webhook/wompi-events"
        fi
    else
        printf "  %s ${YELLOW}%s${NC}\n" "$(pad_label "n8n")" "desactivado (agrega 'n8n' a COMPOSE_PROFILES en .env)"
    fi
    echo -e "${BOLD}${GREEN}══════════════════════════════════════════════════════════════════${NC}"
    echo -e "  ${DIM}Estado detallado: ./scripts/status-dev.sh   ·   Detener: ./scripts/stop-dev.sh${NC}"
    echo -e "  ${DIM}Logs: docker compose logs -f api   ·   Web: tail -f .dev/web.log${NC}"
}

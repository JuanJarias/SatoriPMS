#!/usr/bin/env bash
# ==============================================================================
# SatoriPMS - Levantar el entorno de desarrollo completo
#
# 1. Verifica herramientas y el archivo .env (secretos obligatorios).
# 2. Levanta PostgreSQL, API (FastAPI), Redis (solo n8n) y n8n con Docker Compose y espera a que
#    cada servicio responda.
# 3. Abre el túnel público zrok2 para n8n (WhatsApp y Wompi), si aplica.
# 4. Inicia la aplicación web (Vite) en segundo plano.
# 5. Muestra los enlaces de acceso (clicables) y, con --open, los abre en el navegador.
# ==============================================================================
set -Eeuo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

START_INFRA=true
START_WEB=true
START_TUNNEL=true
BUILD=true
SYNC_FLOW=false
OPEN_BROWSER=false

show_help() {
    cat <<EOF
Uso: ./scripts/start-dev.sh [opciones]

Levanta toda la infraestructura y deja los servicios listos para usar.

Opciones:
  --no-frontend      No inicia la aplicación web (Vite).
  --frontend-only    Solo inicia la aplicación web (sin Docker).
  --no-tunnel        No abre el túnel público zrok2 para n8n.
  --no-build         No reconstruye la imagen de la API (más rápido si no cambió el código).
  --sync-flow        Importa y publica el flujo V9 en n8n al terminar.
  --open             Abre en el navegador la aplicación web, n8n y la documentación de la API.
  -h, --help         Muestra esta ayuda.

Otros scripts:
  ./scripts/stop-dev.sh       Detiene todo conservando los datos.
  ./scripts/reset-dev.sh      Borra contenedores y datos (pide confirmación).
  ./scripts/status-dev.sh     Diagnóstico de servicios, túnel y WhatsApp.
  ./scripts/sync-n8n-flow.sh  Importa y publica el flujo V9 en n8n.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) show_help; exit 0 ;;
        --no-frontend) START_WEB=false ;;
        --frontend-only|--only-frontend) START_INFRA=false; START_TUNNEL=false ;;
        --no-tunnel) START_TUNNEL=false ;;
        --no-build) BUILD=false ;;
        -u|--update) BUILD=true ;;   # compatibilidad con la versión anterior
        --sync-flow) SYNC_FLOW=true ;;
        --open) OPEN_BROWSER=true ;;
        -d|--down)                    # compatibilidad con la versión anterior
            log_warn "'start-dev.sh $1' está obsoleto; usa ./scripts/stop-dev.sh"
            exec "$SCRIPTS_DIR/stop-dev.sh" ;;
        -D|--destroy)                 # compatibilidad con la versión anterior
            log_warn "'start-dev.sh $1' está obsoleto; usa ./scripts/reset-dev.sh"
            exec "$SCRIPTS_DIR/reset-dev.sh" ;;
        *) log_error "Opción no reconocida: $1"; show_help; exit 1 ;;
    esac
    shift
done

refuse_root

# ── 1. Dependencias ──────────────────────────────────────────────────────────
log_step "PASO 1: Verificando herramientas"
for cmd in curl setsid; do
    command -v "$cmd" >/dev/null 2>&1 || die "Falta el comando '$cmd'."
done
if $START_WEB; then
    for cmd in node npm; do
        command -v "$cmd" >/dev/null 2>&1 || die "Falta '$cmd' (necesario para la aplicación web). Usa --no-frontend para omitirla."
    done
    log_success "Node.js $(node --version) y npm $(npm --version)."
fi
if $START_INFRA; then
    command -v docker >/dev/null 2>&1 || die "Falta 'docker'."
    detect_compose
    log_success "Docker y ${COMPOSE[*]} listos."
fi

# ── 2. Archivo .env ──────────────────────────────────────────────────────────
log_step "PASO 2: Verificando el archivo .env"
if [ ! -f "$ENV_FILE" ]; then
    cp "$ROOT_DIR/.env.example" "$ENV_FILE"
    log_warn "No existía .env: se creó desde .env.example."
    log_warn "Completa los secretos (guía: docs/Guia_Configuracion_Entorno.md) y vuelve a ejecutar."
    exit 1
fi
if $START_INFRA; then
    env_ok=true
    jwt="$(env_get JWT_SECRET)"
    if [ "${#jwt}" -lt 32 ]; then
        log_error "JWT_SECRET debe tener al menos 32 caracteres (la API no arranca). Genera uno con: openssl rand -hex 32"
        env_ok=false
    fi
    service_key="$(env_get SATORI_SERVICE_KEY)"
    if [ -z "$service_key" ] || [ "$service_key" = "cambia_esta_llave_de_servicio" ]; then
        log_error "Falta SATORI_SERVICE_KEY en .env (n8n no podrá llamar a la API). Genera una con: openssl rand -hex 32"
        env_ok=false
    fi
    $env_ok || exit 1
    log_success "Secretos obligatorios presentes."
fi

# ── 3. Contenedores ──────────────────────────────────────────────────────────
if $START_INFRA; then
    log_step "PASO 3: Levantando contenedores (PostgreSQL, API$(n8n_enabled && echo ', n8n'))"
    up_args=(up -d --remove-orphans --wait --wait-timeout 240)
    if $BUILD; then
        up_args+=(--build)
        log_info "Construyendo la API dentro de Docker (la primera vez tarda unos minutos)..."
    fi
    if ! compose "${up_args[@]}"; then
        log_error "Docker Compose no pudo levantar los servicios. Revisa: docker compose logs --tail 50"
        exit 1
    fi
    log_success "Contenedores en ejecución."

    # Una base creada por el backend Java anterior (Flyway) no admite las migraciones de Alembic.
    legacy_schema="$(compose exec -T postgres sh -c 'psql -tA -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT to_regclass('"'"'public.flyway_schema_history'"'"') IS NOT NULL AND to_regclass('"'"'public.alembic_version'"'"') IS NULL"' 2>/dev/null | tr -d '[:space:]' || true)"
    if [ "$legacy_schema" = "t" ]; then
        log_error "La base de datos tiene el esquema del servidor Java anterior (Flyway) y la API nueva no puede migrarlo."
        log_info "Los datos locales no son compatibles. Para empezar de cero (BORRA la información local) ejecuta:"
        log_info "  ./scripts/reset-dev.sh --start"
        exit 1
    fi
    wait_for_http "$API_URL/api/v1/health" 120 "Backend (API)" || {
        log_info "Últimas líneas de la API:"; compose logs --tail 20 api || true; exit 1; }
    if n8n_enabled; then
        wait_for_http "$N8N_URL/healthz" 120 "n8n" || {
            log_info "Últimas líneas de n8n:"; compose logs --tail 20 n8n || true; exit 1; }
    else
        log_info "n8n desactivado (COMPOSE_PROFILES no incluye 'n8n')."
    fi
fi

# ── 4. Túnel público para n8n ────────────────────────────────────────────────
if $START_INFRA && $START_TUNNEL && n8n_enabled; then
    log_step "PASO 4: Túnel público de n8n"
    public="$(public_n8n_url)"
    share="$(zrok_share_name)"
    if [ -z "$public" ]; then
        log_warn "N8N_PUBLIC_URL está vacío: WhatsApp y Wompi no podrán llegar a n8n."
    elif [ "$(http_code "$public/healthz" 8)" = "200" ]; then
        log_success "El túnel ya está activo: $public"
    elif [ -z "$share" ]; then
        log_warn "N8N_PUBLIC_URL ($public) no es de zrok2 y no responde. Levanta tu túnel manualmente."
    elif ! command -v zrok2 >/dev/null 2>&1; then
        log_warn "zrok2 no está instalado; no se puede abrir el túnel $public"
    else
        log_info "Abriendo túnel zrok2 '$share' hacia el puerto $N8N_PORT..."
        start_background "$TUNNEL_PID_FILE" "$TUNNEL_LOG_FILE" "$ROOT_DIR" \
            zrok2 share public "$N8N_PORT" -n "public:$share" --headless
        if ! wait_for_http "$public/healthz" 40 "Túnel público"; then
            log_warn "Revisa $TUNNEL_LOG_FILE. Si aparece '409 shareConflict', libera el share huérfano:"
            log_warn "  zrok2 delete share <share_id>   y vuelve a ejecutar este script."
            stop_pid_group "$TUNNEL_PID_FILE" "Túnel zrok2" >/dev/null || true
        fi
    fi
fi

# ── 5. Aplicación web ────────────────────────────────────────────────────────
if $START_WEB; then
    log_step "PASO 5: Aplicación web (React + Vite)"
    if pid_alive "$WEB_PID_FILE" || [ "$(http_code "$WEB_URL")" = "200" ]; then
        log_success "La aplicación web ya está en ejecución."
    else
        if [ ! -d "$WEB_DIR/node_modules" ] || [ "$WEB_DIR/package-lock.json" -nt "$WEB_DIR/node_modules/.package-lock.json" ]; then
            log_info "Instalando dependencias de npm..."
            (cd "$WEB_DIR" && npm install --silent --no-audit --no-fund)
        fi
        start_background "$WEB_PID_FILE" "$WEB_LOG_FILE" "$WEB_DIR" npm run dev
        wait_for_http "$WEB_URL" 60 "Aplicación web" || {
            log_info "Últimas líneas de $WEB_LOG_FILE:"; tail -n 20 "$WEB_LOG_FILE" || true; exit 1; }
    fi
fi

# ── 6. Flujo n8n (opcional) ──────────────────────────────────────────────────
if $SYNC_FLOW && $START_INFRA && n8n_enabled; then
    "$SCRIPTS_DIR/sync-n8n-flow.sh"
fi

print_links

if $OPEN_BROWSER; then
    $START_WEB && open_url "$WEB_URL"
    if $START_INFRA; then
        n8n_enabled && open_url "$N8N_URL"
        open_url "$API_URL/docs"
    fi
fi

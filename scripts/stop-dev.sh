#!/usr/bin/env bash
# ==============================================================================
# SatoriPMS - Detener el entorno de desarrollo (conservando los datos)
#
# Detiene la aplicación web y el túnel iniciados por start-dev.sh y da de baja
# los contenedores. Los volúmenes (base de datos, Redis y n8n) se conservan.
# ==============================================================================
set -Eeuo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

STOP_WEB=true
STOP_TUNNEL=true
STOP_INFRA=true
PAUSE_ONLY=false

show_help() {
    cat <<EOF
Uso: ./scripts/stop-dev.sh [opciones]

Detiene todo el entorno sin borrar datos.

Opciones:
  --pause         Solo pausa los contenedores (docker compose stop); arrancan más rápido después.
  --keep-tunnel   No cierra el túnel zrok2.
  --web-only      Solo detiene la aplicación web.
  -h, --help      Muestra esta ayuda.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) show_help; exit 0 ;;
        --pause) PAUSE_ONLY=true ;;
        --keep-tunnel) STOP_TUNNEL=false ;;
        --web-only) STOP_TUNNEL=false; STOP_INFRA=false ;;
        *) log_error "Opción no reconocida: $1"; show_help; exit 1 ;;
    esac
    shift
done

refuse_root
log_step "Deteniendo SatoriPMS"

if $STOP_WEB; then
    stop_pid_group "$WEB_PID_FILE" "Aplicación web" || log_info "La aplicación web no estaba en ejecución (iniciada por start-dev.sh)."
fi

if $STOP_TUNNEL; then
    stop_pid_group "$TUNNEL_PID_FILE" "Túnel zrok2" || log_info "No hay túnel iniciado por start-dev.sh."
fi

if $STOP_INFRA; then
    detect_compose
    if $PAUSE_ONLY; then
        compose stop
        log_success "Contenedores pausados. Reanuda con ./scripts/start-dev.sh --no-build"
    else
        compose down --remove-orphans
        log_success "Contenedores dados de baja. Los datos (volúmenes) se conservan."
    fi
fi

#!/usr/bin/env bash
# ==============================================================================
# SatoriPMS - Reiniciar el entorno de desarrollo desde cero
#
# Detiene todo y BORRA los volúmenes de datos: base de datos (reservas,
# huéspedes, habitaciones...), Redis (sesiones y bloqueos) y, salvo que se use
# --keep-n8n, también n8n (cuenta, credenciales, flujos e historial).
# ==============================================================================
set -Eeuo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

KEEP_N8N=false
ASSUME_YES=false
START_AFTER=false
SEED=false
REMOVE_IMAGES=false

show_help() {
    cat <<EOF
Uso: ./scripts/reset-dev.sh [opciones]

Borra contenedores y datos del entorno local. Pide confirmación.

Opciones:
  --keep-n8n     Conserva los datos de n8n (cuenta, credenciales y flujos); solo borra PostgreSQL y Redis.
  --images       Borra también la imagen construida de la API (fuerza recompilación completa).
  --start        Vuelve a levantar todo al terminar (start-dev.sh).
  --seed         Con --start: además publica el flujo V9 en n8n (las habitaciones y los usuarios de
                 desarrollo los crea Alembic al arrancar la API).
  -y, --yes      No pide confirmación.
  -h, --help     Muestra esta ayuda.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) show_help; exit 0 ;;
        --keep-n8n) KEEP_N8N=true ;;
        --images) REMOVE_IMAGES=true ;;
        --start) START_AFTER=true ;;
        --seed) SEED=true; START_AFTER=true ;;
        -y|--yes) ASSUME_YES=true ;;
        *) log_error "Opción no reconocida: $1"; show_help; exit 1 ;;
    esac
    shift
done

refuse_root
detect_compose
project="$(compose_project_name)"

log_step "REINICIO COMPLETO DEL ENTORNO"
log_warn "Se borrarán de forma permanente:"
log_warn "  • Base de datos PostgreSQL (${project}_postgres_data): reservas, huéspedes, habitaciones, usuarios."
log_warn "  • Redis (${project}_redis_data): sesiones del chatbot, bloqueos y links de Wompi."
if $KEEP_N8N; then
    log_info "  • n8n se conserva (--keep-n8n)."
else
    log_warn "  • n8n (${project}_n8n_data): cuenta de acceso, credenciales, flujos e historial de ejecuciones."
fi

if ! $ASSUME_YES; then
    read -r -p "  Escribe RESET para confirmar: " confirm
    if [ "$confirm" != "RESET" ]; then
        log_info "Operación cancelada. No se borró nada."
        exit 0
    fi
fi

# La aplicación web se detiene; el túnel se conserva porque no guarda datos.
"$SCRIPTS_DIR/stop-dev.sh" --web-only >/dev/null 2>&1 || true

down_args=(down --remove-orphans)
$REMOVE_IMAGES && down_args+=(--rmi local)
if $KEEP_N8N; then
    compose "${down_args[@]}"
    for vol in "${project}_postgres_data" "${project}_redis_data"; do
        if docker volume inspect "$vol" >/dev/null 2>&1; then
            docker volume rm "$vol" >/dev/null
            log_success "Volumen $vol eliminado."
        fi
    done
else
    compose "${down_args[@]}" --volumes
    log_success "Contenedores y volúmenes eliminados."
fi
rm -f "$WEB_LOG_FILE"
log_success "Entorno reiniciado."

if $START_AFTER; then
    start_args=()
    $SEED && start_args+=(--sync-flow)
    "$SCRIPTS_DIR/start-dev.sh" "${start_args[@]}"
    if $SEED; then
        log_success "Datos de prueba creados por Alembic. Usuarios de desarrollo: admin / admin123 y recepcion / recepcion123."
        if ! $KEEP_N8N && n8n_enabled; then
            log_warn "n8n quedó sin cuenta ni credenciales: abre $N8N_URL para crear el usuario propietario."
        fi
    fi
else
    log_info "Levanta de nuevo con: ./scripts/start-dev.sh"
fi

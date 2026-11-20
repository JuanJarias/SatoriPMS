#!/usr/bin/env bash
# ==============================================================================
# SatoriPMS - Diagnóstico del entorno de desarrollo
#
# Muestra el estado de contenedores, servicios, aplicación web, túnel público y
# la configuración de WhatsApp en Meta (vigencia del token y suscripción de la
# app a la cuenta de WhatsApp Business). Solo lectura: no modifica nada.
# ==============================================================================
set -Eeuo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

CHECK_META=true

show_help() {
    cat <<EOF
Uso: ./scripts/status-dev.sh [opciones]

Opciones:
  --no-meta    No consulta la API de Meta (token y suscripción de WhatsApp).
  -h, --help   Muestra esta ayuda.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) show_help; exit 0 ;;
        --no-meta) CHECK_META=false ;;
        *) log_error "Opción no reconocida: $1"; show_help; exit 1 ;;
    esac
    shift
done

detect_compose

log_step "Contenedores"
compose ps --format 'table {{.Name}}\t{{.State}}\t{{.Status}}' || true

log_step "Procesos locales"
if pid_alive "$WEB_PID_FILE"; then
    log_success "Aplicación web en ejecución (PID $(cat "$WEB_PID_FILE"), log: .dev/web.log)."
elif [ "$(http_code "$WEB_URL")" = "200" ]; then
    log_info "La aplicación web responde, pero no fue iniciada por start-dev.sh."
else
    log_warn "La aplicación web no está en ejecución."
fi
if pid_alive "$TUNNEL_PID_FILE"; then
    log_success "Túnel zrok2 en ejecución (PID $(cat "$TUNNEL_PID_FILE"), log: .dev/tunnel.log)."
elif pgrep -f "zrok2 share" >/dev/null 2>&1; then
    log_info "Hay un túnel zrok2 activo iniciado fuera de start-dev.sh."
else
    log_warn "No hay túnel zrok2 en ejecución."
fi

if $CHECK_META && n8n_enabled; then
    log_step "WhatsApp en Meta (solo lectura)"
    token="$(env_get WHATSAPP_TOKEN)"
    waba="$(env_get WHATSAPP_ACCOUNT_ID)"
    phone="$(env_get WHATSAPP_PHONE_ID)"
    version="$(env_get WHATSAPP_GRAPH_VERSION)"; version="${version:-v25.0}"
    if [ -z "$token" ] || [ -z "$waba" ]; then
        log_warn "Faltan WHATSAPP_TOKEN o WHATSAPP_ACCOUNT_ID en .env."
    else
        graph="https://graph.facebook.com/$version"
        auth=(-H "Authorization: Bearer $token")
        debug="$(curl -s -m 10 "$graph/debug_token?input_token=$token" "${auth[@]}" || true)"
        subs="$(curl -s -m 10 "$graph/$waba/subscribed_apps" "${auth[@]}" || true)"
        number="$(curl -s -m 10 "$graph/$phone?fields=display_phone_number,status,quality_rating" "${auth[@]}" || true)"
        python3 - "$debug" "$subs" "$number" <<'PY'
import json, sys, time
from datetime import datetime
G, Y, R, N = "\033[0;32m", "\033[1;33m", "\033[0;31m", "\033[0m"
def load(s):
    try: return json.loads(s)
    except Exception: return {}
debug, subs, number = (load(x) for x in sys.argv[1:4])
d = debug.get("data", {})
if not d:
    print(f"  {R}[ERR]{N}  No se pudo validar el token: {debug.get('error', {}).get('message', 'sin respuesta')}")
    sys.exit(0)
if not d.get("is_valid"):
    print(f"  {R}[ERR]{N}  El token de WhatsApp NO es válido (vencido o revocado). Renueva WHATSAPP_TOKEN y recrea n8n.")
else:
    exp = d.get("expires_at") or 0
    if exp == 0:
        print(f"  {G}[OK]{N}   Token válido y sin vencimiento (usuario de sistema).")
    else:
        hours = (exp - time.time()) / 3600
        when = datetime.fromtimestamp(exp).strftime("%Y-%m-%d %H:%M")
        color, tag = (G, "OK") if hours > 6 else (Y, "WARN")
        print(f"  {color}[{tag}]{N} Token válido; vence el {when} (en {hours:.1f} h).")
app_id = d.get("app_id")
apps = [a.get("whatsapp_business_api_data", {}) for a in subs.get("data", [])]
if any(a.get("id") == app_id for a in apps):
    print(f"  {G}[OK]{N}   La app {d.get('application', app_id)} está suscrita a la cuenta de WhatsApp Business.")
else:
    names = ", ".join(a.get("name", "?") for a in apps) or "ninguna"
    print(f"  {R}[ERR]{N}  La app {d.get('application', app_id)} NO está suscrita a la cuenta (suscritas: {names}).")
    print(f"         Meta no entregará mensajes a n8n. Suscríbela en WhatsApp > Configuración > Webhooks")
    print(f"         o con: POST /<WHATSAPP_ACCOUNT_ID>/subscribed_apps")
if number.get("display_phone_number"):
    print(f"  [INFO] Número {number['display_phone_number']}: estado {number.get('status')}, calidad {number.get('quality_rating')}.")
PY
    fi
fi

print_links

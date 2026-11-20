#!/usr/bin/env bash
# ==============================================================================
# SatoriPMS - Importar y publicar el flujo del chatbot en n8n
#
# n8n mantiene publicada la versión anterior si el campo "versionId" del JSON
# no cambia. Este script importa una copia temporal del flujo con un versionId
# nuevo (sin modificar el archivo del repositorio), la publica y reinicia n8n.
# ==============================================================================
set -Eeuo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

FLOW_FILE="$ROOT_DIR/flows/n8n/V10_ChatbotReservas.json"
N8N_CONTAINER="satori_n8n"

show_help() {
    cat <<EOF
Uso: ./scripts/sync-n8n-flow.sh [ruta_flujo.json]

Importa y publica en n8n el flujo indicado (por defecto flows/n8n/V10_ChatbotReservas.json)
y reinicia n8n para que el cambio quede activo.
EOF
}

case "${1:-}" in
    -h|--help) show_help; exit 0 ;;
    "") ;;
    *) FLOW_FILE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" ;;
esac

refuse_root
detect_compose
[ -f "$FLOW_FILE" ] || die "No existe el flujo: $FLOW_FILE"
command -v python3 >/dev/null 2>&1 || die "Falta python3."
docker inspect -f '{{.State.Running}}' "$N8N_CONTAINER" 2>/dev/null | grep -q true \
    || die "El contenedor $N8N_CONTAINER no está en ejecución. Levántalo con ./scripts/start-dev.sh"

log_step "Sincronizando flujo n8n: $(basename "$FLOW_FILE")"

log_info "Verificando integridad del flujo..."
integrity="$(python3 "$ROOT_DIR/tests/chatbot/verify_n8n_flow_integrity.py" "$FLOW_FILE")"
echo "$integrity" | grep -q "ALL CHECKS PASSED" || { echo "$integrity"; die "El flujo tiene errores de integridad; no se importa."; }
log_success "Integridad verificada."

mkdir -p "$DEV_DIR"
tmp_flow="$DEV_DIR/flow-import.json"
flow_id="$(python3 - "$FLOW_FILE" "$tmp_flow" <<'PY'
import json, sys, uuid
src, dst = sys.argv[1], sys.argv[2]
flow = json.load(open(src, encoding="utf-8"))
flow["versionId"] = str(uuid.uuid4())
json.dump(flow, open(dst, "w", encoding="utf-8"), ensure_ascii=False)
print(flow.get("id", ""))
PY
)"
[ -n "$flow_id" ] || die "El flujo no tiene campo 'id'."

docker cp "$tmp_flow" "$N8N_CONTAINER:/tmp/flow-import.json" >/dev/null
filter='deprecat|N8N_|^ -|There are|Python|license'
docker exec "$N8N_CONTAINER" n8n import:workflow --input=/tmp/flow-import.json 2>&1 | grep -Ev "$filter" || true
docker exec "$N8N_CONTAINER" n8n publish:workflow --id="$flow_id" 2>&1 | grep -Ev "$filter" || true
docker exec "$N8N_CONTAINER" rm -f /tmp/flow-import.json || true
rm -f "$tmp_flow"

log_info "Reiniciando n8n para activar la versión publicada..."
docker restart "$N8N_CONTAINER" >/dev/null
wait_for_http "$N8N_URL/healthz" 90 "n8n"
log_success "Flujo '$flow_id' importado y publicado."

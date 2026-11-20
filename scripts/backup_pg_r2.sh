#!/usr/bin/env bash
# ==============================================================================
# SatoriPMS — Respaldo diario cifrado de PostgreSQL 16 hacia Cloudflare R2
# Cron sugerido (3:00 a. m. hora Colombia):
#   0 3 * * * /ruta/SatoriPMS/scripts/backup_pg_r2.sh >> /var/log/satori_backup.log 2>&1
# ==============================================================================
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" || "${1:-}" == "--check" ]] && DRY_RUN=true

if [ -f "$ENV_FILE" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
        line="${line%$'\r'}"
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# || "$line" != *=* ]] && continue
        key="${line%%=*}"
        val="${line#*=}"
        key="$(printf '%s' "$key" | xargs)"
        [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || continue
        if [[ "$val" =~ ^\"(.*)\"$ || "$val" =~ ^\'(.*)\'$ ]]; then
            val="${BASH_REMATCH[1]}"
        fi
        export "$key=$val"
    done < "$ENV_FILE"
fi

PG_CONTAINER="${PG_CONTAINER:-satori_postgres}"
if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "$PG_CONTAINER"; then
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "satori_postgres_prod"; then
        PG_CONTAINER="satori_postgres_prod"
    fi
fi

POSTGRES_USER="${POSTGRES_USER:-satori}"
POSTGRES_DB="${POSTGRES_DB:-satoripms}"
BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/.dev/backups}"
mkdir -p "$BACKUP_DIR"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RAW_DUMP="$BACKUP_DIR/satoripms_${STAMP}.dump"
ENC_DUMP="${RAW_DUMP}.enc"

cleanup() {
    rm -f "$RAW_DUMP" "$ENC_DUMP"
}
trap cleanup EXIT

if $DRY_RUN; then
    echo "[DRY-RUN] Verificando herramientas y variables para respaldo cifrado..."
    command -v openssl >/dev/null 2>&1 || { echo "Falta openssl"; exit 1; }
    echo "[DRY-RUN] Contenedor objetivo: $PG_CONTAINER | Base: $POSTGRES_DB"
    echo "[DRY-RUN] Destino R2: ${R2_BUCKET:-satoripms-backups} (${R2_ENDPOINT:-no configurado})"
    exit 0
fi

: "${BACKUP_ENCRYPTION_KEY:?Defina BACKUP_ENCRYPTION_KEY para cifrar el respaldo (AES-256-CBC)}"
: "${R2_BUCKET:?Defina R2_BUCKET}"
: "${R2_ENDPOINT:?Defina R2_ENDPOINT (https://<account_id>.r2.cloudflarestorage.com)}"

command -v aws >/dev/null 2>&1 || { echo "Falta awscli para subir a Cloudflare R2"; exit 1; }
command -v openssl >/dev/null 2>&1 || { echo "Falta openssl"; exit 1; }

echo "[1/3] Generando pg_dump comprimido desde $PG_CONTAINER ($POSTGRES_DB)..."
docker exec "$PG_CONTAINER" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > "$RAW_DUMP"

echo "[2/3] Cifrando respaldo con AES-256-CBC + PBKDF2..."
export BACKUP_ENCRYPTION_KEY
openssl enc -aes-256-cbc -salt -pbkdf2 -in "$RAW_DUMP" -out "$ENC_DUMP" -pass env:BACKUP_ENCRYPTION_KEY

echo "[3/3] Subiendo a Cloudflare R2 s3://${R2_BUCKET}/postgres/..."
AWS_ACCESS_KEY_ID="${R2_ACCESS_KEY_ID:-${AWS_ACCESS_KEY_ID:-}}" \
AWS_SECRET_ACCESS_KEY="${R2_SECRET_ACCESS_KEY:-${AWS_SECRET_ACCESS_KEY:-}}" \
aws s3 cp "$ENC_DUMP" "s3://${R2_BUCKET}/postgres/$(basename "$ENC_DUMP")" --endpoint-url "$R2_ENDPOINT"

echo "Respaldo completado y cifrado: $(basename "$ENC_DUMP")"

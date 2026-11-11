#!/usr/bin/env bash
# ==============================================================================
# SatoriPMS - Acceso directo a scripts/start-dev.sh
# ==============================================================================
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/scripts/start-dev.sh" "$@"

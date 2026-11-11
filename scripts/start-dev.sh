#!/usr/bin/env bash
# ==============================================================================
# SatoriPMS - Script de Inicialización y Desarrollo (Dev Server)
# ==============================================================================
set -e # Salir inmediatamente si un comando falla

# ------------------------------------------------------------------------------
# Variables y Colores
# ------------------------------------------------------------------------------
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Opciones por defecto
START_FRONTEND=true
ONLY_FRONTEND=false
STOP_ONLY=false
DESTROY_ONLY=false
UPDATE_INFRA=false

# ------------------------------------------------------------------------------
# Funciones de Logging
# ------------------------------------------------------------------------------
log_step()    { echo -e "\n${BOLD}${BLUE}==>${NC} ${BOLD}$1${NC}"; }
log_info()    { echo -e "  ${CYAN}[INFO]${NC} $1"; }
log_success() { echo -e "  ${GREEN}[OK]${NC}   $1"; }
log_warn()    { echo -e "  ${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "  ${RED}[ERR]${NC}  $1"; }

# ------------------------------------------------------------------------------
# Detección de Docker Compose (v2 plugin o standalone)
# ------------------------------------------------------------------------------
get_compose_cmd() {
    if docker compose version >/dev/null 2>&1; then
        echo "docker compose"
    elif command -v docker-compose >/dev/null 2>&1; then
        echo "docker-compose"
    else
        echo ""
    fi
}

# ------------------------------------------------------------------------------
# Función de Ayuda
# ------------------------------------------------------------------------------
show_help() {
    echo -e "${BOLD}Uso: ./start-dev.sh [opciones]${NC}"
    echo
    echo "Opciones de Arranque:"
    echo "  -h, --help            Muestra esta ayuda y sale."
    echo "  --frontend-only       Inicia únicamente la aplicación web React (sin requerir Docker)."
    echo "  --no-frontend         Levanta la infraestructura Docker pero NO inicia React."
    echo "  -u, --update          Reconstruye las imágenes de Docker vía multi-stage build."
    echo
    echo "Opciones de Detención/Destrucción:"
    echo "  -d, --down            Detiene los contenedores sin borrar los datos."
    echo "  -D, --destroy         ¡PELIGRO! Detiene y BORRA completamente todos los contenedores y volúmenes."
    echo
    echo "Ejemplos:"
    echo "  ./scripts/start-dev.sh                 (Inicia todo el stack)"
    echo "  ./scripts/start-dev.sh --frontend-only (Inicia interfaz web React en Vite)"
    echo "  ./scripts/start-dev.sh -u              (Reconstruye contenedores e inicia)"
}

# ------------------------------------------------------------------------------
# Analizar Argumentos CLI
# ------------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        --frontend-only|--only-frontend)
            ONLY_FRONTEND=true
            shift
            ;;
        --no-frontend)
            START_FRONTEND=false
            shift
            ;;
        -d|--down)
            STOP_ONLY=true
            shift
            ;;
        -D|--destroy)
            DESTROY_ONLY=true
            shift
            ;;
        -u|--update)
            UPDATE_INFRA=true
            shift
            ;;
        *)
            log_error "Opción no reconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# ------------------------------------------------------------------------------
# Fase de Detención / Destrucción
# ------------------------------------------------------------------------------
COMPOSE_BIN="$(get_compose_cmd)"

if [ "$DESTROY_ONLY" = true ]; then
    log_step "DESTRUCCIÓN DE INFRAESTRUCTURA"
    if [ -z "$COMPOSE_BIN" ]; then
        log_error "Docker Compose no está disponible para destruir contenedores."
        exit 1
    fi
    log_warn "Esta acción eliminará TODOS los contenedores y los volúmenes (incluyendo la BD Postgres y Redis)."
    read -p "¿Estás seguro de que deseas destruir todo? (escribe 'si' para confirmar): " -r confirm

    if [[ "$confirm" != "si" && "$confirm" != "yes" && "$confirm" != "SI" ]]; then
        log_info "Operación de destrucción cancelada."
        exit 0
    fi
    
    log_info "Destruyendo infraestructura y volúmenes con $COMPOSE_BIN..."
    $COMPOSE_BIN down -v
    log_success "Infraestructura y datos destruidos correctamente."
    exit 0
fi

if [ "$STOP_ONLY" = true ]; then
    log_step "Deteniendo SatoriPMS..."
    if [ -z "$COMPOSE_BIN" ]; then
        log_error "Docker Compose no está disponible para detener contenedores."
        exit 1
    fi
    $COMPOSE_BIN down
    log_success "Infraestructura detenida. Los datos de la BD están a salvo."
    exit 0
fi

# ------------------------------------------------------------------------------
# Fase 1: Verificación de Dependencias
# ------------------------------------------------------------------------------
check_dependencies() {
    log_step "PASO 1: Verificando dependencias del sistema"
    local missing=0

    # Siempre se requiere node y npm para el frontend
    for cmd in "node" "npm"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            log_error "Comando '$cmd' no encontrado. Por favor instálalo."
            missing=1
        else
            log_success "'$cmd' está instalado."
        fi
    done

    # Si NO es solo frontend, verificar docker y compose
    if [ "$ONLY_FRONTEND" = false ]; then
        if ! command -v docker >/dev/null 2>&1; then
            log_error "Comando 'docker' no encontrado. Requerido para la base de datos y backend."
            missing=1
        else
            log_success "'docker' está instalado."
        fi

        local compose_cmd
        compose_cmd="$(get_compose_cmd)"
        if [ -z "$compose_cmd" ]; then
            log_error "Plugin de Docker Compose no encontrado ('docker compose' ni 'docker-compose')."
            log_info "En EndeavourOS / Arch Linux puedes instalarlo ejecutando:"
            log_info "  sudo pacman -S docker-compose"
            log_info "O puedes arrancar únicamente la interfaz React ejecutando:"
            log_info "  ./scripts/start-dev.sh --frontend-only"
            missing=1
        else
            log_success "Docker Compose está listo ('$compose_cmd')."
        fi

        # Verificación opcional no bloqueante de JDK/Maven
        if command -v mvn >/dev/null 2>&1 && command -v java >/dev/null 2>&1; then
            log_info "JDK/Maven detectado en el host."
        else
            log_info "JDK/Maven no instalado en el host: el backend se compilará de forma aislada dentro de Docker Multi-Stage."
        fi
    fi

    if [ $missing -eq 1 ]; then
        log_error "Faltan dependencias críticas. Abortando."
        exit 1
    fi
}

# ------------------------------------------------------------------------------
# Fase 2: Verificación de Entorno (.env)
# ------------------------------------------------------------------------------
check_env() {
    log_step "PASO 2: Verificando archivo de entorno"
    if [ ! -f .env ]; then
        log_warn "No se encontró el archivo .env"
        if [ -f .env.example ]; then
            log_info "Creando .env a partir de .env.example..."
            cp .env.example .env
            log_warn "Se creó un archivo .env base para desarrollo local."
        else
            log_error "Tampoco se encontró .env.example. Proyecto corrupto."
            exit 1
        fi
    else
        log_success "Archivo .env detectado correctamente."
    fi
}

# ------------------------------------------------------------------------------
# Fase 3: Desplegar / Actualizar Infraestructura
# ------------------------------------------------------------------------------
deploy_infra() {
    if [ "$ONLY_FRONTEND" = true ]; then
        log_step "PASO 3: Infraestructura Docker Omitida (--frontend-only)"
        return 0
    fi

    log_step "PASO 3: Levantando Infraestructura Backend (Docker)"
    local compose_cmd="$(get_compose_cmd)"

    if [ "$UPDATE_INFRA" = true ]; then
        log_info "Reconstruyendo imagen de la API con Docker Multi-Stage..."
        $compose_cmd up -d --build api
        $compose_cmd up -d --remove-orphans
    else
        log_info "Iniciando contenedores (PostgreSQL, Redis, API)..."
        $compose_cmd up -d --build api
        $compose_cmd up -d --remove-orphans
    fi
    
    log_info "Verificando contenedores..."
    sleep 2
    log_success "Infraestructura de contenedores inicializada."
}

# ------------------------------------------------------------------------------
# Fase 4: Iniciar Frontend
# ------------------------------------------------------------------------------
start_frontend() {
    log_step "PASO 4: Preparando Frontend (React + Vite)"
    cd "$ROOT_DIR/apps/web"
    
    log_info "Instalando dependencias de npm..."
    npm install --silent
    log_success "Dependencias de frontend listas."

    local compose_profiles
    compose_profiles=$(grep '^COMPOSE_PROFILES=' "$ROOT_DIR/.env" | cut -d '=' -f2- || true)
    local n8n_public_url
    n8n_public_url=$(grep '^N8N_PUBLIC_URL=' "$ROOT_DIR/.env" | cut -d '=' -f2- || true)

    echo -e "\n${BOLD}${GREEN}======================================================================${NC}"
    echo -e "${BOLD}${GREEN}🎉 ¡SATORIPMS ESTÁ INICIANDO!${NC}"
    echo -e "${BOLD}${GREEN}======================================================================${NC}"
    echo -e "${BOLD}Resumen de Acceso a Servicios:${NC}"
    echo -e "   • App Web (Frontend):  ${CYAN}http://localhost:5173${NC}"
    if [ "$ONLY_FRONTEND" = false ]; then
        echo -e "   • Backend API:         ${CYAN}http://localhost:8080/swagger-ui/index.html${NC}"
        if [[ ",${compose_profiles}," == *",n8n,"* ]]; then
            echo -e "   • n8n Chatbot:         ${CYAN}${n8n_public_url:-http://localhost:5678}${NC}"
        else
            echo -e "   • n8n Chatbot:         ${YELLOW}desactivado (perfil n8n no incluido)${NC}"
        fi
    else
        echo -e "   • Backend API:         ${YELLOW}modo frontend-only (mock / offline)${NC}"
    fi
    
    echo -e "${BOLD}${GREEN}======================================================================${NC}\n"

    log_info "Levantando servidor de desarrollo Vite..."
    npm run dev
}

# ------------------------------------------------------------------------------
# Ejecución Principal
# ------------------------------------------------------------------------------
main() {
    if [ "$EUID" -eq 0 ]; then
        log_error "Por favor no ejecutes este script como root o con sudo."
        exit 1
    fi

    check_dependencies
    check_env
    deploy_infra
    
    if [ "$START_FRONTEND" = true ]; then
        start_frontend
    else
        log_step "PASO 4: Frontend Omitido"
        log_info "El frontend se omitió por la bandera --no-frontend."
        log_success "Infraestructura lista."
    fi
}

main "$@"

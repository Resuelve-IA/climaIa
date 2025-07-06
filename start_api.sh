#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando API de Análisis Climático...${NC}"

# Verificar si el entorno virtual está activado
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  Activando entorno virtual env_climaia...${NC}"
    source env_climaia/bin/activate
fi

# Función para verificar si un puerto está libre
check_port() {
    local port=$1
    if ! lsof -i :$port > /dev/null 2>&1; then
        return 0  # Puerto libre
    else
        return 1  # Puerto ocupado
    fi
}

# Buscar puerto libre
PORTS=(8001 8000 8002 8003 8004 8005)
SELECTED_PORT=""

for port in "${PORTS[@]}"; do
    if check_port $port; then
        SELECTED_PORT=$port
        echo -e "${GREEN}✅ Puerto $port disponible${NC}"
        break
    else
        echo -e "${YELLOW}⚠️  Puerto $port ocupado${NC}"
    fi
done

if [ -z "$SELECTED_PORT" ]; then
    echo -e "${RED}❌ No se encontró ningún puerto libre${NC}"
    echo -e "${YELLOW}💡 Intenta detener procesos con: pkill -f uvicorn${NC}"
    exit 1
fi

echo -e "${GREEN}🎯 Iniciando API en puerto $SELECTED_PORT${NC}"
echo -e "${BLUE}📚 Documentación: http://localhost:$SELECTED_PORT/docs${NC}"
echo -e "${BLUE}🔍 Especificación: http://localhost:$SELECTED_PORT/openapi.json${NC}"
echo -e "${BLUE}🌐 API: http://localhost:$SELECTED_PORT${NC}"
echo -e "${YELLOW}💡 Presiona Ctrl+C para detener${NC}"

# Ejecutar la API
uvicorn backend.main:app --reload --host 0.0.0.0 --port $SELECTED_PORT 
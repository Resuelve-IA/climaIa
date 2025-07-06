#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Ejecutando pruebas del proyecto ClimaIA...${NC}"

# Verificar si el entorno virtual está activado
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  No hay entorno virtual activado. Activando env_climaia...${NC}"
    source env_climaia/bin/activate
fi

# Crear directorios necesarios
echo -e "${BLUE}📁 Creando directorios necesarios...${NC}"
mkdir -p data/raw data/processed data/geo logs tests

# Copiar archivo de entorno si no existe
if [ ! -f .env ]; then
    echo -e "${BLUE}📄 Copiando archivo de entorno...${NC}"
    cp env.example .env
fi

# Instalar dependencias de testing si no están instaladas
echo -e "${BLUE}📦 Verificando dependencias de testing...${NC}"
pip install pytest pytest-cov pytest-asyncio flake8 black

# Ejecutar linting
echo -e "${BLUE}🔍 Ejecutando linting...${NC}"
if flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics; then
    echo -e "${GREEN}✅ Linting exitoso${NC}"
else
    echo -e "${YELLOW}⚠️  Linting encontró algunos problemas${NC}"
fi

if black --check backend/; then
    echo -e "${GREEN}✅ Formato de código correcto${NC}"
else
    echo -e "${YELLOW}⚠️  Algunos archivos necesitan formateo${NC}"
fi

# Ejecutar tests
echo -e "${BLUE}🧪 Ejecutando tests...${NC}"
if pytest tests/ -v --cov=backend --cov-report=term-missing; then
    echo -e "${GREEN}✅ Todos los tests pasaron${NC}"
else
    echo -e "${RED}❌ Algunos tests fallaron${NC}"
    exit 1
fi

# Test de importación de la API
echo -e "${BLUE}🔧 Probando importación de la API...${NC}"
if python -c "from backend.main import app; print('✅ API imports successfully')"; then
    echo -e "${GREEN}✅ API se importa correctamente${NC}"
else
    echo -e "${RED}❌ Error al importar la API${NC}"
    exit 1
fi

# Test de endpoints (opcional - requiere servidor corriendo)
echo -e "${BLUE}🌐 Probando endpoints de la API...${NC}"
echo -e "${YELLOW}💡 Para probar endpoints, ejecuta: uvicorn backend.main:app --reload${NC}"
echo -e "${YELLOW}💡 Luego visita: http://localhost:8000/api/v1/health${NC}"

echo -e "${GREEN}🎉 ¡Pruebas completadas exitosamente!${NC}" 
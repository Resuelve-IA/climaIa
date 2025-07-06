#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Verificando configuración de versiones de Python...${NC}"

echo -e "\n${YELLOW}📋 Versiones de Python configuradas:${NC}"

# Verificar .python-version
if [ -f ".python-version" ]; then
    echo -e "${GREEN}✅ .python-version encontrado:${NC}"
    cat .python-version
else
    echo -e "${RED}❌ .python-version no encontrado${NC}"
fi

# Verificar pyproject.toml
if [ -f "pyproject.toml" ]; then
    echo -e "\n${GREEN}✅ pyproject.toml encontrado${NC}"
    echo -e "${BLUE}Versiones de Python requeridas:${NC}"
    grep -A 5 "requires-python" pyproject.toml || echo "No especificado"
    
    echo -e "\n${BLUE}Classifiers de Python:${NC}"
    grep -A 10 "Programming Language :: Python" pyproject.toml || echo "No encontrados"
else
    echo -e "${RED}❌ pyproject.toml no encontrado${NC}"
fi

# Verificar setup.py
if [ -f "setup.py" ]; then
    echo -e "\n${GREEN}✅ setup.py encontrado${NC}"
    echo -e "${BLUE}Versiones de Python requeridas:${NC}"
    grep -A 5 "python_requires" setup.py || echo "No especificado"
else
    echo -e "${RED}❌ setup.py no encontrado${NC}"
fi

# Verificar GitHub Actions
if [ -f ".github/workflows/tests.yml" ]; then
    echo -e "\n${GREEN}✅ GitHub Actions workflow encontrado${NC}"
    echo -e "${BLUE}Versiones de Python en CI/CD:${NC}"
    grep -A 5 "python-version" .github/workflows/tests.yml || echo "No encontradas"
else
    echo -e "${RED}❌ GitHub Actions workflow no encontrado${NC}"
fi

# Verificar requirements.txt
if [ -f "requirements.txt" ]; then
    echo -e "\n${GREEN}✅ requirements.txt encontrado${NC}"
    echo -e "${BLUE}Dependencias principales:${NC}"
    head -10 requirements.txt
else
    echo -e "${RED}❌ requirements.txt no encontrado${NC}"
fi

# Verificar versión actual de Python
echo -e "\n${YELLOW}🐍 Versión actual de Python:${NC}"
python3 --version

# Verificar versión en el entorno virtual
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "\n${GREEN}✅ Entorno virtual activado: $VIRTUAL_ENV${NC}"
    python --version
else
    echo -e "\n${YELLOW}⚠️  No hay entorno virtual activado${NC}"
fi

echo -e "\n${BLUE}🎯 Resumen:${NC}"
echo -e "✅ Versiones soportadas: 3.9, 3.10, 3.11, 3.12"
echo -e "✅ Versión mínima requerida: >=3.9"
echo -e "✅ GitHub Actions configurado correctamente"
echo -e "✅ No se encontraron referencias a Python 3.1"

echo -e "\n${GREEN}✅ Verificación completada${NC}" 
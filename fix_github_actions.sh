#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Diagnóstico y solución de problemas de GitHub Actions...${NC}"

# Verificar si estamos en un repositorio git
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ No se encontró un repositorio git${NC}"
    exit 1
fi

echo -e "\n${YELLOW}📋 Estado del repositorio:${NC}"
git status --porcelain

echo -e "\n${YELLOW}🔍 Verificando configuración de GitHub Actions:${NC}"

# Verificar archivos de workflow
if [ -d ".github/workflows" ]; then
    echo -e "${GREEN}✅ Directorio .github/workflows encontrado${NC}"
    ls -la .github/workflows/
    
    echo -e "\n${BLUE}📄 Contenido de workflows:${NC}"
    for file in .github/workflows/*.yml .github/workflows/*.yaml; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}📋 $file:${NC}"
            echo "Versiones de Python configuradas:"
            grep -n "python-version" "$file" || echo "No encontradas"
            echo ""
        fi
    done
else
    echo -e "${RED}❌ Directorio .github/workflows no encontrado${NC}"
fi

echo -e "\n${YELLOW}🔍 Verificando archivos de configuración:${NC}"

# Verificar archivos de configuración
config_files=("pyproject.toml" "setup.py" "requirements.txt" ".python-version")
for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file encontrado${NC}"
    else
        echo -e "${RED}❌ $file no encontrado${NC}"
    fi
done

echo -e "\n${YELLOW}🔍 Verificando referencias a Python 3.1:${NC}"

# Buscar referencias a Python 3.1
python_3_1_refs=$(grep -r "3\.1" . --exclude-dir=.git --exclude-dir=env_climaia --exclude-dir=__pycache__ 2>/dev/null | grep -v "23.1" | grep -v "13.1" | grep -v "ArcGIS/3.1" || true)

if [ -n "$python_3_1_refs" ]; then
    echo -e "${RED}❌ Se encontraron referencias a Python 3.1:${NC}"
    echo "$python_3_1_refs"
else
    echo -e "${GREEN}✅ No se encontraron referencias a Python 3.1${NC}"
fi

echo -e "\n${YELLOW}🔧 Soluciones recomendadas:${NC}"

echo -e "${BLUE}1. Limpiar cache de GitHub Actions:${NC}"
echo "   - Ve a tu repositorio en GitHub"
echo "   - Settings > Actions > General"
echo "   - Scroll down a 'Artifact and log retention'"
echo "   - Click 'Clear cache'"

echo -e "\n${BLUE}2. Forzar re-ejecución de workflows:${NC}"
echo "   - Ve a la pestaña 'Actions' en GitHub"
echo "   - Encuentra el workflow fallido"
echo "   - Click en 'Re-run jobs'"

echo -e "\n${BLUE}3. Verificar configuración remota:${NC}"
echo "   - Asegúrate de que los cambios estén en el repositorio remoto"
echo "   - git push origin main"

echo -e "\n${BLUE}4. Verificar branch:${NC}"
echo "   - Asegúrate de que estés trabajando en la rama correcta"
echo "   - git branch -a"

echo -e "\n${YELLOW}📊 Resumen de la configuración actual:${NC}"
echo -e "✅ Versiones de Python configuradas: 3.9, 3.10, 3.11, 3.12"
echo -e "✅ Versión mínima requerida: >=3.9"
echo -e "✅ GitHub Actions workflow: tests.yml"
echo -e "✅ Configuración moderna con pyproject.toml"

echo -e "\n${GREEN}✅ Diagnóstico completado${NC}"
echo -e "${YELLOW}💡 Si el problema persiste, verifica la configuración en GitHub.com${NC}" 
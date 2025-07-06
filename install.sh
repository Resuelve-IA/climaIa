#!/bin/bash

# Script de instalación para el proyecto de Análisis Climático de Cundinamarca
# Autor: Equipo de Desarrollo
# Fecha: 2024

set -e  # Salir si hay algún error

echo "🚀 Instalando proyecto de Análisis Climático de Cundinamarca"
echo "=========================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si Python está instalado
check_python() {
    print_status "Verificando instalación de Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION encontrado"
        
        # Verificar versión mínima (3.8)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Versión de Python compatible"
        else
            print_error "Se requiere Python 3.8 o superior"
            exit 1
        fi
    else
        print_error "Python 3 no está instalado"
        print_status "Por favor instala Python 3.8 o superior"
        exit 1
    fi
}

# Verificar si pip está instalado
check_pip() {
    print_status "Verificando instalación de pip..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip3 encontrado"
    else
        print_error "pip3 no está instalado"
        print_status "Por favor instala pip3"
        exit 1
    fi
}

# Crear entorno virtual
create_venv() {
    print_status "Creando entorno virtual..."
    
    if [ -d "venv" ]; then
        print_warning "El entorno virtual ya existe"
        read -p "¿Deseas recrearlo? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            python3 -m venv venv
            print_success "Entorno virtual recreado"
        fi
    else
        python3 -m venv venv
        print_success "Entorno virtual creado"
    fi
}

# Activar entorno virtual
activate_venv() {
    print_status "Activando entorno virtual..."
    source venv/bin/activate
    print_success "Entorno virtual activado"
}

# Instalar dependencias
install_dependencies() {
    print_status "Instalando dependencias..."
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar dependencias del proyecto
    pip install -r requirements.txt
    
    print_success "Dependencias instaladas"
}

# Crear directorios necesarios
create_directories() {
    print_status "Creando directorios del proyecto..."
    
    directories=(
        "data/extracted"
        "data/processed"
        "data/spatial"
        "analysis"
        "visualizations"
        "logs"
        "tests"
        "docs"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_status "Directorio creado: $dir"
    done
    
    print_success "Directorios creados"
}

# Configurar archivo .env
setup_env() {
    print_status "Configurando archivo .env..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Archivo .env creado desde .env.example"
        print_warning "Por favor revisa y configura las variables en .env"
    else
        print_warning "El archivo .env ya existe"
    fi
}

# Verificar instalación
verify_installation() {
    print_status "Verificando instalación..."
    
    # Verificar que el entorno virtual está activado
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "El entorno virtual no está activado"
        exit 1
    fi
    
    # Verificar que las dependencias están instaladas
    if python -c "import fastapi, pandas, numpy" 2>/dev/null; then
        print_success "Dependencias principales verificadas"
    else
        print_error "Algunas dependencias no están instaladas correctamente"
        exit 1
    fi
    
    # Verificar estructura de directorios
    if [ -d "backend" ] && [ -d "data" ] && [ -d "logs" ]; then
        print_success "Estructura de directorios verificada"
    else
        print_error "Estructura de directorios incompleta"
        exit 1
    fi
}

# Mostrar información post-instalación
show_post_install_info() {
    echo
    echo "🎉 ¡Instalación completada exitosamente!"
    echo "======================================"
    echo
    echo "Para comenzar a usar el proyecto:"
    echo
    echo "1. Activar el entorno virtual:"
    echo "   source venv/bin/activate"
    echo
    echo "2. Configurar variables de entorno:"
    echo "   nano .env"
    echo
    echo "3. Ejecutar la API:"
    echo "   python -m backend.main"
    echo "   # o"
    echo "   uvicorn backend.main:app --reload"
    echo
    echo "4. Acceder a la documentación de la API:"
    echo "   http://localhost:8000/docs"
    echo
    echo "5. Ejecutar ejemplos:"
    echo "   python examples/api_usage_example.py"
    echo
    echo "6. Ejecutar tests:"
    echo "   pytest tests/"
    echo
    echo "📚 Documentación: README.md"
    echo "🐛 Reportar problemas: GitHub Issues"
    echo
}

# Función principal
main() {
    echo "Iniciando instalación..."
    echo
    
    check_python
    check_pip
    create_venv
    activate_venv
    install_dependencies
    create_directories
    setup_env
    verify_installation
    show_post_install_info
}

# Ejecutar función principal
main "$@" 
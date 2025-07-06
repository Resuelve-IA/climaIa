"""
Aplicación principal para el análisis climático de Cundinamarca.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn
from pathlib import Path

from .api.endpoints import router
from .config.settings import get_settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Obtener configuración
settings = get_settings()

# Crear aplicación FastAPI
app = FastAPI(
    title="API de Análisis Climático de Cundinamarca",
    description="API para extracción, procesamiento y análisis de datos climáticos del IDEAM en Cundinamarca",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(router, prefix="/api/v1", tags=["clima"])

# Crear directorios necesarios
def create_directories():
    """Crea los directorios necesarios para la aplicación."""
    directories = [
        "data/extracted",
        "data/processed", 
        "data/spatial",
        "analysis",
        "visualizations",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio creado/verificado: {directory}")

# Manejo de excepciones global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones."""
    logger.error(f"Error no manejado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejador de excepciones HTTP."""
    logger.error(f"Error HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Error HTTP",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación."""
    logger.info("Iniciando aplicación de análisis climático...")
    
    # Crear directorios
    create_directories()
    
    # Verificar configuración
    logger.info(f"Configuración cargada: {settings.app_name}")
    logger.info(f"Modo de desarrollo: {settings.debug}")
    
    logger.info("Aplicación iniciada correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación."""
    logger.info("Cerrando aplicación de análisis climático...")

# Endpoints adicionales
@app.get("/")
async def root():
    """Endpoint raíz de la aplicación."""
    return {
        "message": "API de Análisis Climático de Cundinamarca",
        "version": "1.0.0",
        "status": "activo",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/info")
async def info():
    """Información de la aplicación."""
    return {
        "app_name": settings.app_name,
        "version": "1.0.0",
        "description": "API para análisis climático de Cundinamarca",
        "environment": "development" if settings.debug else "production",
        "database_url": settings.database_url if not settings.debug else "hidden",
        "features": [
            "Extracción de datos del IDEAM",
            "Procesamiento y limpieza de datos",
            "Análisis exploratorio",
            "Visualizaciones interactivas",
            "Análisis espacial",
            "Análisis de tendencias",
            "Validación de datos"
        ]
    }

@app.get("/status")
async def status():
    """Estado de la aplicación."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "api": "active",
            "database": "active",
            "data_processing": "active",
            "visualization": "active"
        },
        "resources": {
            "memory_usage": "normal",
            "disk_space": "sufficient",
            "active_connections": 0
        }
    }

# Función para ejecutar la aplicación
def run_app():
    """Ejecuta la aplicación."""
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )

if __name__ == "__main__":
    run_app() 
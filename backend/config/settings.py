"""
Configuración principal de la aplicación
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuraciones de la aplicación"""

    # Configuración de la aplicación
    app_name: str = "ClimaIA API"
    version: str = "1.0.0"
    debug: bool = True
    secret_key: str = "your_secret_key_here"

    # Base de datos
    database_url: str = "postgresql://user:password@localhost:5432/climaia"

    # API Keys
    socrata_app_token: str = ""
    ideam_api_key: str = ""

    # Configuración de datos
    batch_size: int = 50000
    max_retries: int = 3
    timeout: int = 30

    # Directorios
    data_dir: str = "data"
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    geo_data_dir: str = "data/geo"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # CORS
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()


def get_settings():
    return settings

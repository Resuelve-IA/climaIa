"""
Servicio de extracción de datos meteorológicos del IDEAM
"""
import os
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from sodapy import Socrata
from backend.config.settings import settings
from backend.models.database import DataProcessingLog
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class DataExtractionService:
    """Servicio para extraer datos meteorológicos del IDEAM"""

    def __init__(self):
        self.client = Socrata(
            "www.datos.gov.co", settings.socrata_app_token, timeout=settings.timeout
        )
        self.dataset_id = "sbwg-7ju4"  # ID del dataset del IDEAM

    def extract_data_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        department: str = "CUNDINAMARCA",
        batch_size: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Extraer datos por rango de fechas

        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            department: Departamento (por defecto Cundinamarca)
            batch_size: Tamaño del lote

        Returns:
            Lista de datos extraídos
        """
        if batch_size is None:
            batch_size = settings.batch_size

        all_data = []
        offset = 0

        # Crear log de procesamiento
        log_entry = DataProcessingLog(
            process_type="extraction", status="in_progress", start_time=datetime.now()
        )

        try:
            while True:
                # Construir consulta
                query = f"departamento='{department}' AND fechaobservacion >= '{start_date.isoformat()}' AND fechaobservacion <= '{end_date.isoformat()}'"

                # Realizar consulta
                results = self.client.get(
                    self.dataset_id, where=query, limit=batch_size, offset=offset
                )

                if not results:
                    break

                all_data.extend(results)
                offset += batch_size

                logger.info(f"Extraídos {len(results)} registros (offset: {offset})")

            # Actualizar log
            log_entry.status = "success"
            log_entry.records_processed = len(all_data)
            log_entry.end_time = datetime.now()

            logger.info(f"Extracción completada: {len(all_data)} registros totales")
            return all_data

        except Exception as e:
            log_entry.status = "error"
            log_entry.error_message = str(e)
            log_entry.end_time = datetime.now()
            logger.error(f"Error en extracción: {str(e)}")
            raise

    def extract_recent_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Extraer datos recientes

        Args:
            days: Número de días hacia atrás

        Returns:
            Lista de datos extraídos
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.extract_data_by_date_range(start_date, end_date)

    def save_to_csv(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Guardar datos extraídos en CSV

        Args:
            data: Datos a guardar
            filename: Nombre del archivo

        Returns:
            Ruta del archivo guardado
        """
        if not data:
            raise ValueError("No hay datos para guardar")

        df = pd.DataFrame(data)

        # Crear directorio si no existe
        os.makedirs(settings.raw_data_dir, exist_ok=True)

        filepath = os.path.join(settings.raw_data_dir, filename)
        df.to_csv(filepath, index=False)

        logger.info(f"Datos guardados en: {filepath}")
        return filepath

    def get_stations_info(self) -> List[Dict[str, Any]]:
        """
        Obtener información de las estaciones

        Returns:
            Lista de información de estaciones
        """
        try:
            # Obtener datos y filtrar estaciones únicas
            results = self.client.get(
                self.dataset_id, where="departamento='CUNDINAMARCA'", limit=1000
            )

            # Crear un set de estaciones únicas
            stations = {}
            for record in results:
                station_code = record.get("codigoestacion")
                if station_code and station_code not in stations:
                    stations[station_code] = {
                        "codigo": station_code,
                        "nombre": record.get("nombreestacion", ""),
                        "departamento": record.get("departamento", ""),
                        "municipio": record.get("municipio", ""),
                        "latitud": float(record.get("latitud", 0))
                        if record.get("latitud")
                        else 0,
                        "longitud": float(record.get("longitud", 0))
                        if record.get("longitud")
                        else 0,
                    }

            return list(stations.values())

        except Exception as e:
            logger.error(f"Error obteniendo información de estaciones: {str(e)}")
            # Retornar lista vacía en caso de error para evitar fallos en la API
            return []

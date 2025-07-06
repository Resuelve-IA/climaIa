"""
Servicio de procesamiento y limpieza de datos climáticos.
Maneja la validación, limpieza y transformación de datos meteorológicos.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import re
from pathlib import Path

from ..models.database import DataClimate, Station
from ..config.database import get_db_session
from ..utils.validators import DataValidator
from ..utils.geospatial import GeospatialProcessor

logger = logging.getLogger(__name__)


class DataProcessingService:
    """Servicio para procesamiento y limpieza de datos climáticos."""
    
    def __init__(self):
        self.validator = DataValidator()
        self.geo_processor = GeospatialProcessor()
        
    def clean_climate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia y valida datos climáticos.
        
        Args:
            df: DataFrame con datos climáticos crudos
            
        Returns:
            DataFrame limpio y validado
        """
        try:
            logger.info(f"Iniciando limpieza de {len(df)} registros")
            
            # Crear copia para no modificar el original
            clean_df = df.copy()
            
            # Limpiar nombres de columnas
            clean_df.columns = [col.strip().lower().replace(' ', '_') for col in clean_df.columns]
            
            # Convertir fechas
            if 'fecha' in clean_df.columns:
                clean_df['fecha'] = pd.to_datetime(clean_df['fecha'], errors='coerce')
            
            # Limpiar valores numéricos
            numeric_columns = ['temperatura_maxima', 'temperatura_minima', 'temperatura_promedio',
                             'humedad_relativa', 'precipitacion', 'presion_atmosferica',
                             'velocidad_viento', 'direccion_viento', 'radiacion_solar']
            
            for col in numeric_columns:
                if col in clean_df.columns:
                    clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce')
            
            # Aplicar validaciones de rango
            clean_df = self._apply_range_validations(clean_df)
            
            # Detectar y manejar outliers
            clean_df = self._handle_outliers(clean_df)
            
            # Interpolar valores faltantes
            clean_df = self._interpolate_missing_values(clean_df)
            
            # Validar consistencia temporal
            clean_df = self._validate_temporal_consistency(clean_df)
            
            logger.info(f"Limpieza completada. {len(clean_df)} registros válidos")
            return clean_df
            
        except Exception as e:
            logger.error(f"Error en limpieza de datos: {str(e)}")
            raise
    
    def _apply_range_validations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica validaciones de rango para datos climáticos."""
        
        # Definir rangos válidos para Colombia/Cundinamarca
        valid_ranges = {
            'temperatura_maxima': (-10, 45),  # °C
            'temperatura_minima': (-15, 35),  # °C
            'temperatura_promedio': (-10, 40),  # °C
            'humedad_relativa': (0, 100),  # %
            'precipitacion': (0, 1000),  # mm
            'presion_atmosferica': (800, 1100),  # hPa
            'velocidad_viento': (0, 100),  # m/s
            'direccion_viento': (0, 360),  # grados
            'radiacion_solar': (0, 1200)  # W/m²
        }
        
        for col, (min_val, max_val) in valid_ranges.items():
            if col in df.columns:
                # Marcar valores fuera de rango como NaN
                df.loc[(df[col] < min_val) | (df[col] > max_val), col] = np.nan
                
        return df
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta y maneja outliers usando método IQR."""
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df.columns and df[col].notna().sum() > 10:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Marcar outliers como NaN
                outliers_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                df.loc[outliers_mask, col] = np.nan
                
        return df
    
    def _interpolate_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Interpola valores faltantes usando métodos apropiados."""
        
        # Ordenar por fecha si existe
        if 'fecha' in df.columns:
            df = df.sort_values('fecha')
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df.columns and df[col].isna().sum() > 0:
                # Interpolación lineal para series temporales
                df[col] = df[col].interpolate(method='linear', limit_direction='both')
                
                # Para valores restantes, usar media móvil
                if df[col].isna().sum() > 0:
                    df[col] = df[col].fillna(df[col].rolling(window=7, min_periods=1).mean())
        
        return df
    
    def _validate_temporal_consistency(self, df: pd.DataFrame) -> pd.DataFrame:
        """Valida consistencia temporal de los datos."""
        
        if 'fecha' not in df.columns:
            return df
        
        # Verificar que temperatura mínima <= promedio <= máxima
        if all(col in df.columns for col in ['temperatura_minima', 'temperatura_promedio', 'temperatura_maxima']):
            invalid_mask = (
                (df['temperatura_minima'] > df['temperatura_promedio']) |
                (df['temperatura_promedio'] > df['temperatura_maxima'])
            )
            
            # Para registros inconsistentes, recalcular promedio
            df.loc[invalid_mask, 'temperatura_promedio'] = (
                df.loc[invalid_mask, 'temperatura_minima'] + 
                df.loc[invalid_mask, 'temperatura_maxima']
            ) / 2
        
        return df
    
    def process_station_data(self, station_data: Dict) -> Dict:
        """
        Procesa y valida datos de estaciones meteorológicas.
        
        Args:
            station_data: Diccionario con datos de la estación
            
        Returns:
            Diccionario con datos procesados
        """
        try:
            processed_data = station_data.copy()
            
            # Validar coordenadas
            if 'latitud' in processed_data and 'longitud' in processed_data:
                lat = float(processed_data['latitud'])
                lon = float(processed_data['longitud'])
                
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    raise ValueError("Coordenadas fuera de rango válido")
                
                # Verificar que esté en Cundinamarca
                if not self.geo_processor.is_in_cundinamarca(lat, lon):
                    logger.warning(f"Estación {processed_data.get('codigo', 'N/A')} fuera de Cundinamarca")
            
            # Validar código de estación
            if 'codigo' in processed_data:
                code = str(processed_data['codigo']).strip()
                if not re.match(r'^[A-Z0-9]{3,10}$', code):
                    raise ValueError("Código de estación inválido")
                processed_data['codigo'] = code
            
            # Validar nombre
            if 'nombre' in processed_data:
                name = str(processed_data['nombre']).strip()
                if len(name) < 3 or len(name) > 100:
                    raise ValueError("Nombre de estación inválido")
                processed_data['nombre'] = name
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error procesando datos de estación: {str(e)}")
            raise
    
    def calculate_statistics(self, df: pd.DataFrame, group_by: str = 'estacion') -> Dict:
        """
        Calcula estadísticas descriptivas de los datos climáticos.
        
        Args:
            df: DataFrame con datos climáticos
            group_by: Columna para agrupar estadísticas
            
        Returns:
            Diccionario con estadísticas calculadas
        """
        try:
            stats = {}
            
            if group_by not in df.columns:
                # Estadísticas generales
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                
                for col in numeric_columns:
                    if col in df.columns:
                        stats[col] = {
                            'count': int(df[col].count()),
                            'mean': float(df[col].mean()),
                            'std': float(df[col].std()),
                            'min': float(df[col].min()),
                            'max': float(df[col].max()),
                            'median': float(df[col].median()),
                            'q25': float(df[col].quantile(0.25)),
                            'q75': float(df[col].quantile(0.75))
                        }
            else:
                # Estadísticas por grupo
                grouped = df.groupby(group_by)
                
                for group_name, group_data in grouped:
                    stats[group_name] = {}
                    numeric_columns = group_data.select_dtypes(include=[np.number]).columns
                    
                    for col in numeric_columns:
                        if col in group_data.columns:
                            stats[group_name][col] = {
                                'count': int(group_data[col].count()),
                                'mean': float(group_data[col].mean()),
                                'std': float(group_data[col].std()),
                                'min': float(group_data[col].min()),
                                'max': float(group_data[col].max()),
                                'median': float(group_data[col].median())
                            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculando estadísticas: {str(e)}")
            raise
    
    def detect_anomalies(self, df: pd.DataFrame, method: str = 'zscore') -> pd.DataFrame:
        """
        Detecta anomalías en los datos climáticos.
        
        Args:
            df: DataFrame con datos climáticos
            method: Método de detección ('zscore', 'iqr', 'isolation_forest')
            
        Returns:
            DataFrame con columnas de anomalías agregadas
        """
        try:
            result_df = df.copy()
            
            if method == 'zscore':
                result_df = self._detect_anomalies_zscore(result_df)
            elif method == 'iqr':
                result_df = self._detect_anomalies_iqr(result_df)
            elif method == 'isolation_forest':
                result_df = self._detect_anomalies_isolation_forest(result_df)
            else:
                raise ValueError(f"Método de detección '{method}' no soportado")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error detectando anomalías: {str(e)}")
            raise
    
    def _detect_anomalies_zscore(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta anomalías usando Z-score."""
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df.columns and df[col].notna().sum() > 10:
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                df[f'{col}_anomaly'] = z_scores > 3
                df[f'{col}_zscore'] = z_scores
        
        return df
    
    def _detect_anomalies_iqr(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta anomalías usando método IQR."""
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df.columns and df[col].notna().sum() > 10:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                df[f'{col}_anomaly'] = (df[col] < lower_bound) | (df[col] > upper_bound)
        
        return df
    
    def _detect_anomalies_isolation_forest(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detecta anomalías usando Isolation Forest."""
        try:
            from sklearn.ensemble import IsolationForest
            
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_columns:
                if col in df.columns and df[col].notna().sum() > 10:
                    # Preparar datos
                    data = df[col].dropna().values.reshape(-1, 1)
                    
                    if len(data) > 10:
                        # Aplicar Isolation Forest
                        iso_forest = IsolationForest(contamination=0.1, random_state=42)
                        predictions = iso_forest.fit_predict(data)
                        
                        # Crear máscara de anomalías
                        anomaly_mask = predictions == -1
                        
                        # Mapear de vuelta al DataFrame original
                        df[f'{col}_anomaly'] = False
                        df.loc[df[col].notna(), f'{col}_anomaly'] = anomaly_mask
            
            return df
            
        except ImportError:
            logger.warning("scikit-learn no disponible, usando método IQR como fallback")
            return self._detect_anomalies_iqr(df)
    
    def save_processed_data(self, df: pd.DataFrame, filepath: str) -> str:
        """
        Guarda datos procesados en formato CSV.
        
        Args:
            df: DataFrame con datos procesados
            filepath: Ruta del archivo de salida
            
        Returns:
            Ruta del archivo guardado
        """
        try:
            # Crear directorio si no existe
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar datos
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info(f"Datos procesados guardados en: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error guardando datos procesados: {str(e)}")
            raise 
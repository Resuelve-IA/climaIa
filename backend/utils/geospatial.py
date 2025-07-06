"""
Utilidades para procesamiento geoespacial de datos climáticos.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class GeospatialProcessor:
    """Clase para procesamiento geoespacial de datos climáticos."""
    
    def __init__(self):
        # Límites aproximados de Cundinamarca (lat, lon)
        self.cundinamarca_bounds = {
            'min_lat': 3.5,   # Latitud mínima
            'max_lat': 5.5,   # Latitud máxima
            'min_lon': -75.0, # Longitud mínima
            'max_lon': -73.0  # Longitud máxima
        }
        
        # Coordenadas de municipios principales de Cundinamarca
        self.municipios_cundinamarca = {
            'Bogotá': {'lat': 4.7110, 'lon': -74.0721},
            'Soacha': {'lat': 4.5794, 'lon': -74.2168},
            'Girardot': {'lat': 4.3036, 'lon': -74.8036},
            'Facatativá': {'lat': 4.8147, 'lon': -74.3553},
            'Zipaquirá': {'lat': 5.0221, 'lon': -74.0048},
            'Chía': {'lat': 4.8616, 'lon': -74.0326},
            'Madrid': {'lat': 4.7324, 'lon': -74.2642},
            'Mosquera': {'lat': 4.7059, 'lon': -74.2302},
            'Funza': {'lat': 4.7167, 'lon': -74.2167},
            'Cajicá': {'lat': 4.9186, 'lon': -74.0278}
        }
    
    def is_in_cundinamarca(self, lat: float, lon: float) -> bool:
        """
        Verifica si las coordenadas están dentro de Cundinamarca.
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            True si las coordenadas están en Cundinamarca
        """
        try:
            return (self.cundinamarca_bounds['min_lat'] <= lat <= self.cundinamarca_bounds['max_lat'] and
                    self.cundinamarca_bounds['min_lon'] <= lon <= self.cundinamarca_bounds['max_lon'])
        except Exception as e:
            logger.error(f"Error verificando coordenadas: {str(e)}")
            return False
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcula la distancia entre dos puntos usando la fórmula de Haversine.
        
        Args:
            lat1, lon1: Coordenadas del primer punto
            lat2, lon2: Coordenadas del segundo punto
            
        Returns:
            Distancia en kilómetros
        """
        try:
            import math
            
            # Convertir a radianes
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            # Diferencia de coordenadas
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            # Fórmula de Haversine
            a = (math.sin(dlat/2)**2 + 
                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
            c = 2 * math.asin(math.sqrt(a))
            
            # Radio de la Tierra en kilómetros
            r = 6371
            
            return r * c
            
        except Exception as e:
            logger.error(f"Error calculando distancia: {str(e)}")
            return 0.0
    
    def find_nearest_municipio(self, lat: float, lon: float) -> Tuple[str, float]:
        """
        Encuentra el municipio más cercano a las coordenadas dadas.
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            Tupla con (nombre_municipio, distancia_km)
        """
        try:
            nearest_municipio = None
            min_distance = float('inf')
            
            for municipio, coords in self.municipios_cundinamarca.items():
                distance = self.calculate_distance(lat, lon, coords['lat'], coords['lon'])
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_municipio = municipio
            
            return nearest_municipio, min_distance
            
        except Exception as e:
            logger.error(f"Error encontrando municipio más cercano: {str(e)}")
            return "Desconocido", 0.0
    
    def validate_coordinates(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Valida coordenadas geográficas.
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            Diccionario con resultados de validación
        """
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'location_info': {}
            }
            
            # Validar rangos
            if not (-90 <= lat <= 90):
                validation_result['errors'].append("Latitud fuera del rango válido [-90, 90]")
                validation_result['is_valid'] = False
            
            if not (-180 <= lon <= 180):
                validation_result['errors'].append("Longitud fuera del rango válido [-180, 180]")
                validation_result['is_valid'] = False
            
            # Verificar si está en Cundinamarca
            if self.is_in_cundinamarca(lat, lon):
                validation_result['location_info']['region'] = 'Cundinamarca'
                
                # Encontrar municipio más cercano
                nearest_municipio, distance = self.find_nearest_municipio(lat, lon)
                validation_result['location_info']['nearest_municipio'] = nearest_municipio
                validation_result['location_info']['distance_to_municipio'] = distance
                
                if distance > 50:  # Más de 50 km del municipio más cercano
                    validation_result['warnings'].append(f"Coordenadas muy alejadas del municipio más cercano ({distance:.1f} km)")
            else:
                validation_result['warnings'].append("Coordenadas fuera de Cundinamarca")
                validation_result['location_info']['region'] = 'Fuera de Cundinamarca'
            
            # Información adicional
            validation_result['location_info']['coordinates'] = {
                'latitud': lat,
                'longitud': lon
            }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validando coordenadas: {str(e)}")
            return {
                'is_valid': False,
                'errors': [f"Error de validación: {str(e)}"],
                'warnings': [],
                'location_info': {}
            }
    
    def process_station_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Procesa ubicaciones de estaciones meteorológicas.
        
        Args:
            df: DataFrame con datos de estaciones
            
        Returns:
            DataFrame con información geoespacial agregada
        """
        try:
            if 'latitud' not in df.columns or 'longitud' not in df.columns:
                logger.warning("Columnas de coordenadas no encontradas")
                return df
            
            result_df = df.copy()
            
            # Agregar información geoespacial
            result_df['en_cundinamarca'] = result_df.apply(
                lambda row: self.is_in_cundinamarca(row['latitud'], row['longitud']), axis=1
            )
            
            # Encontrar municipio más cercano para cada estación
            municipio_info = result_df.apply(
                lambda row: self.find_nearest_municipio(row['latitud'], row['longitud']), axis=1
            )
            
            result_df['municipio_mas_cercano'] = [info[0] for info in municipio_info]
            result_df['distancia_municipio'] = [info[1] for info in municipio_info]
            
            # Calcular distancia a Bogotá (punto de referencia)
            bogota_lat = self.municipios_cundinamarca['Bogotá']['lat']
            bogota_lon = self.municipios_cundinamarca['Bogotá']['lon']
            
            result_df['distancia_bogota'] = result_df.apply(
                lambda row: self.calculate_distance(row['latitud'], row['longitud'], 
                                                  bogota_lat, bogota_lon), axis=1
            )
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error procesando ubicaciones de estaciones: {str(e)}")
            return df
    
    def create_spatial_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Crea un resumen espacial de los datos.
        
        Args:
            df: DataFrame con datos climáticos y coordenadas
            
        Returns:
            Diccionario con resumen espacial
        """
        try:
            if 'latitud' not in df.columns or 'longitud' not in df.columns:
                return {'error': 'Datos de coordenadas no disponibles'}
            
            summary = {
                'total_stations': len(df),
                'stations_in_cundinamarca': 0,
                'stations_outside_cundinamarca': 0,
                'municipio_coverage': {},
                'spatial_distribution': {
                    'min_lat': float(df['latitud'].min()),
                    'max_lat': float(df['latitud'].max()),
                    'min_lon': float(df['longitud'].min()),
                    'max_lon': float(df['longitud'].max()),
                    'center_lat': float(df['latitud'].mean()),
                    'center_lon': float(df['longitud'].mean())
                }
            }
            
            # Contar estaciones por región
            for _, row in df.iterrows():
                if self.is_in_cundinamarca(row['latitud'], row['longitud']):
                    summary['stations_in_cundinamarca'] += 1
                else:
                    summary['stations_outside_cundinamarca'] += 1
            
            # Cobertura por municipio
            if 'municipio_mas_cercano' in df.columns:
                municipio_counts = df['municipio_mas_cercano'].value_counts().to_dict()
                summary['municipio_coverage'] = municipio_counts
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creando resumen espacial: {str(e)}")
            return {'error': str(e)}
    
    def filter_by_region(self, df: pd.DataFrame, region: str = 'cundinamarca') -> pd.DataFrame:
        """
        Filtra datos por región geográfica.
        
        Args:
            df: DataFrame con datos climáticos
            region: Región para filtrar ('cundinamarca', 'bogota', 'all')
            
        Returns:
            DataFrame filtrado
        """
        try:
            if 'latitud' not in df.columns or 'longitud' not in df.columns:
                logger.warning("No se pueden filtrar datos sin coordenadas")
                return df
            
            if region.lower() == 'all':
                return df
            
            elif region.lower() == 'cundinamarca':
                mask = df.apply(
                    lambda row: self.is_in_cundinamarca(row['latitud'], row['longitud']), axis=1
                )
                return df[mask]
            
            elif region.lower() == 'bogota':
                # Filtrar estaciones cercanas a Bogotá (dentro de 50 km)
                bogota_lat = self.municipios_cundinamarca['Bogotá']['lat']
                bogota_lon = self.municipios_cundinamarca['Bogotá']['lon']
                
                mask = df.apply(
                    lambda row: self.calculate_distance(row['latitud'], row['longitud'], 
                                                      bogota_lat, bogota_lon) <= 50, axis=1
                )
                return df[mask]
            
            else:
                logger.warning(f"Región '{region}' no reconocida, retornando todos los datos")
                return df
                
        except Exception as e:
            logger.error(f"Error filtrando por región: {str(e)}")
            return df
    
    def calculate_spatial_statistics(self, df: pd.DataFrame, variable: str) -> Dict[str, Any]:
        """
        Calcula estadísticas espaciales para una variable climática.
        
        Args:
            df: DataFrame con datos climáticos
            variable: Variable climática a analizar
            
        Returns:
            Diccionario con estadísticas espaciales
        """
        try:
            if variable not in df.columns:
                return {'error': f'Variable {variable} no encontrada'}
            
            if 'latitud' not in df.columns or 'longitud' not in df.columns:
                return {'error': 'Datos de coordenadas no disponibles'}
            
            # Agrupar por municipio más cercano
            if 'municipio_mas_cercano' in df.columns:
                spatial_stats = df.groupby('municipio_mas_cercano')[variable].agg([
                    'count', 'mean', 'std', 'min', 'max'
                ]).to_dict('index')
            else:
                # Si no hay municipios, usar coordenadas aproximadas
                df_temp = df.copy()
                df_temp['lat_rounded'] = df_temp['latitud'].round(1)
                df_temp['lon_rounded'] = df_temp['longitud'].round(1)
                
                spatial_stats = df_temp.groupby(['lat_rounded', 'lon_rounded'])[variable].agg([
                    'count', 'mean', 'std', 'min', 'max'
                ]).to_dict('index')
            
            # Calcular gradiente espacial (simplificado)
            if len(df) > 2:
                # Correlación con latitud y longitud
                lat_corr = df[variable].corr(df['latitud'])
                lon_corr = df[variable].corr(df['longitud'])
                
                spatial_stats['gradient'] = {
                    'latitud_correlation': float(lat_corr) if not pd.isna(lat_corr) else 0.0,
                    'longitud_correlation': float(lon_corr) if not pd.isna(lon_corr) else 0.0
                }
            
            return spatial_stats
            
        except Exception as e:
            logger.error(f"Error calculando estadísticas espaciales: {str(e)}")
            return {'error': str(e)}
    
    def export_spatial_data(self, df: pd.DataFrame, output_path: str) -> str:
        """
        Exporta datos espaciales en formato GeoJSON.
        
        Args:
            df: DataFrame con datos climáticos y coordenadas
            output_path: Ruta del archivo de salida
            
        Returns:
            Ruta del archivo exportado
        """
        try:
            if 'latitud' not in df.columns or 'longitud' not in df.columns:
                raise ValueError("Datos de coordenadas no disponibles")
            
            # Crear estructura GeoJSON
            geojson = {
                "type": "FeatureCollection",
                "features": []
            }
            
            for _, row in df.iterrows():
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [row['longitud'], row['latitud']]
                    },
                    "properties": {}
                }
                
                # Agregar propiedades (excluir coordenadas)
                for col in df.columns:
                    if col not in ['latitud', 'longitud']:
                        value = row[col]
                        if pd.isna(value):
                            feature["properties"][col] = None
                        elif isinstance(value, (int, float)):
                            feature["properties"][col] = float(value)
                        else:
                            feature["properties"][col] = str(value)
                
                geojson["features"].append(feature)
            
            # Guardar archivo
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(geojson, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Datos espaciales exportados a: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exportando datos espaciales: {str(e)}")
            raise 
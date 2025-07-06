"""
Ejemplo de uso de la API de Análisis Climático de Cundinamarca.
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time

# Configuración de la API
API_BASE_URL = "http://localhost:8000/api/v1"

def test_api_health():
    """Prueba la salud de la API."""
    print("=== Probando salud de la API ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API está funcionando correctamente")
            print(f"Estado: {response.json()['status']}")
        else:
            print("❌ API no está respondiendo correctamente")
    except Exception as e:
        print(f"❌ Error conectando con la API: {str(e)}")

def extract_climate_data():
    """Ejemplo de extracción de datos climáticos."""
    print("\n=== Extrayendo datos climáticos ===")
    
    # Parámetros de extracción
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "station_code": None  # Extraer todas las estaciones
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/extract-data",
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Datos extraídos exitosamente")
            print(f"Registros extraídos: {result['data_count']}")
            print(f"Archivo guardado: {result['file_path']}")
            return result['file_path']
        else:
            print(f"❌ Error extrayendo datos: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en extracción: {str(e)}")
        return None

def process_climate_data(file_path):
    """Ejemplo de procesamiento de datos."""
    print("\n=== Procesando datos climáticos ===")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/process-data",
            params={"file_path": file_path}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Datos procesados exitosamente")
                print(f"Registros procesados: {result['data_count']}")
                print(f"Archivo procesado: {result['processed_data_path']}")
                print(f"Score de calidad: {result['validation_results']['data_quality_score']:.2f}%")
                return result['processed_data_path']
            else:
                print("❌ Datos no válidos")
                print(f"Errores: {result['validation_results']['errors']}")
                return None
        else:
            print(f"❌ Error procesando datos: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en procesamiento: {str(e)}")
        return None

def analyze_climate_data(file_path):
    """Ejemplo de análisis exploratorio."""
    print("\n=== Realizando análisis exploratorio ===")
    
    payload = {
        "data_file": file_path,
        "analysis_type": "complete"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze-data",
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Análisis completado exitosamente")
                print(f"Directorio de resultados: {result['output_directory']}")
                print(f"Total de registros: {result['data_summary']['total_records']}")
                return result['output_directory']
            else:
                print("❌ Error en el análisis")
                return None
        else:
            print(f"❌ Error en análisis: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en análisis: {str(e)}")
        return None

def create_visualizations(file_path):
    """Ejemplo de creación de visualizaciones."""
    print("\n=== Creando visualizaciones ===")
    
    payload = {
        "data_file": file_path,
        "plot_types": ["temperatura", "precipitacion", "correlation", "dashboard"]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/create-visualizations",
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Visualizaciones creadas exitosamente")
                print(f"Total de gráficos: {result['total_plots']}")
                print(f"Directorio: {result['output_directory']}")
                print("Gráficos creados:")
                for name, path in result['visualizations'].items():
                    print(f"  - {name}: {path}")
                return result['output_directory']
            else:
                print("❌ Error creando visualizaciones")
                return None
        else:
            print(f"❌ Error en visualizaciones: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en visualizaciones: {str(e)}")
        return None

def get_stations_info():
    """Ejemplo de obtención de información de estaciones."""
    print("\n=== Obteniendo información de estaciones ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/stations")
        
        if response.status_code == 200:
            stations = response.json()
            print(f"✅ Se encontraron {len(stations)} estaciones")
            
            # Mostrar primeras 5 estaciones
            for i, station in enumerate(stations[:5]):
                print(f"  {i+1}. {station['name']} ({station['code']})")
                print(f"     Región: {station['region']}")
                print(f"     Válida: {'Sí' if station['is_valid'] else 'No'}")
            
            if len(stations) > 5:
                print(f"  ... y {len(stations) - 5} estaciones más")
                
            return stations
        else:
            print(f"❌ Error obteniendo estaciones: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error obteniendo estaciones: {str(e)}")
        return None

def validate_data(file_path):
    """Ejemplo de validación de datos."""
    print("\n=== Validando datos ===")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/validate-data",
            params={"file_path": file_path}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Validación completada")
            print(f"Válido: {'Sí' if result['success'] else 'No'}")
            print(f"Score de calidad: {result['quality_score']:.2f}%")
            print(f"Total de registros: {result['data_count']}")
            
            if result['validation_results']['errors']:
                print("Errores encontrados:")
                for error in result['validation_results']['errors']:
                    print(f"  - {error}")
            
            if result['validation_results']['warnings']:
                print("Advertencias:")
                for warning in result['validation_results']['warnings']:
                    print(f"  - {warning}")
                    
            return result['success']
        else:
            print(f"❌ Error validando datos: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en validación: {str(e)}")
        return False

def spatial_analysis(file_path):
    """Ejemplo de análisis espacial."""
    print("\n=== Realizando análisis espacial ===")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/spatial-analysis",
            params={
                "data_file": file_path,
                "variable": "temperatura_promedio"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Análisis espacial completado")
                print(f"Estaciones en Cundinamarca: {result['stations_in_cundinamarca']}")
                print(f"Total de estaciones: {result['total_stations']}")
                print(f"Archivo GeoJSON: {result['geojson_file']}")
                return result['geojson_file']
            else:
                print("❌ Error en análisis espacial")
                return None
        else:
            print(f"❌ Error en análisis espacial: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en análisis espacial: {str(e)}")
        return None

def trend_analysis(file_path):
    """Ejemplo de análisis de tendencias."""
    print("\n=== Realizando análisis de tendencias ===")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/trend-analysis",
            params={
                "data_file": file_path,
                "variable": "temperatura_promedio"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Análisis de tendencias completado")
                trend_data = result['trend_analysis']
                
                if 'linear_trend' in trend_data:
                    linear = trend_data['linear_trend']
                    print(f"Tendencia lineal: {linear['trend_direction']}")
                    print(f"R²: {linear['r_squared']:.4f}")
                    print(f"Significativo: {'Sí' if linear['trend_significance'] else 'No'}")
                
                if 'mann_kendall' in trend_data:
                    mk = trend_data['mann_kendall']
                    if mk['trend']:
                        print(f"Test Mann-Kendall: {mk['trend']}")
                        print(f"P-value: {mk['p_value']:.4f}")
                
                return trend_data
            else:
                print("❌ Error en análisis de tendencias")
                return None
        else:
            print(f"❌ Error en análisis de tendencias: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en análisis de tendencias: {str(e)}")
        return None

def main():
    """Función principal que ejecuta todos los ejemplos."""
    print("🚀 Ejemplo de uso de la API de Análisis Climático de Cundinamarca")
    print("=" * 70)
    
    # 1. Probar salud de la API
    test_api_health()
    
    # 2. Obtener información de estaciones
    stations = get_stations_info()
    
    # 3. Extraer datos (comentado para evitar sobrecarga del servidor)
    # print("\n⚠️  Saltando extracción de datos para evitar sobrecarga...")
    # extracted_file = "data/extracted/example_data.csv"  # Archivo de ejemplo
    
    # 4. Procesar datos
    # processed_file = process_climate_data(extracted_file)
    
    # 5. Validar datos
    # is_valid = validate_data(processed_file)
    
    # 6. Análisis exploratorio
    # analysis_dir = analyze_climate_data(processed_file)
    
    # 7. Crear visualizaciones
    # viz_dir = create_visualizations(processed_file)
    
    # 8. Análisis espacial
    # spatial_file = spatial_analysis(processed_file)
    
    # 9. Análisis de tendencias
    # trend_results = trend_analysis(processed_file)
    
    print("\n" + "=" * 70)
    print("✅ Ejemplo completado")
    print("\nPara ejecutar el flujo completo:")
    print("1. Asegúrate de que la API esté ejecutándose")
    print("2. Descomenta las líneas en la función main()")
    print("3. Ejecuta este script nuevamente")

if __name__ == "__main__":
    main() 
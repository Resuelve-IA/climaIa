"""
Endpoints de la API para análisis climático de Cundinamarca.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any
import pandas as pd
import logging
from datetime import datetime, timedelta
from pathlib import Path

from backend.services.data_extraction import DataExtractionService
from backend.services.data_processing import DataProcessingService
from backend.services.exploratory_analysis import ExploratoryAnalysisService
from backend.services.visualization_service import VisualizationService
from backend.schemas.api import (
    ClimateDataRequest,
    ClimateDataResponse,
    StationDataResponse,
    AnalysisRequest,
    AnalysisResponse,
    VisualizationRequest,
    ValidationResponse,
    ProcessingResponse,
)
from backend.utils.validators import DataValidator
from backend.utils.geospatial import GeospatialProcessor

logger = logging.getLogger(__name__)

# Crear router principal
router = APIRouter()

# Inicializar servicios
data_extraction = DataExtractionService()
data_processing = DataProcessingService()
exploratory_analysis = ExploratoryAnalysisService()
visualization_service = VisualizationService()
validator = DataValidator()
geo_processor = GeospatialProcessor()


@router.get("/", response_model=Dict[str, str])
async def root():
    """Endpoint raíz de la API."""
    return {
        "message": "API de Análisis Climático de Cundinamarca",
        "version": "1.0.0",
        "status": "activo",
    }


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/extract-data", response_model=ClimateDataResponse)
async def extract_climate_data(request: ClimateDataRequest):
    """
    Extrae datos climáticos del IDEAM.

    Args:
        request: Solicitud con parámetros de extracción

    Returns:
        Respuesta con datos extraídos
    """
    try:
        logger.info(
            f"Extrayendo datos para período: {request.start_date} - {request.end_date}"
        )

        # Extraer datos
        if request.station_code:
            data = data_extraction.extract_data_by_station(
                request.station_code, request.start_date, request.end_date
            )
        else:
            data = data_extraction.extract_data_by_date_range(
                request.start_date, request.end_date
            )

        if data is None or len(data) == 0:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron datos para los parámetros especificados",
            )

        # Convertir a DataFrame
        df = pd.DataFrame(data)

        # Guardar datos extraídos
        output_path = f"data/extracted/climate_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        data_extraction.save_data_to_csv(df, output_path)

        return ClimateDataResponse(
            success=True,
            message="Datos extraídos exitosamente",
            data_count=len(df),
            date_range={"start": request.start_date, "end": request.end_date},
            file_path=output_path,
            columns=list(df.columns),
        )

    except Exception as e:
        logger.error(f"Error extrayendo datos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extrayendo datos: {str(e)}")


@router.post("/process-data", response_model=ProcessingResponse)
async def process_climate_data(
    file_path: str = Query(..., description="Ruta del archivo CSV con datos")
):
    """
    Procesa y limpia datos climáticos.

    Args:
        file_path: Ruta del archivo CSV con datos

    Returns:
        Respuesta con datos procesados
    """
    try:
        logger.info(f"Procesando datos desde: {file_path}")

        # Cargar datos
        if not Path(file_path).exists():
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        df = pd.read_csv(file_path)

        # Validar datos
        validation_results = validator.validate_climate_data(df)

        if not validation_results["is_valid"]:
            return ProcessingResponse(
                success=False,
                message="Datos no válidos",
                validation_results=validation_results,
                data_count=len(df),
                processed_data_path=None,
            )

        # Procesar datos
        processed_df = data_processing.clean_climate_data(df)

        # Guardar datos procesados
        output_path = f"data/processed/processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        data_processing.save_processed_data(processed_df, output_path)

        # Calcular estadísticas
        stats = data_processing.calculate_statistics(processed_df)

        return ProcessingResponse(
            success=True,
            message="Datos procesados exitosamente",
            validation_results=validation_results,
            data_count=len(processed_df),
            processed_data_path=output_path,
            statistics=stats,
        )

    except Exception as e:
        logger.error(f"Error procesando datos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando datos: {str(e)}")


@router.post("/analyze-data", response_model=AnalysisResponse)
async def analyze_climate_data(request: AnalysisRequest):
    """
    Realiza análisis exploratorio de datos climáticos.

    Args:
        request: Solicitud con parámetros de análisis

    Returns:
        Respuesta con resultados del análisis
    """
    try:
        logger.info(f"Analizando datos desde: {request.data_file}")

        # Cargar datos
        if not Path(request.data_file).exists():
            raise HTTPException(
                status_code=404, detail="Archivo de datos no encontrado"
            )

        df = pd.read_csv(request.data_file)

        # Realizar análisis exploratorio
        output_dir = f"analysis/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        analysis_results = exploratory_analysis.perform_complete_eda(df, output_dir)

        return AnalysisResponse(
            success=True,
            message="Análisis completado exitosamente",
            analysis_results=analysis_results,
            output_directory=output_dir,
            data_summary={
                "total_records": len(df),
                "variables": list(df.columns),
                "date_range": {
                    "start": df["fecha"].min() if "fecha" in df.columns else None,
                    "end": df["fecha"].max() if "fecha" in df.columns else None,
                },
            },
        )

    except Exception as e:
        logger.error(f"Error analizando datos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analizando datos: {str(e)}")


@router.post("/create-visualizations", response_model=Dict[str, Any])
async def create_visualizations(request: VisualizationRequest):
    """
    Crea visualizaciones de datos climáticos.

    Args:
        request: Solicitud con parámetros de visualización

    Returns:
        Respuesta con rutas de visualizaciones creadas
    """
    try:
        logger.info(f"Creando visualizaciones para: {request.data_file}")

        # Cargar datos
        if not Path(request.data_file).exists():
            raise HTTPException(
                status_code=404, detail="Archivo de datos no encontrado"
            )

        df = pd.read_csv(request.data_file)

        # Crear directorio de salida
        output_dir = f"visualizations/plots_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        visualizations = {}

        # Crear diferentes tipos de visualizaciones
        if "temperatura" in request.plot_types or "all" in request.plot_types:
            temp_plots = visualization_service.create_temperature_analysis_plots(
                df, output_dir
            )
            visualizations.update(temp_plots)

        if "precipitacion" in request.plot_types or "all" in request.plot_types:
            precip_plots = visualization_service.create_precipitation_analysis_plots(
                df, output_dir
            )
            visualizations.update(precip_plots)

        if "correlation" in request.plot_types or "all" in request.plot_types:
            corr_plot = visualization_service.create_correlation_heatmap(df, output_dir)
            visualizations["correlation_heatmap"] = corr_plot

        if "station_comparison" in request.plot_types or "all" in request.plot_types:
            station_plot = visualization_service.create_station_comparison_plot(
                df, output_dir
            )
            visualizations["station_comparison"] = station_plot

        if "anomalies" in request.plot_types or "all" in request.plot_types:
            anomaly_plot = visualization_service.create_anomaly_detection_plot(
                df, output_dir
            )
            visualizations["anomaly_detection"] = anomaly_plot

        if "dashboard" in request.plot_types or "all" in request.plot_types:
            dashboard = visualization_service.create_summary_dashboard(df, output_dir)
            visualizations["summary_dashboard"] = dashboard

        return {
            "success": True,
            "message": "Visualizaciones creadas exitosamente",
            "visualizations": visualizations,
            "output_directory": output_dir,
            "total_plots": len(visualizations),
        }

    except Exception as e:
        logger.error(f"Error creando visualizaciones: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error creando visualizaciones: {str(e)}"
        )


@router.get("/stations", response_model=List[StationDataResponse])
async def get_stations():
    """
    Obtiene información de estaciones meteorológicas.

    Returns:
        Lista de estaciones disponibles
    """
    try:
        logger.info("Obteniendo información de estaciones")

        stations = data_extraction.get_stations_info()

        if not stations:
            raise HTTPException(status_code=404, detail="No se encontraron estaciones")

        # Procesar información de estaciones
        processed_stations = []
        for station in stations:
            # Validar datos de estación
            validation = validator.validate_station_data(station)

            # Procesar información geoespacial
            if "latitud" in station and "longitud" in station:
                geo_info = geo_processor.validate_coordinates(
                    station["latitud"], station["longitud"]
                )
            else:
                geo_info = {"location_info": {"region": "Desconocido"}}

            processed_stations.append(
                StationDataResponse(
                    code=station.get("codigo", "N/A"),
                    name=station.get("nombre", "N/A"),
                    latitude=station.get("latitud"),
                    longitude=station.get("longitud"),
                    elevation=station.get("elevacion"),
                    region=geo_info["location_info"].get("region", "Desconocido"),
                    is_valid=validation["is_valid"],
                    validation_errors=validation["errors"],
                )
            )

        return processed_stations

    except Exception as e:
        logger.error(f"Error obteniendo estaciones: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo estaciones: {str(e)}"
        )


@router.get("/stations/{station_code}", response_model=StationDataResponse)
async def get_station(station_code: str):
    """
    Obtiene información de una estación específica.

    Args:
        station_code: Código de la estación

    Returns:
        Información de la estación
    """
    try:
        logger.info(f"Obteniendo información de estación: {station_code}")

        stations = data_extraction.get_stations_info()

        # Buscar estación específica
        station = None
        for s in stations:
            if s.get("codigo") == station_code:
                station = s
                break

        if not station:
            raise HTTPException(
                status_code=404, detail=f"Estación {station_code} no encontrada"
            )

        # Validar y procesar datos
        validation = validator.validate_station_data(station)

        if "latitud" in station and "longitud" in station:
            geo_info = geo_processor.validate_coordinates(
                station["latitud"], station["longitud"]
            )
        else:
            geo_info = {"location_info": {"region": "Desconocido"}}

        return StationDataResponse(
            code=station.get("codigo", "N/A"),
            name=station.get("nombre", "N/A"),
            latitude=station.get("latitud"),
            longitude=station.get("longitud"),
            elevation=station.get("elevacion"),
            region=geo_info["location_info"].get("region", "Desconocido"),
            is_valid=validation["is_valid"],
            validation_errors=validation["errors"],
        )

    except Exception as e:
        logger.error(f"Error obteniendo estación {station_code}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo estación: {str(e)}"
        )


@router.post("/validate-data", response_model=ValidationResponse)
async def validate_data(
    file_path: str = Query(..., description="Ruta del archivo CSV con datos")
):
    """
    Valida datos climáticos.

    Args:
        file_path: Ruta del archivo CSV con datos

    Returns:
        Resultados de validación
    """
    try:
        logger.info(f"Validando datos desde: {file_path}")

        # Cargar datos
        if not Path(file_path).exists():
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        df = pd.read_csv(file_path)

        # Validar datos
        validation_results = validator.validate_climate_data(df)

        # Generar reporte
        report = validator.get_validation_report(validation_results)

        return ValidationResponse(
            success=validation_results["is_valid"],
            validation_results=validation_results,
            report=report,
            data_count=len(df),
            quality_score=validation_results.get("data_quality_score", 0.0),
        )

    except Exception as e:
        logger.error(f"Error validando datos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validando datos: {str(e)}")


@router.get("/download/{file_type}/{filename}")
async def download_file(file_type: str, filename: str):
    """
    Descarga archivos generados por la API.

    Args:
        file_type: Tipo de archivo (data, analysis, visualizations)
        filename: Nombre del archivo

    Returns:
        Archivo para descarga
    """
    try:
        # Construir ruta del archivo
        file_path = Path(f"{file_type}/{filename}")

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/octet-stream",
        )

    except Exception as e:
        logger.error(f"Error descargando archivo: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error descargando archivo: {str(e)}"
        )


@router.get("/spatial-analysis", response_model=Dict[str, Any])
async def spatial_analysis(
    data_file: str = Query(..., description="Ruta del archivo CSV con datos"),
    variable: str = Query(..., description="Variable climática a analizar"),
):
    """
    Realiza análisis espacial de datos climáticos.

    Args:
        data_file: Ruta del archivo CSV con datos
        variable: Variable climática a analizar

    Returns:
        Resultados del análisis espacial
    """
    try:
        logger.info(f"Realizando análisis espacial para variable: {variable}")

        # Cargar datos
        if not Path(data_file).exists():
            raise HTTPException(
                status_code=404, detail="Archivo de datos no encontrado"
            )

        df = pd.read_csv(data_file)

        # Verificar que hay coordenadas
        if "latitud" not in df.columns or "longitud" not in df.columns:
            raise HTTPException(
                status_code=400, detail="Datos de coordenadas no disponibles"
            )

        # Procesar ubicaciones de estaciones
        df_spatial = geo_processor.process_station_locations(df)

        # Crear resumen espacial
        spatial_summary = geo_processor.create_spatial_summary(df_spatial)

        # Calcular estadísticas espaciales
        spatial_stats = geo_processor.calculate_spatial_statistics(df_spatial, variable)

        # Exportar datos espaciales
        output_path = f"data/spatial/spatial_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.geojson"
        geo_processor.export_spatial_data(df_spatial, output_path)

        return {
            "success": True,
            "spatial_summary": spatial_summary,
            "spatial_statistics": spatial_stats,
            "geojson_file": output_path,
            "stations_in_cundinamarca": spatial_summary.get(
                "stations_in_cundinamarca", 0
            ),
            "total_stations": spatial_summary.get("total_stations", 0),
        }

    except Exception as e:
        logger.error(f"Error en análisis espacial: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error en análisis espacial: {str(e)}"
        )


@router.get("/trend-analysis", response_model=Dict[str, Any])
async def trend_analysis(
    data_file: str = Query(..., description="Ruta del archivo CSV con datos"),
    variable: str = Query(..., description="Variable climática a analizar"),
):
    """
    Realiza análisis de tendencias para una variable climática.

    Args:
        data_file: Ruta del archivo CSV con datos
        variable: Variable climática a analizar

    Returns:
        Resultados del análisis de tendencias
    """
    try:
        logger.info(f"Analizando tendencias para variable: {variable}")

        # Cargar datos
        if not Path(data_file).exists():
            raise HTTPException(
                status_code=404, detail="Archivo de datos no encontrado"
            )

        df = pd.read_csv(data_file)

        # Importar StatisticalAnalyzer
        from backend.utils.statistics import StatisticalAnalyzer

        stat_analyzer = StatisticalAnalyzer()

        # Realizar análisis de tendencias
        trend_results = stat_analyzer.perform_trend_analysis(df, variable)

        return {"success": True, "variable": variable, "trend_analysis": trend_results}

    except Exception as e:
        logger.error(f"Error en análisis de tendencias: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error en análisis de tendencias: {str(e)}"
        )

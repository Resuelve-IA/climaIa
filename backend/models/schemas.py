"""
Esquemas Pydantic para la API
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class WeatherDataBase(BaseModel):
    """Esquema base para datos meteorológicos"""
    fecha_observacion: datetime
    valor_observado: float
    nombre_estacion: str
    departamento: str
    municipio: str
    latitud: float
    longitud: float
    descripcion_sensor: str


class WeatherDataCreate(WeatherDataBase):
    """Esquema para crear datos meteorológicos"""
    pass


class WeatherData(WeatherDataBase):
    """Esquema para datos meteorológicos completos"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StationBase(BaseModel):
    """Esquema base para estaciones"""
    codigo_estacion: str
    nombre_estacion: str
    departamento: str
    municipio: str
    latitud: float
    longitud: float


class StationCreate(StationBase):
    """Esquema para crear estaciones"""
    pass


class Station(StationBase):
    """Esquema para estaciones completas"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    """Esquema para solicitudes de análisis"""
    start_date: datetime
    end_date: datetime
    station_ids: Optional[List[int]] = None
    variables: Optional[List[str]] = None


class AnalysisResult(BaseModel):
    """Esquema para resultados de análisis"""
    analysis_type: str
    data: dict
    metadata: dict
    created_at: datetime


class VisualizationRequest(BaseModel):
    """Esquema para solicitudes de visualización"""
    chart_type: str = Field(..., description="Tipo de gráfico: heatmap, timeline, geographic")
    data_params: dict
    options: Optional[dict] = None


class APIResponse(BaseModel):
    """Esquema para respuestas de la API"""
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None 
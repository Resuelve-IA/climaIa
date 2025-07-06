from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ClimateDataRequest(BaseModel):
    estacion: str
    fecha_inicio: datetime
    fecha_fin: datetime


class ClimateDataResponse(BaseModel):
    estacion: str
    datos: List[Dict[str, Any]]


class StationDataResponse(BaseModel):
    codigo: str
    nombre: str
    departamento: str
    municipio: str
    latitud: float
    longitud: float
    datos: Optional[List[Dict[str, Any]]]


class AnalysisRequest(BaseModel):
    tipo_analisis: str
    parametros: Optional[Dict[str, Any]]


class AnalysisResponse(BaseModel):
    tipo_analisis: str
    resultado: Dict[str, Any]
    graficos: Optional[List[str]]


class VisualizationRequest(BaseModel):
    tipo_grafico: str
    parametros: Optional[Dict[str, Any]]


class ValidationResponse(BaseModel):
    valido: bool
    errores: Optional[List[str]]


class ProcessingResponse(BaseModel):
    exito: bool
    mensaje: str
    archivo_salida: Optional[str]

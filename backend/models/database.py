"""
Modelos de base de datos SQLAlchemy
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.config.database import Base


class Station(Base):
    """Modelo para estaciones meteorológicas"""
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    codigo_estacion = Column(String(50), unique=True, index=True, nullable=False)
    nombre_estacion = Column(String(200), nullable=False)
    departamento = Column(String(100), nullable=False)
    municipio = Column(String(100), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con datos meteorológicos
    weather_data = relationship("WeatherData", back_populates="station")


class WeatherData(Base):
    """Modelo para datos meteorológicos"""
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    fecha_observacion = Column(DateTime, nullable=False, index=True)
    valor_observado = Column(Float, nullable=False)
    descripcion_sensor = Column(String(200), nullable=False)
    unidad_medida = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con estación
    station = relationship("Station", back_populates="weather_data")


class AnalysisResult(Base):
    """Modelo para resultados de análisis"""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_type = Column(String(100), nullable=False)
    parameters = Column(Text)  # JSON como texto
    result_data = Column(Text)  # JSON como texto
    extra_metadata = Column(Text)  # JSON como texto (renombrado)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DataProcessingLog(Base):
    """Modelo para logs de procesamiento de datos"""
    __tablename__ = "data_processing_logs"

    id = Column(Integer, primary_key=True, index=True)
    process_type = Column(String(100), nullable=False)  # extraction, cleaning, analysis
    status = Column(String(50), nullable=False)  # success, error, in_progress
    records_processed = Column(Integer, default=0)
    error_message = Column(Text)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 
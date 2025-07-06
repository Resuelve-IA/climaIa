"""
Utilidades para validación de datos climáticos.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class DataValidator:
    """Clase para validación de datos climáticos."""

    def __init__(self):
        # Rangos válidos para Colombia/Cundinamarca
        self.valid_ranges = {
            "temperatura_maxima": (-10, 45),  # °C
            "temperatura_minima": (-15, 35),  # °C
            "temperatura_promedio": (-10, 40),  # °C
            "humedad_relativa": (0, 100),  # %
            "precipitacion": (0, 1000),  # mm
            "presion_atmosferica": (800, 1100),  # hPa
            "velocidad_viento": (0, 100),  # m/s
            "direccion_viento": (0, 360),  # grados
            "radiacion_solar": (0, 1200),  # W/m²
        }

    def validate_climate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Valida datos climáticos completos.

        Args:
            df: DataFrame con datos climáticos

        Returns:
            Diccionario con resultados de validación
        """
        try:
            validation_results = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "validation_summary": {},
                "data_quality_score": 0.0,
            }

            # Validar estructura básica
            structure_validation = self._validate_data_structure(df)
            validation_results["errors"].extend(structure_validation["errors"])
            validation_results["warnings"].extend(structure_validation["warnings"])

            # Validar rangos de valores
            range_validation = self._validate_value_ranges(df)
            validation_results["errors"].extend(range_validation["errors"])
            validation_results["warnings"].extend(range_validation["warnings"])

            # Validar consistencia temporal
            temporal_validation = self._validate_temporal_consistency(df)
            validation_results["errors"].extend(temporal_validation["errors"])
            validation_results["warnings"].extend(temporal_validation["warnings"])

            # Validar consistencia lógica
            logic_validation = self._validate_logical_consistency(df)
            validation_results["errors"].extend(logic_validation["errors"])
            validation_results["warnings"].extend(logic_validation["warnings"])

            # Calcular score de calidad
            validation_results["data_quality_score"] = self._calculate_quality_score(df)

            # Determinar si los datos son válidos
            validation_results["is_valid"] = len(validation_results["errors"]) == 0

            # Resumen de validación
            validation_results["validation_summary"] = {
                "total_records": len(df),
                "valid_records": len(df) - len(validation_results["errors"]),
                "error_count": len(validation_results["errors"]),
                "warning_count": len(validation_results["warnings"]),
                "completeness": (df.notnull().sum().sum() / (len(df) * len(df.columns)))
                * 100,
            }

            return validation_results

        except Exception as e:
            logger.error(f"Error en validación de datos: {str(e)}")
            return {
                "is_valid": False,
                "errors": [f"Error de validación: {str(e)}"],
                "warnings": [],
                "validation_summary": {},
                "data_quality_score": 0.0,
            }

    def _validate_data_structure(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Valida la estructura básica de los datos."""

        errors = []
        warnings = []

        # Verificar columnas requeridas
        required_columns = ["fecha", "estacion"]
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Columna requerida '{col}' no encontrada")

        # Verificar que hay al menos una variable climática
        climate_variables = [
            "temperatura",
            "precipitacion",
            "humedad",
            "presion",
            "viento",
        ]
        has_climate_data = any(
            any(var in col.lower() for var in climate_variables) for col in df.columns
        )

        if not has_climate_data:
            errors.append("No se encontraron variables climáticas en los datos")

        # Verificar tipos de datos
        if "fecha" in df.columns:
            try:
                pd.to_datetime(df["fecha"])
            except:
                errors.append("Columna 'fecha' no contiene fechas válidas")

        # Verificar que no hay filas completamente vacías
        empty_rows = df.isnull().all(axis=1).sum()
        if empty_rows > 0:
            warnings.append(f"Se encontraron {empty_rows} filas completamente vacías")

        return {"errors": errors, "warnings": warnings}

    def _validate_value_ranges(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Valida rangos de valores para variables climáticas."""

        errors = []
        warnings = []

        for col, (min_val, max_val) in self.valid_ranges.items():
            if col in df.columns:
                # Verificar valores fuera de rango
                out_of_range = df[(df[col] < min_val) | (df[col] > max_val)]

                if len(out_of_range) > 0:
                    error_msg = f"Columna '{col}': {len(out_of_range)} valores fuera del rango válido ({min_val}, {max_val})"

                    if (
                        len(out_of_range) > len(df) * 0.1
                    ):  # Más del 10% de valores fuera de rango
                        errors.append(error_msg)
                    else:
                        warnings.append(error_msg)

        return {"errors": errors, "warnings": warnings}

    def _validate_temporal_consistency(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Valida consistencia temporal de los datos."""

        errors = []
        warnings = []

        if "fecha" not in df.columns:
            return {"errors": errors, "warnings": warnings}

        try:
            df_temp = df.copy()
            df_temp["fecha"] = pd.to_datetime(df_temp["fecha"])

            # Verificar que las fechas están en orden cronológico
            df_sorted = df_temp.sort_values("fecha")
            if not df_sorted["fecha"].equals(df_temp["fecha"]):
                warnings.append("Las fechas no están en orden cronológico")

            # Verificar duplicados de fecha por estación
            if "estacion" in df.columns:
                duplicates = df_temp.groupby(["estacion", "fecha"]).size()
                duplicate_dates = duplicates[duplicates > 1]

                if len(duplicate_dates) > 0:
                    warnings.append(
                        f"Se encontraron fechas duplicadas en {len(duplicate_dates)} combinaciones estación-fecha"
                    )

            # Verificar gaps temporales grandes
            if "estacion" in df.columns:
                for station in df_temp["estacion"].unique():
                    station_data = df_temp[df_temp["estacion"] == station].sort_values(
                        "fecha"
                    )

                    if len(station_data) > 1:
                        date_diffs = station_data["fecha"].diff().dt.days
                        large_gaps = date_diffs[
                            date_diffs > 30
                        ]  # Gaps mayores a 30 días

                        if len(large_gaps) > 0:
                            warnings.append(
                                f"Estación {station}: {len(large_gaps)} gaps temporales mayores a 30 días"
                            )

        except Exception as e:
            errors.append(f"Error validando consistencia temporal: {str(e)}")

        return {"errors": errors, "warnings": warnings}

    def _validate_logical_consistency(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Valida consistencia lógica entre variables."""

        errors = []
        warnings = []

        # Verificar que temperatura mínima <= promedio <= máxima
        temp_cols = ["temperatura_minima", "temperatura_promedio", "temperatura_maxima"]
        if all(col in df.columns for col in temp_cols):
            invalid_temp = df[
                (df["temperatura_minima"] > df["temperatura_promedio"])
                | (df["temperatura_promedio"] > df["temperatura_maxima"])
            ]

            if len(invalid_temp) > 0:
                error_msg = f"Se encontraron {len(invalid_temp)} registros con temperaturas inconsistentes"

                if (
                    len(invalid_temp) > len(df) * 0.05
                ):  # Más del 5% de registros inconsistentes
                    errors.append(error_msg)
                else:
                    warnings.append(error_msg)

        # Verificar que precipitación no es negativa
        if "precipitacion" in df.columns:
            negative_precip = df[df["precipitacion"] < 0]
            if len(negative_precip) > 0:
                errors.append(
                    f"Se encontraron {len(negative_precip)} registros con precipitación negativa"
                )

        # Verificar que humedad está entre 0 y 100
        if "humedad_relativa" in df.columns:
            invalid_humidity = df[
                (df["humedad_relativa"] < 0) | (df["humedad_relativa"] > 100)
            ]
            if len(invalid_humidity) > 0:
                errors.append(
                    f"Se encontraron {len(invalid_humidity)} registros con humedad fuera del rango [0, 100]"
                )

        return {"errors": errors, "warnings": warnings}

    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calcula un score de calidad de los datos."""

        score = 100.0

        # Penalizar por datos faltantes
        missing_percentage = (
            df.isnull().sum().sum() / (len(df) * len(df.columns))
        ) * 100
        score -= (
            missing_percentage * 0.5
        )  # Penalizar 0.5 puntos por cada % de datos faltantes

        # Penalizar por valores fuera de rango
        out_of_range_count = 0
        for col, (min_val, max_val) in self.valid_ranges.items():
            if col in df.columns:
                out_of_range = df[(df[col] < min_val) | (df[col] > max_val)]
                out_of_range_count += len(out_of_range)

        out_of_range_percentage = (
            out_of_range_count / (len(df) * len(df.columns))
        ) * 100
        score -= (
            out_of_range_percentage * 1.0
        )  # Penalizar 1 punto por cada % de valores fuera de rango

        # Penalizar por inconsistencias lógicas
        if all(
            col in df.columns
            for col in [
                "temperatura_minima",
                "temperatura_promedio",
                "temperatura_maxima",
            ]
        ):
            invalid_temp = df[
                (df["temperatura_minima"] > df["temperatura_promedio"])
                | (df["temperatura_promedio"] > df["temperatura_maxima"])
            ]
            invalid_percentage = (len(invalid_temp) / len(df)) * 100
            score -= (
                invalid_percentage * 2.0
            )  # Penalizar 2 puntos por cada % de inconsistencias

        return max(0.0, score)

    def validate_station_data(self, station_data: Dict) -> Dict[str, Any]:
        """
        Valida datos de una estación meteorológica.

        Args:
            station_data: Diccionario con datos de la estación

        Returns:
            Diccionario con resultados de validación
        """
        try:
            validation_results = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "validation_summary": {},
            }

            # Validar código de estación
            if "codigo" in station_data:
                code = str(station_data["codigo"]).strip()
                if not re.match(r"^[A-Z0-9]{3,10}$", code):
                    validation_results["errors"].append("Código de estación inválido")
                else:
                    validation_results["validation_summary"]["codigo"] = code

            # Validar nombre
            if "nombre" in station_data:
                name = str(station_data["nombre"]).strip()
                if len(name) < 3 or len(name) > 100:
                    validation_results["errors"].append("Nombre de estación inválido")
                else:
                    validation_results["validation_summary"]["nombre"] = name

            # Validar coordenadas
            if "latitud" in station_data and "longitud" in station_data:
                try:
                    lat = float(station_data["latitud"])
                    lon = float(station_data["longitud"])

                    if not (-90 <= lat <= 90):
                        validation_results["errors"].append(
                            "Latitud fuera del rango válido [-90, 90]"
                        )

                    if not (-180 <= lon <= 180):
                        validation_results["errors"].append(
                            "Longitud fuera del rango válido [-180, 180]"
                        )

                    validation_results["validation_summary"]["coordenadas"] = {
                        "latitud": lat,
                        "longitud": lon,
                    }

                except (ValueError, TypeError):
                    validation_results["errors"].append(
                        "Coordenadas no son valores numéricos válidos"
                    )

            # Validar elevación
            if "elevacion" in station_data:
                try:
                    elev = float(station_data["elevacion"])
                    if elev < -1000 or elev > 10000:  # Rango razonable para Colombia
                        validation_results["warnings"].append(
                            "Elevación fuera del rango típico para Colombia"
                        )

                    validation_results["validation_summary"]["elevacion"] = elev

                except (ValueError, TypeError):
                    validation_results["errors"].append(
                        "Elevación no es un valor numérico válido"
                    )

            # Determinar si es válido
            validation_results["is_valid"] = len(validation_results["errors"]) == 0

            return validation_results

        except Exception as e:
            logger.error(f"Error validando datos de estación: {str(e)}")
            return {
                "is_valid": False,
                "errors": [f"Error de validación: {str(e)}"],
                "warnings": [],
                "validation_summary": {},
            }

    def get_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """
        Genera un reporte de validación en formato texto.

        Args:
            validation_results: Resultados de validación

        Returns:
            Reporte de validación en formato texto
        """
        report = []
        report.append("REPORTE DE VALIDACIÓN DE DATOS CLIMÁTICOS")
        report.append("=" * 50)
        report.append("")

        # Resumen general
        summary = validation_results.get("validation_summary", {})
        report.append("RESUMEN GENERAL:")
        report.append(f"- Total de registros: {summary.get('total_records', 'N/A')}")
        report.append(f"- Registros válidos: {summary.get('valid_records', 'N/A')}")
        report.append(
            f"- Score de calidad: {validation_results.get('data_quality_score', 0):.2f}%"
        )
        report.append(f"- Completitud: {summary.get('completeness', 0):.2f}%")
        report.append("")

        # Errores
        errors = validation_results.get("errors", [])
        if errors:
            report.append("ERRORES ENCONTRADOS:")
            for i, error in enumerate(errors, 1):
                report.append(f"{i}. {error}")
            report.append("")

        # Advertencias
        warnings = validation_results.get("warnings", [])
        if warnings:
            report.append("ADVERTENCIAS:")
            for i, warning in enumerate(warnings, 1):
                report.append(f"{i}. {warning}")
            report.append("")

        # Estado final
        if validation_results.get("is_valid", False):
            report.append("ESTADO: DATOS VÁLIDOS ✓")
        else:
            report.append("ESTADO: DATOS INVÁLIDOS ✗")

        return "\n".join(report)

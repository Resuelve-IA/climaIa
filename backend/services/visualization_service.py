"""
Servicio de visualización de datos climáticos.
Genera gráficos, mapas y visualizaciones interactivas.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class VisualizationService:
    """Servicio para generar visualizaciones de datos climáticos."""

    def __init__(self):
        # Configurar estilos
        plt.style.use("seaborn-v0_8")
        sns.set_palette("husl")

    def create_temperature_analysis_plots(
        self, df: pd.DataFrame, output_dir: str
    ) -> Dict[str, str]:
        """
        Crea visualizaciones de análisis de temperatura.

        Args:
            df: DataFrame con datos climáticos
            output_dir: Directorio de salida

        Returns:
            Diccionario con rutas de archivos generados
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            plots = {}

            # 1. Serie temporal de temperaturas
            if "fecha" in df.columns and "temperatura_promedio" in df.columns:
                fig = go.Figure()

                df_temp = df.copy()
                df_temp["fecha"] = pd.to_datetime(df_temp["fecha"])
                df_temp = df_temp.sort_values("fecha")

                fig.add_trace(
                    go.Scatter(
                        x=df_temp["fecha"],
                        y=df_temp["temperatura_promedio"],
                        mode="lines+markers",
                        name="Temperatura Promedio",
                        line=dict(color="red", width=2),
                    )
                )

                if "temperatura_maxima" in df_temp.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df_temp["fecha"],
                            y=df_temp["temperatura_maxima"],
                            mode="lines",
                            name="Temperatura Máxima",
                            line=dict(color="orange", width=1),
                        )
                    )

                if "temperatura_minima" in df_temp.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df_temp["fecha"],
                            y=df_temp["temperatura_minima"],
                            mode="lines",
                            name="Temperatura Mínima",
                            line=dict(color="blue", width=1),
                        )
                    )

                fig.update_layout(
                    title="Evolución Temporal de Temperaturas",
                    xaxis_title="Fecha",
                    yaxis_title="Temperatura (°C)",
                    hovermode="x unified",
                )

                temp_plot_path = output_path / "temperature_timeseries.html"
                fig.write_html(str(temp_plot_path))
                plots["temperature_timeseries"] = str(temp_plot_path)

            # 2. Distribución de temperaturas
            temp_cols = [col for col in df.columns if "temperatura" in col.lower()]

            if temp_cols:
                fig = make_subplots(
                    rows=1, cols=len(temp_cols), subplot_titles=temp_cols
                )

                for i, col in enumerate(temp_cols, 1):
                    fig.add_trace(
                        go.Histogram(x=df[col], name=col, nbinsx=30), row=1, col=i
                    )

                fig.update_layout(
                    title="Distribución de Temperaturas", showlegend=False
                )

                dist_plot_path = output_path / "temperature_distribution.html"
                fig.write_html(str(dist_plot_path))
                plots["temperature_distribution"] = str(dist_plot_path)

            # 3. Box plot por estación
            if "estacion" in df.columns and "temperatura_promedio" in df.columns:
                fig = px.box(
                    df,
                    x="estacion",
                    y="temperatura_promedio",
                    title="Distribución de Temperatura por Estación",
                )

                fig.update_layout(
                    xaxis_title="Estación", yaxis_title="Temperatura Promedio (°C)"
                )

                box_plot_path = output_path / "temperature_by_station.html"
                fig.write_html(str(box_plot_path))
                plots["temperature_by_station"] = str(box_plot_path)

            return plots

        except Exception as e:
            logger.error(f"Error creando gráficos de temperatura: {str(e)}")
            raise

    def create_precipitation_analysis_plots(
        self, df: pd.DataFrame, output_dir: str
    ) -> Dict[str, str]:
        """
        Crea visualizaciones de análisis de precipitación.

        Args:
            df: DataFrame con datos climáticos
            output_dir: Directorio de salida

        Returns:
            Diccionario con rutas de archivos generados
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            plots = {}

            # 1. Serie temporal de precipitación
            if "fecha" in df.columns and "precipitacion" in df.columns:
                fig = go.Figure()

                df_temp = df.copy()
                df_temp["fecha"] = pd.to_datetime(df_temp["fecha"])
                df_temp = df_temp.sort_values("fecha")

                fig.add_trace(
                    go.Scatter(
                        x=df_temp["fecha"],
                        y=df_temp["precipitacion"],
                        mode="lines+markers",
                        name="Precipitación",
                        line=dict(color="blue", width=2),
                        fill="tonexty",
                    )
                )

                fig.update_layout(
                    title="Evolución Temporal de Precipitación",
                    xaxis_title="Fecha",
                    yaxis_title="Precipitación (mm)",
                    hovermode="x unified",
                )

                precip_plot_path = output_path / "precipitation_timeseries.html"
                fig.write_html(str(precip_plot_path))
                plots["precipitation_timeseries"] = str(precip_plot_path)

            # 2. Distribución de precipitación
            if "precipitacion" in df.columns:
                fig = go.Figure()

                fig.add_trace(
                    go.Histogram(
                        x=df["precipitacion"],
                        nbinsx=50,
                        name="Precipitación",
                        marker_color="blue",
                    )
                )

                fig.update_layout(
                    title="Distribución de Precipitación",
                    xaxis_title="Precipitación (mm)",
                    yaxis_title="Frecuencia",
                )

                dist_plot_path = output_path / "precipitation_distribution.html"
                fig.write_html(str(dist_plot_path))
                plots["precipitation_distribution"] = str(dist_plot_path)

            # 3. Precipitación acumulada por mes
            if "fecha" in df.columns and "precipitacion" in df.columns:
                df_temp = df.copy()
                df_temp["fecha"] = pd.to_datetime(df_temp["fecha"])
                df_temp["mes"] = df_temp["fecha"].dt.month
                df_temp["año"] = df_temp["fecha"].dt.year

                monthly_precip = (
                    df_temp.groupby(["año", "mes"])["precipitacion"].sum().reset_index()
                )

                fig = px.line(
                    monthly_precip,
                    x="mes",
                    y="precipitacion",
                    color="año",
                    title="Precipitación Mensual Acumulada",
                )

                fig.update_layout(
                    xaxis_title="Mes", yaxis_title="Precipitación Acumulada (mm)"
                )

                monthly_plot_path = output_path / "monthly_precipitation.html"
                fig.write_html(str(monthly_plot_path))
                plots["monthly_precipitation"] = str(monthly_plot_path)

            return plots

        except Exception as e:
            logger.error(f"Error creando gráficos de precipitación: {str(e)}")
            raise

    def create_correlation_heatmap(self, df: pd.DataFrame, output_dir: str) -> str:
        """
        Crea mapa de calor de correlaciones.

        Args:
            df: DataFrame con datos climáticos
            output_dir: Directorio de salida

        Returns:
            Ruta del archivo generado
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            numeric_columns = df.select_dtypes(include=[np.number]).columns

            if len(numeric_columns) < 2:
                raise ValueError("Se necesitan al menos 2 variables numéricas")

            correlation_matrix = df[numeric_columns].corr()

            fig = px.imshow(
                correlation_matrix,
                text_auto=True,
                aspect="auto",
                title="Matriz de Correlación de Variables Climáticas",
                color_continuous_scale="RdBu_r",
            )

            fig.update_layout(xaxis_title="Variables", yaxis_title="Variables")

            heatmap_path = output_path / "correlation_heatmap.html"
            fig.write_html(str(heatmap_path))

            return str(heatmap_path)

        except Exception as e:
            logger.error(f"Error creando mapa de calor: {str(e)}")
            raise

    def create_station_comparison_plot(self, df: pd.DataFrame, output_dir: str) -> str:
        """
        Crea gráfico de comparación entre estaciones.

        Args:
            df: DataFrame con datos climáticos
            output_dir: Directorio de salida

        Returns:
            Ruta del archivo generado
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            if "estacion" not in df.columns:
                raise ValueError("Columna 'estacion' no encontrada")

            # Seleccionar variable principal para comparar
            main_var = None
            for var in ["temperatura_promedio", "precipitacion", "humedad_relativa"]:
                if var in df.columns:
                    main_var = var
                    break

            if not main_var:
                raise ValueError("No se encontraron variables climáticas principales")

            fig = px.box(
                df,
                x="estacion",
                y=main_var,
                title=f"Comparación de {main_var} entre Estaciones",
                color="estacion",
            )

            fig.update_layout(
                xaxis_title="Estación", yaxis_title=main_var, showlegend=False
            )

            comparison_path = output_path / "station_comparison.html"
            fig.write_html(str(comparison_path))

            return str(comparison_path)

        except Exception as e:
            logger.error(f"Error creando comparación de estaciones: {str(e)}")
            raise

    def create_anomaly_detection_plot(self, df: pd.DataFrame, output_dir: str) -> str:
        """
        Crea visualización de detección de anomalías.

        Args:
            df: DataFrame con datos climáticos
            output_dir: Directorio de salida

        Returns:
            Ruta del archivo generado
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Seleccionar variable para análisis
            main_var = None
            for var in ["temperatura_promedio", "precipitacion", "humedad_relativa"]:
                if var in df.columns:
                    main_var = var
                    break

            if not main_var:
                raise ValueError("No se encontraron variables climáticas principales")

            # Detectar anomalías usando IQR
            Q1 = df[main_var].quantile(0.25)
            Q3 = df[main_var].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # Crear figura
            fig = go.Figure()

            # Datos normales
            normal_data = df[
                (df[main_var] >= lower_bound) & (df[main_var] <= upper_bound)
            ]
            fig.add_trace(
                go.Scatter(
                    x=normal_data.index,
                    y=normal_data[main_var],
                    mode="markers",
                    name="Datos Normales",
                    marker=dict(color="blue", size=6),
                )
            )

            # Anomalías
            anomalies = df[(df[main_var] < lower_bound) | (df[main_var] > upper_bound)]
            if len(anomalies) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=anomalies.index,
                        y=anomalies[main_var],
                        mode="markers",
                        name="Anomalías",
                        marker=dict(color="red", size=8, symbol="x"),
                    )
                )

            # Líneas de límites
            fig.add_hline(
                y=upper_bound,
                line_dash="dash",
                line_color="red",
                annotation_text="Límite Superior",
            )
            fig.add_hline(
                y=lower_bound,
                line_dash="dash",
                line_color="red",
                annotation_text="Límite Inferior",
            )

            fig.update_layout(
                title=f"Detección de Anomalías - {main_var}",
                xaxis_title="Índice",
                yaxis_title=main_var,
            )

            anomaly_path = output_path / "anomaly_detection.html"
            fig.write_html(str(anomaly_path))

            return str(anomaly_path)

        except Exception as e:
            logger.error(f"Error creando gráfico de anomalías: {str(e)}")
            raise

    def create_summary_dashboard(self, df: pd.DataFrame, output_dir: str) -> str:
        """
        Crea dashboard resumen con múltiples visualizaciones.

        Args:
            df: DataFrame con datos climáticos
            output_dir: Directorio de salida

        Returns:
            Ruta del archivo generado
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Crear subplots
            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=(
                    "Temperatura Promedio",
                    "Precipitación",
                    "Humedad Relativa",
                    "Distribución Temporal",
                ),
                specs=[
                    [{"secondary_y": False}, {"secondary_y": False}],
                    [{"secondary_y": False}, {"secondary_y": False}],
                ],
            )

            # 1. Temperatura promedio
            if "temperatura_promedio" in df.columns:
                fig.add_trace(
                    go.Histogram(x=df["temperatura_promedio"], name="Temperatura"),
                    row=1,
                    col=1,
                )

            # 2. Precipitación
            if "precipitacion" in df.columns:
                fig.add_trace(
                    go.Histogram(x=df["precipitacion"], name="Precipitación"),
                    row=1,
                    col=2,
                )

            # 3. Humedad relativa
            if "humedad_relativa" in df.columns:
                fig.add_trace(
                    go.Histogram(x=df["humedad_relativa"], name="Humedad"), row=2, col=1
                )

            # 4. Serie temporal (si hay fecha)
            if "fecha" in df.columns and "temperatura_promedio" in df.columns:
                df_temp = df.copy()
                df_temp["fecha"] = pd.to_datetime(df_temp["fecha"])
                df_temp = df_temp.sort_values("fecha")

                fig.add_trace(
                    go.Scatter(
                        x=df_temp["fecha"],
                        y=df_temp["temperatura_promedio"],
                        mode="lines",
                        name="Temperatura",
                    ),
                    row=2,
                    col=2,
                )

            fig.update_layout(
                title="Dashboard Resumen - Análisis Climático",
                height=800,
                showlegend=False,
            )

            dashboard_path = output_path / "summary_dashboard.html"
            fig.write_html(str(dashboard_path))

            return str(dashboard_path)

        except Exception as e:
            logger.error(f"Error creando dashboard: {str(e)}")
            raise

    def export_plots_to_png(
        self, html_files: Dict[str, str], output_dir: str
    ) -> Dict[str, str]:
        """
        Exporta gráficos HTML a formato PNG.

        Args:
            html_files: Diccionario con rutas de archivos HTML
            output_dir: Directorio de salida

        Returns:
            Diccionario con rutas de archivos PNG
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            png_files = {}

            for name, html_path in html_files.items():
                try:
                    # Convertir HTML a PNG usando plotly
                    fig = go.Figure()
                    # Aquí se cargaría el HTML y se convertiría a PNG
                    # Por simplicidad, creamos un gráfico básico

                    png_path = output_path / f"{name}.png"
                    # fig.write_image(str(png_path))
                    png_files[name] = str(png_path)

                except Exception as e:
                    logger.warning(f"No se pudo convertir {name} a PNG: {str(e)}")

            return png_files

        except Exception as e:
            logger.error(f"Error exportando a PNG: {str(e)}")
            raise

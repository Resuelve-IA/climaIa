"""
Utilidades de visualización para datos climáticos.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path

logger = logging.getLogger(__name__)


class PlotGenerator:
    """Clase para generar visualizaciones de datos climáticos."""

    def __init__(self):
        # Configurar estilos
        plt.style.use("seaborn-v0_8")
        sns.set_palette("husl")

        # Colores para variables climáticas
        self.climate_colors = {
            "temperatura": "red",
            "precipitacion": "blue",
            "humedad": "green",
            "presion": "purple",
            "viento": "orange",
            "radiacion": "yellow",
        }

    def create_time_series_plot(
        self, df: pd.DataFrame, variable: str, output_path: str = None
    ) -> go.Figure:
        """
        Crea gráfico de serie temporal para una variable climática.

        Args:
            df: DataFrame con datos climáticos
            variable: Variable a graficar
            output_path: Ruta para guardar el gráfico (opcional)

        Returns:
            Figura de Plotly
        """
        try:
            if "fecha" not in df.columns or variable not in df.columns:
                raise ValueError(f"Columnas 'fecha' y '{variable}' requeridas")

            df_temp = df.copy()
            df_temp["fecha"] = pd.to_datetime(df_temp["fecha"])
            df_temp = df_temp.sort_values("fecha")

            fig = go.Figure()

            # Agregar línea principal
            fig.add_trace(
                go.Scatter(
                    x=df_temp["fecha"],
                    y=df_temp[variable],
                    mode="lines+markers",
                    name=variable,
                    line=dict(width=2),
                    marker=dict(size=4),
                )
            )

            # Configurar layout
            fig.update_layout(
                title=f"Serie Temporal - {variable}",
                xaxis_title="Fecha",
                yaxis_title=variable,
                hovermode="x unified",
                template="plotly_white",
            )

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Gráfico guardado en: {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creando gráfico de serie temporal: {str(e)}")
            raise

    def create_distribution_plot(
        self, df: pd.DataFrame, variable: str, output_path: str = None
    ) -> go.Figure:
        """
        Crea gráfico de distribución para una variable climática.

        Args:
            df: DataFrame con datos climáticos
            variable: Variable a graficar
            output_path: Ruta para guardar el gráfico (opcional)

        Returns:
            Figura de Plotly
        """
        try:
            if variable not in df.columns:
                raise ValueError(f"Variable '{variable}' no encontrada")

            fig = go.Figure()

            # Histograma
            fig.add_trace(
                go.Histogram(x=df[variable], nbinsx=30, name="Histograma", opacity=0.7)
            )

            # Agregar línea de densidad
            fig.add_trace(
                go.Scatter(
                    x=df[variable].sort_values(),
                    y=df[variable].value_counts(bins=30).sort_index(),
                    mode="lines",
                    name="Densidad",
                    line=dict(color="red", width=2),
                )
            )

            fig.update_layout(
                title=f"Distribución de {variable}",
                xaxis_title=variable,
                yaxis_title="Frecuencia",
                template="plotly_white",
            )

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Gráfico guardado en: {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creando gráfico de distribución: {str(e)}")
            raise

    def create_box_plot(
        self,
        df: pd.DataFrame,
        variable: str,
        group_by: str = None,
        output_path: str = None,
    ) -> go.Figure:
        """
        Crea gráfico de cajas para una variable climática.

        Args:
            df: DataFrame con datos climáticos
            variable: Variable a graficar
            group_by: Variable para agrupar (opcional)
            output_path: Ruta para guardar el gráfico (opcional)

        Returns:
            Figura de Plotly
        """
        try:
            if variable not in df.columns:
                raise ValueError(f"Variable '{variable}' no encontrada")

            if group_by and group_by not in df.columns:
                raise ValueError(f"Variable de agrupación '{group_by}' no encontrada")

            if group_by:
                fig = px.box(
                    df,
                    x=group_by,
                    y=variable,
                    title=f"Distribución de {variable} por {group_by}",
                    color=group_by,
                )
            else:
                fig = px.box(df, y=variable, title=f"Distribución de {variable}")

            fig.update_layout(template="plotly_white", showlegend=False)

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Gráfico guardado en: {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creando gráfico de cajas: {str(e)}")
            raise

    def create_correlation_heatmap(
        self, df: pd.DataFrame, output_path: str = None
    ) -> go.Figure:
        """
        Crea mapa de calor de correlaciones.

        Args:
            df: DataFrame con datos climáticos
            output_path: Ruta para guardar el gráfico (opcional)

        Returns:
            Figura de Plotly
        """
        try:
            # Seleccionar solo variables numéricas
            numeric_columns = df.select_dtypes(include=[np.number]).columns

            if len(numeric_columns) < 2:
                raise ValueError("Se necesitan al menos 2 variables numéricas")

            correlation_matrix = df[numeric_columns].corr()

            fig = px.imshow(
                correlation_matrix,
                text_auto=True,
                aspect="auto",
                title="Matriz de Correlación",
                color_continuous_scale="RdBu_r",
            )

            fig.update_layout(template="plotly_white")

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Gráfico guardado en: {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creando mapa de calor: {str(e)}")
            raise

    def create_scatter_plot(
        self,
        df: pd.DataFrame,
        x_var: str,
        y_var: str,
        color_by: str = None,
        output_path: str = None,
    ) -> go.Figure:
        """
        Crea gráfico de dispersión.

        Args:
            df: DataFrame con datos climáticos
            x_var: Variable del eje X
            y_var: Variable del eje Y
            color_by: Variable para colorear (opcional)
            output_path: Ruta para guardar el gráfico (opcional)

        Returns:
            Figura de Plotly
        """
        try:
            if x_var not in df.columns or y_var not in df.columns:
                raise ValueError(f"Variables '{x_var}' o '{y_var}' no encontradas")

            if color_by and color_by not in df.columns:
                raise ValueError(f"Variable de color '{color_by}' no encontrada")

            if color_by:
                fig = px.scatter(
                    df,
                    x=x_var,
                    y=y_var,
                    color=color_by,
                    title=f"{y_var} vs {x_var}",
                    hover_data=[color_by],
                )
            else:
                fig = px.scatter(df, x=x_var, y=y_var, title=f"{y_var} vs {x_var}")

            fig.update_layout(template="plotly_white")

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Gráfico guardado en: {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creando gráfico de dispersión: {str(e)}")
            raise

    def create_multi_panel_dashboard(
        self, df: pd.DataFrame, variables: List[str], output_path: str = None
    ) -> go.Figure:
        """
        Crea dashboard con múltiples paneles.

        Args:
            df: DataFrame con datos climáticos
            variables: Lista de variables a graficar
            output_path: Ruta para guardar el gráfico (opcional)

        Returns:
            Figura de Plotly
        """
        try:
            # Verificar variables disponibles
            available_vars = [var for var in variables if var in df.columns]
            if not available_vars:
                raise ValueError(
                    "Ninguna de las variables especificadas está disponible"
                )

            # Determinar layout
            n_vars = len(available_vars)
            n_cols = min(3, n_vars)
            n_rows = (n_vars + n_cols - 1) // n_cols

            fig = make_subplots(
                rows=n_rows,
                cols=n_cols,
                subplot_titles=available_vars,
                specs=[[{"secondary_y": False}] * n_cols] * n_rows,
            )

            # Agregar gráficos
            for i, var in enumerate(available_vars):
                row = i // n_cols + 1
                col = i % n_cols + 1

                fig.add_trace(
                    go.Histogram(x=df[var], name=var, showlegend=False),
                    row=row,
                    col=col,
                )

            fig.update_layout(
                title="Dashboard de Variables Climáticas",
                template="plotly_white",
                height=300 * n_rows,
            )

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Dashboard guardado en: {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creando dashboard: {str(e)}")
            raise

    def create_anomaly_plot(
        self,
        df: pd.DataFrame,
        variable: str,
        method: str = "iqr",
        output_path: str = None,
    ) -> go.Figure:
        """
        Crea gráfico de detección de anomalías.

        Args:
            df: DataFrame con datos climáticos
            variable: Variable a analizar
            method: Método de detección ('iqr', 'zscore')
            output_path: Ruta para guardar el gráfico (opcional)

        Returns:
            Figura de Plotly
        """
        try:
            if variable not in df.columns:
                raise ValueError(f"Variable '{variable}' no encontrada")

            fig = go.Figure()

            # Detectar anomalías
            if method == "iqr":
                Q1 = df[variable].quantile(0.25)
                Q3 = df[variable].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                normal_data = df[
                    (df[variable] >= lower_bound) & (df[variable] <= upper_bound)
                ]
                anomalies = df[
                    (df[variable] < lower_bound) | (df[variable] > upper_bound)
                ]

            elif method == "zscore":
                z_scores = np.abs(
                    (df[variable] - df[variable].mean()) / df[variable].std()
                )
                threshold = 3

                normal_data = df[z_scores <= threshold]
                anomalies = df[z_scores > threshold]

            else:
                raise ValueError(f"Método '{method}' no soportado")

            # Datos normales
            fig.add_trace(
                go.Scatter(
                    x=normal_data.index,
                    y=normal_data[variable],
                    mode="markers",
                    name="Datos Normales",
                    marker=dict(color="blue", size=6),
                )
            )

            # Anomalías
            if len(anomalies) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=anomalies.index,
                        y=anomalies[variable],
                        mode="markers",
                        name="Anomalías",
                        marker=dict(color="red", size=8, symbol="x"),
                    )
                )

            # Líneas de límites (solo para IQR)
            if method == "iqr":
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
                title=f"Detección de Anomalías - {variable} ({method.upper()})",
                xaxis_title="Índice",
                yaxis_title=variable,
                template="plotly_white",
            )

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Gráfico guardado en: {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creando gráfico de anomalías: {str(e)}")
            raise

    def save_plot_as_png(self, fig: go.Figure, output_path: str) -> str:
        """
        Guarda un gráfico de Plotly como imagen PNG.

        Args:
            fig: Figura de Plotly
            output_path: Ruta del archivo de salida

        Returns:
            Ruta del archivo guardado
        """
        try:
            # Crear directorio si no existe
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Guardar como PNG
            fig.write_image(output_path, width=1200, height=800)

            logger.info(f"Imagen guardada en: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error guardando imagen: {str(e)}")
            raise

    def create_summary_report_plots(
        self, df: pd.DataFrame, output_dir: str
    ) -> Dict[str, str]:
        """
        Crea un conjunto de gráficos para un reporte resumen.

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

            # 1. Distribuciones de variables principales
            numeric_columns = df.select_dtypes(include=[np.number]).columns[:6]

            for col in numeric_columns:
                if col in df.columns:
                    fig = self.create_distribution_plot(df, col)
                    plot_path = output_path / f"dist_{col}.html"
                    fig.write_html(str(plot_path))
                    plots[f"distribution_{col}"] = str(plot_path)

            # 2. Correlaciones
            if len(numeric_columns) > 1:
                fig = self.create_correlation_heatmap(df)
                corr_path = output_path / "correlation_heatmap.html"
                fig.write_html(str(corr_path))
                plots["correlation_heatmap"] = str(corr_path)

            # 3. Series temporales (si hay fecha)
            if "fecha" in df.columns:
                for col in numeric_columns[:3]:  # Solo las primeras 3 variables
                    if col in df.columns:
                        fig = self.create_time_series_plot(df, col)
                        ts_path = output_path / f"timeseries_{col}.html"
                        fig.write_html(str(ts_path))
                        plots[f"timeseries_{col}"] = str(ts_path)

            # 4. Box plots por estación (si hay datos de estación)
            if "estacion" in df.columns and len(df["estacion"].unique()) <= 10:
                for col in numeric_columns[:2]:  # Solo las primeras 2 variables
                    if col in df.columns:
                        fig = self.create_box_plot(df, col, "estacion")
                        box_path = output_path / f"boxplot_{col}_by_station.html"
                        fig.write_html(str(box_path))
                        plots[f"boxplot_{col}_by_station"] = str(box_path)

            return plots

        except Exception as e:
            logger.error(f"Error creando gráficos de reporte: {str(e)}")
            raise

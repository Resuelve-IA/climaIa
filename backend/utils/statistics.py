"""
Utilidades de análisis estadístico para datos climáticos.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
import warnings

logger = logging.getLogger(__name__)


class StatisticalAnalyzer:
    """Clase para análisis estadístico de datos climáticos."""

    def __init__(self):
        warnings.filterwarnings("ignore", category=RuntimeWarning)

    def calculate_descriptive_statistics(
        self, df: pd.DataFrame, variables: List[str] = None
    ) -> Dict[str, Any]:
        """
        Calcula estadísticas descriptivas para variables climáticas.

        Args:
            df: DataFrame con datos climáticos
            variables: Lista de variables a analizar (opcional)

        Returns:
            Diccionario con estadísticas descriptivas
        """
        try:
            if variables is None:
                variables = df.select_dtypes(include=[np.number]).columns.tolist()

            stats_dict = {}

            for var in variables:
                if var in df.columns:
                    data = df[var].dropna()

                    if len(data) > 0:
                        stats_dict[var] = {
                            "count": int(data.count()),
                            "mean": float(data.mean()),
                            "std": float(data.std()),
                            "min": float(data.min()),
                            "max": float(data.max()),
                            "median": float(data.median()),
                            "q25": float(data.quantile(0.25)),
                            "q75": float(data.quantile(0.75)),
                            "skewness": float(data.skew()),
                            "kurtosis": float(data.kurtosis()),
                            "missing_count": int(df[var].isnull().sum()),
                            "missing_percentage": float(
                                (df[var].isnull().sum() / len(df)) * 100
                            ),
                        }

            return stats_dict

        except Exception as e:
            logger.error(f"Error calculando estadísticas descriptivas: {str(e)}")
            raise

    def perform_normality_test(
        self, df: pd.DataFrame, variables: List[str] = None
    ) -> Dict[str, Any]:
        """
        Realiza pruebas de normalidad para variables climáticas.

        Args:
            df: DataFrame con datos climáticos
            variables: Lista de variables a analizar (opcional)

        Returns:
            Diccionario con resultados de pruebas de normalidad
        """
        try:
            if variables is None:
                variables = df.select_dtypes(include=[np.number]).columns.tolist()

            normality_results = {}

            for var in variables:
                if var in df.columns:
                    data = df[var].dropna()

                    if len(data) > 3:  # Mínimo 3 observaciones para pruebas
                        # Test de Shapiro-Wilk
                        try:
                            shapiro_stat, shapiro_p = stats.shapiro(data)
                            normality_results[var] = {
                                "shapiro_wilk": {
                                    "statistic": float(shapiro_stat),
                                    "p_value": float(shapiro_p),
                                    "is_normal": shapiro_p > 0.05,
                                }
                            }
                        except:
                            normality_results[var] = {
                                "shapiro_wilk": {
                                    "statistic": None,
                                    "p_value": None,
                                    "is_normal": None,
                                }
                            }

                        # Test de Kolmogorov-Smirnov
                        try:
                            ks_stat, ks_p = stats.kstest(
                                data, "norm", args=(data.mean(), data.std())
                            )
                            normality_results[var]["kolmogorov_smirnov"] = {
                                "statistic": float(ks_stat),
                                "p_value": float(ks_p),
                                "is_normal": ks_p > 0.05,
                            }
                        except:
                            normality_results[var]["kolmogorov_smirnov"] = {
                                "statistic": None,
                                "p_value": None,
                                "is_normal": None,
                            }

            return normality_results

        except Exception as e:
            logger.error(f"Error realizando pruebas de normalidad: {str(e)}")
            raise

    def calculate_correlations(
        self, df: pd.DataFrame, variables: List[str] = None, method: str = "pearson"
    ) -> Dict[str, Any]:
        """
        Calcula correlaciones entre variables climáticas.

        Args:
            df: DataFrame con datos climáticos
            variables: Lista de variables a analizar (opcional)
            method: Método de correlación ('pearson', 'spearman', 'kendall')

        Returns:
            Diccionario con matrices de correlación
        """
        try:
            if variables is None:
                variables = df.select_dtypes(include=[np.number]).columns.tolist()

            if len(variables) < 2:
                return {"error": "Se necesitan al menos 2 variables numéricas"}

            # Filtrar variables disponibles
            available_vars = [var for var in variables if var in df.columns]

            if len(available_vars) < 2:
                return {"error": "Menos de 2 variables disponibles"}

            # Calcular correlaciones
            if method == "pearson":
                corr_matrix = df[available_vars].corr(method="pearson")
            elif method == "spearman":
                corr_matrix = df[available_vars].corr(method="spearman")
            elif method == "kendall":
                corr_matrix = df[available_vars].corr(method="kendall")
            else:
                raise ValueError(f"Método '{method}' no soportado")

            # Calcular p-values para correlaciones significativas
            p_values = {}
            for i, var1 in enumerate(available_vars):
                for j, var2 in enumerate(available_vars):
                    if i < j:  # Solo triangular superior
                        data1 = df[var1].dropna()
                        data2 = df[var2].dropna()

                        # Alinear datos
                        common_idx = data1.index.intersection(data2.index)
                        if len(common_idx) > 3:
                            try:
                                if method == "pearson":
                                    _, p_val = pearsonr(
                                        data1[common_idx], data2[common_idx]
                                    )
                                elif method == "spearman":
                                    _, p_val = spearmanr(
                                        data1[common_idx], data2[common_idx]
                                    )
                                elif method == "kendall":
                                    _, p_val = kendalltau(
                                        data1[common_idx], data2[common_idx]
                                    )

                                p_values[f"{var1}_{var2}"] = float(p_val)
                            except:
                                p_values[f"{var1}_{var2}"] = None

            return {
                "correlation_matrix": corr_matrix.to_dict(),
                "p_values": p_values,
                "method": method,
                "variables": available_vars,
            }

        except Exception as e:
            logger.error(f"Error calculando correlaciones: {str(e)}")
            raise

    def perform_trend_analysis(self, df: pd.DataFrame, variable: str) -> Dict[str, Any]:
        """
        Realiza análisis de tendencias para una variable climática.

        Args:
            df: DataFrame con datos climáticos
            variable: Variable a analizar

        Returns:
            Diccionario con resultados del análisis de tendencias
        """
        try:
            if variable not in df.columns:
                raise ValueError(f"Variable '{variable}' no encontrada")

            if "fecha" not in df.columns:
                return {
                    "error": "Columna de fecha requerida para análisis de tendencias"
                }

            df_temp = df.copy()
            df_temp["fecha"] = pd.to_datetime(df_temp["fecha"])
            df_temp = df_temp.sort_values("fecha")

            # Preparar datos
            data = df_temp[[variable, "fecha"]].dropna()

            if len(data) < 3:
                return {"error": "Insuficientes datos para análisis de tendencias"}

            # Convertir fechas a números para regresión
            data["fecha_num"] = (data["fecha"] - data["fecha"].min()).dt.days

            # Regresión lineal
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                data["fecha_num"], data[variable]
            )

            # Calcular R²
            r_squared = r_value**2

            # Test de Mann-Kendall para tendencia
            try:
                mk_result = self._mann_kendall_test(data[variable])
            except:
                mk_result = {"statistic": None, "p_value": None, "trend": None}

            # Análisis estacional (simplificado)
            seasonal_analysis = self._analyze_seasonality(data, variable)

            return {
                "linear_trend": {
                    "slope": float(slope),
                    "intercept": float(intercept),
                    "r_squared": float(r_squared),
                    "p_value": float(p_value),
                    "std_error": float(std_err),
                    "trend_direction": "increasing" if slope > 0 else "decreasing",
                    "trend_significance": p_value < 0.05,
                },
                "mann_kendall": mk_result,
                "seasonal_analysis": seasonal_analysis,
                "data_points": len(data),
                "date_range": {
                    "start": data["fecha"].min().isoformat(),
                    "end": data["fecha"].max().isoformat(),
                    "duration_days": (data["fecha"].max() - data["fecha"].min()).days,
                },
            }

        except Exception as e:
            logger.error(f"Error en análisis de tendencias: {str(e)}")
            raise

    def _mann_kendall_test(self, data: pd.Series) -> Dict[str, Any]:
        """Implementación simplificada del test de Mann-Kendall."""
        try:
            n = len(data)
            if n < 3:
                return {"statistic": None, "p_value": None, "trend": None}

            # Calcular estadístico S
            s = 0
            for i in range(n):
                for j in range(i + 1, n):
                    if data.iloc[j] > data.iloc[i]:
                        s += 1
                    elif data.iloc[j] < data.iloc[i]:
                        s -= 1

            # Calcular varianza
            var_s = n * (n - 1) * (2 * n + 5) / 18

            # Calcular Z
            if s > 0:
                z = (s - 1) / np.sqrt(var_s)
            elif s < 0:
                z = (s + 1) / np.sqrt(var_s)
            else:
                z = 0

            # P-value aproximado (distribución normal)
            p_value = 2 * (1 - stats.norm.cdf(abs(z)))

            # Determinar tendencia
            if p_value < 0.05:
                trend = "increasing" if s > 0 else "decreasing"
            else:
                trend = "no_trend"

            return {
                "statistic": float(s),
                "z_score": float(z),
                "p_value": float(p_value),
                "trend": trend,
            }

        except Exception as e:
            logger.error(f"Error en test de Mann-Kendall: {str(e)}")
            return {"statistic": None, "p_value": None, "trend": None}

    def _analyze_seasonality(self, df: pd.DataFrame, variable: str) -> Dict[str, Any]:
        """Analiza patrones estacionales en los datos."""
        try:
            df_temp = df.copy()
            df_temp["month"] = df_temp["fecha"].dt.month
            df_temp["year"] = df_temp["fecha"].dt.year

            # Estadísticas por mes
            monthly_stats = (
                df_temp.groupby("month")[variable]
                .agg(["count", "mean", "std", "min", "max"])
                .to_dict("index")
            )

            # Encontrar mes con valores máximos y mínimos
            monthly_means = df_temp.groupby("month")[variable].mean()
            max_month = monthly_means.idxmax()
            min_month = monthly_means.idxmin()

            # Calcular amplitud estacional
            seasonal_amplitude = monthly_means.max() - monthly_means.min()

            return {
                "monthly_statistics": monthly_stats,
                "peak_month": int(max_month),
                "lowest_month": int(min_month),
                "seasonal_amplitude": float(seasonal_amplitude),
                "monthly_means": monthly_means.to_dict(),
            }

        except Exception as e:
            logger.error(f"Error analizando estacionalidad: {str(e)}")
            return {}

    def detect_outliers(
        self, df: pd.DataFrame, variables: List[str] = None, method: str = "iqr"
    ) -> Dict[str, Any]:
        """
        Detecta outliers en variables climáticas.

        Args:
            df: DataFrame con datos climáticos
            variables: Lista de variables a analizar (opcional)
            method: Método de detección ('iqr', 'zscore', 'isolation_forest')

        Returns:
            Diccionario con información de outliers
        """
        try:
            if variables is None:
                variables = df.select_dtypes(include=[np.number]).columns.tolist()

            outliers_results = {}

            for var in variables:
                if var in df.columns:
                    data = df[var].dropna()

                    if len(data) < 10:
                        outliers_results[var] = {"error": "Insuficientes datos"}
                        continue

                    if method == "iqr":
                        outliers_info = self._detect_outliers_iqr(data)
                    elif method == "zscore":
                        outliers_info = self._detect_outliers_zscore(data)
                    elif method == "isolation_forest":
                        outliers_info = self._detect_outliers_isolation_forest(data)
                    else:
                        raise ValueError(f"Método '{method}' no soportado")

                    outliers_results[var] = outliers_info

            return outliers_results

        except Exception as e:
            logger.error(f"Error detectando outliers: {str(e)}")
            raise

    def _detect_outliers_iqr(self, data: pd.Series) -> Dict[str, Any]:
        """Detecta outliers usando método IQR."""
        try:
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = data[(data < lower_bound) | (data > upper_bound)]

            return {
                "method": "iqr",
                "outliers_count": len(outliers),
                "outliers_percentage": float((len(outliers) / len(data)) * 100),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "outlier_indices": outliers.index.tolist(),
                "outlier_values": outliers.tolist(),
            }

        except Exception as e:
            logger.error(f"Error en detección IQR: {str(e)}")
            return {"error": str(e)}

    def _detect_outliers_zscore(self, data: pd.Series) -> Dict[str, Any]:
        """Detecta outliers usando Z-score."""
        try:
            z_scores = np.abs((data - data.mean()) / data.std())
            threshold = 3

            outliers = data[z_scores > threshold]

            return {
                "method": "zscore",
                "outliers_count": len(outliers),
                "outliers_percentage": float((len(outliers) / len(data)) * 100),
                "threshold": threshold,
                "outlier_indices": outliers.index.tolist(),
                "outlier_values": outliers.tolist(),
            }

        except Exception as e:
            logger.error(f"Error en detección Z-score: {str(e)}")
            return {"error": str(e)}

    def _detect_outliers_isolation_forest(self, data: pd.Series) -> Dict[str, Any]:
        """Detecta outliers usando Isolation Forest."""
        try:
            from sklearn.ensemble import IsolationForest

            # Preparar datos
            X = data.values.reshape(-1, 1)

            # Aplicar Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            predictions = iso_forest.fit_predict(X)

            # Identificar outliers
            outlier_mask = predictions == -1
            outliers = data[outlier_mask]

            return {
                "method": "isolation_forest",
                "outliers_count": len(outliers),
                "outliers_percentage": float((len(outliers) / len(data)) * 100),
                "outlier_indices": outliers.index.tolist(),
                "outlier_values": outliers.tolist(),
            }

        except ImportError:
            logger.warning(
                "scikit-learn no disponible, usando método IQR como fallback"
            )
            return self._detect_outliers_iqr(data)
        except Exception as e:
            logger.error(f"Error en detección Isolation Forest: {str(e)}")
            return {"error": str(e)}

    def perform_station_comparison(
        self, df: pd.DataFrame, variable: str
    ) -> Dict[str, Any]:
        """
        Realiza comparación estadística entre estaciones.

        Args:
            df: DataFrame con datos climáticos
            variable: Variable a comparar

        Returns:
            Diccionario con resultados de comparación
        """
        try:
            if variable not in df.columns or "estacion" not in df.columns:
                raise ValueError(
                    "Se requieren columnas 'estacion' y la variable especificada"
                )

            # Estadísticas por estación
            station_stats = (
                df.groupby("estacion")[variable]
                .agg(["count", "mean", "std", "min", "max", "median"])
                .to_dict("index")
            )

            # Test ANOVA para diferencias entre estaciones
            stations = df["estacion"].unique()
            if len(stations) > 1:
                station_groups = [
                    df[df["estacion"] == station][variable].dropna()
                    for station in stations
                ]

                # Filtrar grupos con suficientes datos
                valid_groups = [group for group in station_groups if len(group) > 1]

                if len(valid_groups) > 1:
                    try:
                        f_stat, p_value = stats.f_oneway(*valid_groups)
                        anova_result = {
                            "f_statistic": float(f_stat),
                            "p_value": float(p_value),
                            "significant_difference": p_value < 0.05,
                        }
                    except:
                        anova_result = {"error": "No se pudo calcular ANOVA"}
                else:
                    anova_result = {"error": "Insuficientes datos para ANOVA"}
            else:
                anova_result = {"error": "Solo una estación disponible"}

            return {
                "station_statistics": station_stats,
                "anova_test": anova_result,
                "total_stations": len(stations),
                "variable": variable,
            }

        except Exception as e:
            logger.error(f"Error en comparación de estaciones: {str(e)}")
            raise

    def generate_statistical_report(
        self, df: pd.DataFrame, variables: List[str] = None
    ) -> str:
        """
        Genera un reporte estadístico completo.

        Args:
            df: DataFrame con datos climáticos
            variables: Lista de variables a analizar (opcional)

        Returns:
            Reporte estadístico en formato texto
        """
        try:
            if variables is None:
                variables = df.select_dtypes(include=[np.number]).columns.tolist()

            report_lines = []
            report_lines.append("REPORTE ESTADÍSTICO - ANÁLISIS CLIMÁTICO")
            report_lines.append("=" * 50)
            report_lines.append("")

            # Estadísticas descriptivas
            report_lines.append("1. ESTADÍSTICAS DESCRIPTIVAS")
            report_lines.append("-" * 30)

            desc_stats = self.calculate_descriptive_statistics(df, variables)
            for var, stats in desc_stats.items():
                report_lines.append(f"\nVariable: {var}")
                report_lines.append(f"  - N: {stats['count']}")
                report_lines.append(f"  - Media: {stats['mean']:.2f}")
                report_lines.append(f"  - Desv. Est.: {stats['std']:.2f}")
                report_lines.append(f"  - Mín: {stats['min']:.2f}")
                report_lines.append(f"  - Máx: {stats['max']:.2f}")
                report_lines.append(
                    f"  - Datos faltantes: {stats['missing_percentage']:.1f}%"
                )

            # Pruebas de normalidad
            report_lines.append("\n\n2. PRUEBAS DE NORMALIDAD")
            report_lines.append("-" * 30)

            normality_results = self.perform_normality_test(df, variables)
            for var, results in normality_results.items():
                report_lines.append(f"\nVariable: {var}")
                if "shapiro_wilk" in results:
                    sw = results["shapiro_wilk"]
                    if sw["p_value"] is not None:
                        report_lines.append(
                            f"  - Shapiro-Wilk: p = {sw['p_value']:.4f}"
                        )
                        report_lines.append(
                            f"  - Normal: {'Sí' if sw['is_normal'] else 'No'}"
                        )

            # Correlaciones
            if len(variables) > 1:
                report_lines.append("\n\n3. CORRELACIONES")
                report_lines.append("-" * 30)

                corr_results = self.calculate_correlations(df, variables, "pearson")
                if "correlation_matrix" in corr_results:
                    report_lines.append("\nCorrelaciones significativas (p < 0.05):")
                    for pair, p_val in corr_results["p_values"].items():
                        if p_val is not None and p_val < 0.05:
                            report_lines.append(f"  - {pair}: p = {p_val:.4f}")

            report_lines.append("\n\n" + "=" * 50)
            report_lines.append("Fin del Reporte")

            return "\n".join(report_lines)

        except Exception as e:
            logger.error(f"Error generando reporte estadístico: {str(e)}")
            return f"Error generando reporte: {str(e)}"

"""
Servicio de análisis exploratorio de datos climáticos.
Realiza análisis estadísticos, visualizaciones y reportes de datos meteorológicos.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

from backend.models.database import WeatherData, Station, AnalysisResult
from backend.config.database import get_db
from backend.utils.visualization import PlotGenerator
from backend.utils.statistics import StatisticalAnalyzer

logger = logging.getLogger(__name__)


class ExploratoryAnalysisService:
    """Servicio para análisis exploratorio de datos climáticos."""
    
    def __init__(self):
        self.plot_generator = PlotGenerator()
        self.stat_analyzer = StatisticalAnalyzer()
        
        # Configurar estilo de gráficos
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def perform_complete_eda(self, df: pd.DataFrame, output_dir: str) -> Dict[str, Any]:
        """
        Realiza un análisis exploratorio completo de los datos climáticos.
        
        Args:
            df: DataFrame con datos climáticos
            output_dir: Directorio para guardar resultados
            
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            logger.info("Iniciando análisis exploratorio completo")
            
            # Crear directorio de salida
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            results = {
                'summary': self._generate_data_summary(df),
                'statistics': self._calculate_descriptive_statistics(df),
                'temporal_analysis': self._analyze_temporal_patterns(df),
                'correlation_analysis': self._analyze_correlations(df),
                'seasonal_analysis': self._analyze_seasonal_patterns(df),
                'station_analysis': self._analyze_station_data(df),
                'anomaly_analysis': self._detect_and_analyze_anomalies(df),
                'quality_report': self._generate_data_quality_report(df),
                'visualizations': self._generate_eda_visualizations(df, output_path),
                'recommendations': self._generate_recommendations(df)
            }
            
            # Guardar resultados
            self._save_analysis_results(results, output_path)
            
            logger.info("Análisis exploratorio completado")
            return results
            
        except Exception as e:
            logger.error(f"Error en análisis exploratorio: {str(e)}")
            raise
    
    def _generate_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Genera un resumen general de los datos."""
        
        summary = {
            'total_records': len(df),
            'date_range': {
                'start': df['fecha'].min().isoformat() if 'fecha' in df.columns else None,
                'end': df['fecha'].max().isoformat() if 'fecha' in df.columns else None
            },
            'stations_count': df['estacion'].nunique() if 'estacion' in df.columns else 0,
            'variables_count': len(df.select_dtypes(include=[np.number]).columns),
            'missing_data_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            'columns_info': {}
        }
        
        # Información de columnas
        for col in df.columns:
            summary['columns_info'][col] = {
                'dtype': str(df[col].dtype),
                'non_null_count': df[col].count(),
                'null_count': df[col].isnull().sum(),
                'unique_values': df[col].nunique()
            }
        
        return summary
    
    def _calculate_descriptive_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula estadísticas descriptivas detalladas."""
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        stats = {}
        
        for col in numeric_columns:
            if col in df.columns:
                col_data = df[col].dropna()
                
                if len(col_data) > 0:
                    stats[col] = {
                        'count': int(col_data.count()),
                        'mean': float(col_data.mean()),
                        'std': float(col_data.std()),
                        'min': float(col_data.min()),
                        'max': float(col_data.max()),
                        'median': float(col_data.median()),
                        'q25': float(col_data.quantile(0.25)),
                        'q75': float(col_data.quantile(0.75)),
                        'skewness': float(col_data.skew()),
                        'kurtosis': float(col_data.kurtosis()),
                        'missing_percentage': float((df[col].isnull().sum() / len(df)) * 100)
                    }
        
        return stats
    
    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza patrones temporales en los datos."""
        
        if 'fecha' not in df.columns:
            return {'error': 'Columna de fecha no encontrada'}
        
        df_temp = df.copy()
        df_temp['fecha'] = pd.to_datetime(df_temp['fecha'])
        df_temp = df_temp.sort_values('fecha')
        
        # Agregar columnas temporales
        df_temp['year'] = df_temp['fecha'].dt.year
        df_temp['month'] = df_temp['fecha'].dt.month
        df_temp['day_of_year'] = df_temp['fecha'].dt.dayofyear
        df_temp['season'] = df_temp['fecha'].dt.month.map({
            12: 'Verano', 1: 'Verano', 2: 'Verano',
            3: 'Otoño', 4: 'Otoño', 5: 'Otoño',
            6: 'Invierno', 7: 'Invierno', 8: 'Invierno',
            9: 'Primavera', 10: 'Primavera', 11: 'Primavera'
        })
        
        analysis = {
            'temporal_coverage': {
                'years_covered': df_temp['year'].nunique(),
                'months_covered': df_temp['month'].nunique(),
                'date_range_days': (df_temp['fecha'].max() - df_temp['fecha'].min()).days
            },
            'seasonal_patterns': {},
            'monthly_patterns': {},
            'yearly_patterns': {}
        }
        
        # Análisis por estación
        numeric_columns = df_temp.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col in df_temp.columns and col not in ['year', 'month', 'day_of_year']:
                # Patrones estacionales
                seasonal_stats = df_temp.groupby('season')[col].agg(['mean', 'std', 'count']).to_dict()
                analysis['seasonal_patterns'][col] = seasonal_stats
                
                # Patrones mensuales
                monthly_stats = df_temp.groupby('month')[col].agg(['mean', 'std', 'count']).to_dict()
                analysis['monthly_patterns'][col] = monthly_stats
                
                # Patrones anuales
                yearly_stats = df_temp.groupby('year')[col].agg(['mean', 'std', 'count']).to_dict()
                analysis['yearly_patterns'][col] = yearly_stats
        
        return analysis
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza correlaciones entre variables climáticas."""
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) < 2:
            return {'error': 'Insuficientes variables numéricas para análisis de correlación'}
        
        # Calcular matriz de correlación
        correlation_matrix = df[numeric_columns].corr()
        
        # Encontrar correlaciones más fuertes
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.5:  # Correlación moderada o fuerte
                    strong_correlations.append({
                        'variable1': correlation_matrix.columns[i],
                        'variable2': correlation_matrix.columns[j],
                        'correlation': float(corr_value),
                        'strength': 'fuerte' if abs(corr_value) > 0.7 else 'moderada'
                    })
        
        # Ordenar por valor absoluto de correlación
        strong_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'strong_correlations': strong_correlations[:10],  # Top 10
            'overall_correlation_summary': {
                'mean_correlation': float(correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()),
                'max_correlation': float(correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].max()),
                'min_correlation': float(correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].min())
            }
        }
    
    def _analyze_seasonal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza patrones estacionales específicos."""
        
        if 'fecha' not in df.columns:
            return {'error': 'Columna de fecha no encontrada'}
        
        df_temp = df.copy()
        df_temp['fecha'] = pd.to_datetime(df_temp['fecha'])
        df_temp['month'] = df_temp['fecha'].dt.month
        df_temp['season'] = df_temp['fecha'].dt.month.map({
            12: 'Verano', 1: 'Verano', 2: 'Verano',
            3: 'Otoño', 4: 'Otoño', 5: 'Otoño',
            6: 'Invierno', 7: 'Invierno', 8: 'Invierno',
            9: 'Primavera', 10: 'Primavera', 11: 'Primavera'
        })
        
        analysis = {
            'seasonal_means': {},
            'seasonal_variability': {},
            'peak_seasons': {},
            'seasonal_trends': {}
        }
        
        numeric_columns = df_temp.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df_temp.columns and col not in ['month']:
                # Medias estacionales
                seasonal_means = df_temp.groupby('season')[col].mean().to_dict()
                analysis['seasonal_means'][col] = seasonal_means
                
                # Variabilidad estacional
                seasonal_std = df_temp.groupby('season')[col].std().to_dict()
                analysis['seasonal_variability'][col] = seasonal_std
                
                # Estación con valores máximos
                peak_season = df_temp.groupby('season')[col].mean().idxmax()
                analysis['peak_seasons'][col] = peak_season
                
                # Tendencias estacionales (simplificado)
                monthly_means = df_temp.groupby('month')[col].mean()
                if len(monthly_means) > 1:
                    trend = np.polyfit(range(len(monthly_means)), monthly_means.values, 1)[0]
                    analysis['seasonal_trends'][col] = {
                        'trend_slope': float(trend),
                        'trend_direction': 'incremental' if trend > 0 else 'decremental'
                    }
        
        return analysis
    
    def _analyze_station_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza datos por estación meteorológica."""
        
        if 'estacion' not in df.columns:
            return {'error': 'Columna de estación no encontrada'}
        
        analysis = {
            'station_summary': {},
            'station_comparison': {},
            'data_completeness': {},
            'station_quality': {}
        }
        
        # Resumen por estación
        station_counts = df['estacion'].value_counts().to_dict()
        analysis['station_summary'] = {
            'total_stations': len(station_counts),
            'stations_with_most_data': dict(list(station_counts.items())[:5]),
            'stations_with_least_data': dict(list(station_counts.items())[-5:])
        }
        
        # Comparación entre estaciones
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df.columns:
                station_means = df.groupby('estacion')[col].mean().to_dict()
                station_stds = df.groupby('estacion')[col].std().to_dict()
                
                analysis['station_comparison'][col] = {
                    'means_by_station': station_means,
                    'std_by_station': station_stds,
                    'station_with_highest_mean': max(station_means, key=station_means.get),
                    'station_with_lowest_mean': min(station_means, key=station_means.get)
                }
        
        # Completitud de datos por estación
        for station in df['estacion'].unique():
            station_data = df[df['estacion'] == station]
            completeness = (station_data.notnull().sum().sum() / (len(station_data) * len(station_data.columns))) * 100
            analysis['data_completeness'][station] = float(completeness)
        
        return analysis
    
    def _detect_and_analyze_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detecta y analiza anomalías en los datos."""
        
        analysis = {
            'anomaly_summary': {},
            'anomaly_details': {},
            'anomaly_patterns': {}
        }
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df.columns and df[col].notna().sum() > 10:
                # Detectar outliers usando IQR
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                
                analysis['anomaly_summary'][col] = {
                    'total_anomalies': len(outliers),
                    'anomaly_percentage': float((len(outliers) / len(df)) * 100),
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound)
                }
                
                if len(outliers) > 0:
                    analysis['anomaly_details'][col] = {
                        'min_anomaly_value': float(outliers[col].min()),
                        'max_anomaly_value': float(outliers[col].max()),
                        'anomaly_mean': float(outliers[col].mean())
                    }
        
        return analysis
    
    def _generate_data_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Genera un reporte de calidad de datos."""
        
        report = {
            'completeness': {},
            'consistency': {},
            'accuracy': {},
            'overall_quality_score': 0.0
        }
        
        # Completitud
        missing_data = df.isnull().sum()
        total_cells = len(df) * len(df.columns)
        completeness_score = ((total_cells - missing_data.sum()) / total_cells) * 100
        
        report['completeness'] = {
            'overall_completeness': float(completeness_score),
            'missing_data_by_column': missing_data.to_dict(),
            'columns_with_most_missing': missing_data.nlargest(5).to_dict()
        }
        
        # Consistencia (verificaciones básicas)
        consistency_issues = []
        
        if 'fecha' in df.columns:
            # Verificar que las fechas están en orden
            df_sorted = df.sort_values('fecha')
            if not df_sorted['fecha'].equals(df['fecha']):
                consistency_issues.append("Fechas no están en orden cronológico")
        
        # Verificar rangos de valores
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col in df.columns:
                if 'temperatura' in col.lower():
                    if df[col].min() < -50 or df[col].max() > 60:
                        consistency_issues.append(f"Valores de temperatura fuera de rango en {col}")
                elif 'humedad' in col.lower():
                    if df[col].min() < 0 or df[col].max() > 100:
                        consistency_issues.append(f"Valores de humedad fuera de rango en {col}")
        
        report['consistency'] = {
            'issues_found': consistency_issues,
            'consistency_score': max(0, 100 - len(consistency_issues) * 10)
        }
        
        # Calcular score general
        report['overall_quality_score'] = (completeness_score + report['consistency']['consistency_score']) / 2
        
        return report
    
    def _generate_eda_visualizations(self, df: pd.DataFrame, output_path: Path) -> Dict[str, str]:
        """Genera visualizaciones para el análisis exploratorio."""
        
        visualizations = {}
        
        try:
            # 1. Distribución de variables principales
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            numeric_columns = df.select_dtypes(include=[np.number]).columns[:6]
            
            for i, col in enumerate(numeric_columns):
                if col in df.columns:
                    row, col_idx = i // 3, i % 3
                    df[col].hist(ax=axes[row, col_idx], bins=30, alpha=0.7)
                    axes[row, col_idx].set_title(f'Distribución de {col}')
                    axes[row, col_idx].set_xlabel(col)
                    axes[row, col_idx].set_ylabel('Frecuencia')
            
            plt.tight_layout()
            dist_plot_path = output_path / 'distributions.png'
            plt.savefig(dist_plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            visualizations['distributions'] = str(dist_plot_path)
            
            # 2. Matriz de correlación
            if len(numeric_columns) > 1:
                correlation_matrix = df[numeric_columns].corr()
                plt.figure(figsize=(10, 8))
                sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                           square=True, linewidths=0.5)
                plt.title('Matriz de Correlación')
                plt.tight_layout()
                corr_plot_path = output_path / 'correlation_matrix.png'
                plt.savefig(corr_plot_path, dpi=300, bbox_inches='tight')
                plt.close()
                visualizations['correlation_matrix'] = str(corr_plot_path)
            
            # 3. Series temporales (si hay fecha)
            if 'fecha' in df.columns:
                df_temp = df.copy()
                df_temp['fecha'] = pd.to_datetime(df_temp['fecha'])
                df_temp = df_temp.sort_values('fecha')
                
                # Seleccionar una variable para mostrar
                temp_col = None
                for col in ['temperatura_promedio', 'temperatura_maxima', 'precipitacion']:
                    if col in df_temp.columns:
                        temp_col = col
                        break
                
                if temp_col:
                    plt.figure(figsize=(12, 6))
                    plt.plot(df_temp['fecha'], df_temp[temp_col], alpha=0.7)
                    plt.title(f'Serie Temporal - {temp_col}')
                    plt.xlabel('Fecha')
                    plt.ylabel(temp_col)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    time_series_path = output_path / 'time_series.png'
                    plt.savefig(time_series_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    visualizations['time_series'] = str(time_series_path)
            
            # 4. Box plots por estación (si hay datos de estación)
            if 'estacion' in df.columns and len(df['estacion'].unique()) <= 10:
                temp_col = None
                for col in ['temperatura_promedio', 'temperatura_maxima', 'precipitacion']:
                    if col in df.columns:
                        temp_col = col
                        break
                
                if temp_col:
                    plt.figure(figsize=(12, 6))
                    df.boxplot(column=temp_col, by='estacion', ax=plt.gca())
                    plt.title(f'Distribución de {temp_col} por Estación')
                    plt.suptitle('')  # Eliminar título automático
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    box_plot_path = output_path / 'box_plots.png'
                    plt.savefig(box_plot_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    visualizations['box_plots'] = str(box_plot_path)
            
        except Exception as e:
            logger.error(f"Error generando visualizaciones: {str(e)}")
            visualizations['error'] = str(e)
        
        return visualizations
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Genera recomendaciones basadas en el análisis."""
        
        recommendations = []
        
        # Verificar completitud de datos
        missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_percentage > 20:
            recommendations.append("Alto porcentaje de datos faltantes. Considerar estrategias de imputación.")
        
        # Verificar cobertura temporal
        if 'fecha' in df.columns:
            date_range = pd.to_datetime(df['fecha'].max()) - pd.to_datetime(df['fecha'].min())
            if date_range.days < 365:
                recommendations.append("Cobertura temporal limitada. Se recomienda extender el período de análisis.")
        
        # Verificar número de estaciones
        if 'estacion' in df.columns:
            station_count = df['estacion'].nunique()
            if station_count < 5:
                recommendations.append("Pocas estaciones meteorológicas. Considerar incluir más estaciones para mejor cobertura espacial.")
        
        # Verificar correlaciones
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 1:
            correlation_matrix = df[numeric_columns].corr()
            high_correlations = (correlation_matrix > 0.8).sum().sum() - len(correlation_matrix)
            if high_correlations > 0:
                recommendations.append("Se detectaron variables altamente correlacionadas. Considerar análisis de multicolinealidad.")
        
        if not recommendations:
            recommendations.append("Los datos muestran buena calidad general. Continuar con análisis más avanzados.")
        
        return recommendations
    
    def _save_analysis_results(self, results: Dict[str, Any], output_path: Path) -> None:
        """Guarda los resultados del análisis en archivos."""
        
        # Guardar resultados como JSON
        results_file = output_path / 'eda_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            # Convertir numpy types a Python types para JSON serialization
            json.dump(results, f, default=str, indent=2, ensure_ascii=False)
        
        # Generar reporte en texto
        report_file = output_path / 'eda_report.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("REPORTE DE ANÁLISIS EXPLORATORIO DE DATOS CLIMÁTICOS\n")
            f.write("=" * 60 + "\n\n")
            
            # Resumen
            f.write("RESUMEN GENERAL:\n")
            f.write(f"- Total de registros: {results['summary']['total_records']}\n")
            f.write(f"- Rango de fechas: {results['summary']['date_range']['start']} a {results['summary']['date_range']['end']}\n")
            f.write(f"- Número de estaciones: {results['summary']['stations_count']}\n")
            f.write(f"- Porcentaje de datos faltantes: {results['summary']['missing_data_percentage']:.2f}%\n\n")
            
            # Calidad de datos
            f.write("CALIDAD DE DATOS:\n")
            f.write(f"- Score general de calidad: {results['quality_report']['overall_quality_score']:.2f}%\n")
            f.write(f"- Completitud: {results['quality_report']['completeness']['overall_completeness']:.2f}%\n")
            f.write(f"- Consistencia: {results['quality_report']['consistency']['consistency_score']:.2f}%\n\n")
            
            # Recomendaciones
            f.write("RECOMENDACIONES:\n")
            for i, rec in enumerate(results['recommendations'], 1):
                f.write(f"{i}. {rec}\n")
        
        logger.info(f"Resultados guardados en: {output_path}")
    
    def generate_station_report(self, station_code: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Genera un reporte específico para una estación meteorológica.
        
        Args:
            station_code: Código de la estación
            df: DataFrame con datos climáticos
            
        Returns:
            Diccionario con reporte de la estación
        """
        try:
            if 'estacion' not in df.columns:
                raise ValueError("Columna 'estacion' no encontrada en los datos")
            
            station_data = df[df['estacion'] == station_code].copy()
            
            if len(station_data) == 0:
                raise ValueError(f"No se encontraron datos para la estación {station_code}")
            
            report = {
                'station_info': {
                    'code': station_code,
                    'total_records': len(station_data),
                    'date_range': {
                        'start': station_data['fecha'].min().isoformat() if 'fecha' in station_data.columns else None,
                        'end': station_data['fecha'].max().isoformat() if 'fecha' in station_data.columns else None
                    }
                },
                'statistics': self._calculate_descriptive_statistics(station_data),
                'temporal_analysis': self._analyze_temporal_patterns(station_data),
                'data_quality': self._generate_data_quality_report(station_data)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generando reporte de estación {station_code}: {str(e)}")
            raise 
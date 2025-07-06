# 🌤️ Análisis Climático de Cundinamarca

## 📋 Descripción del Proyecto

Este proyecto realiza un análisis exhaustivo de los datos climáticos de la región de Cundinamarca, Colombia. El sistema incluye extracción, procesamiento, análisis y visualización de datos meteorológicos para comprender patrones climáticos, identificar tendencias y proporcionar información útil para la toma de decisiones en agricultura, planificación urbana y gestión de riesgos.

## 🎯 Objetivos

- **Extracción y Limpieza de Datos**: Procesamiento de datos meteorológicos del IDEAM
- **Análisis Exploratorio**: Identificación de patrones y tendencias climáticas
- **Visualización**: Representación gráfica de información climática
- **Modelado**: Predicción de tendencias climáticas futuras
- **Informes**: Generación de reportes detallados con hallazgos

## 🏗️ Arquitectura del Sistema

```
climaIa/
├── backend/                 # Backend en Python
│   ├── api/                # API REST
│   ├── services/           # Lógica de negocio
│   ├── models/             # Modelos de datos
│   ├── utils/              # Utilidades
│   └── config/             # Configuración
├── frontend/               # Frontend (futuro)
├── data/                   # Datos y archivos
│   ├── raw/                # Datos crudos
│   ├── processed/          # Datos procesados
│   └── geo/                # Datos geoespaciales
├── notebooks/              # Jupyter notebooks
├── docs/                   # Documentación
└── tests/                  # Pruebas
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- PostgreSQL 12+
- Node.js 16+ (para frontend futuro)

### Instalación del Backend

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/climaIa.git
cd climaIa

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar migraciones
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

### Variables de Entorno

```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/climaia

# API Keys
SOCRATA_APP_TOKEN=tu_token_aqui
IDEAM_API_KEY=tu_api_key_aqui

# Configuración de la aplicación
DEBUG=True
SECRET_KEY=tu_secret_key_aqui
```

## 📊 Fuentes de Datos

### 1. IDEAM (Instituto de Hidrología, Meteorología y Estudios Ambientales)
- **URL**: https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Datos-Hidrometeorol-gicos-Crudos-Red-de-Estaciones/sbwg-7ju4
- **Descripción**: Datos hidrometeorológicos crudos de estaciones automáticas
- **Variables**: Temperatura, precipitación, humedad, presión atmosférica
- **Cobertura**: Cundinamarca, Colombia
- **Frecuencia**: Datos instantáneos

### 2. IGAC (Instituto Geográfico Agustín Codazzi)
- **URL**: https://www.colombiaenmapas.gov.co/
- **Descripción**: Cartografía vectorial básica de Colombia
- **Escala**: 1:100.000
- **Contenido**: Entidades territoriales, transporte, hidrografía, relieve

## 🔧 Funcionalidades

### 1. Extracción de Datos
- **API Socrata**: Extracción automática de datos meteorológicos
- **Filtros**: Por departamento (Cundinamarca) y fecha
- **Lotes**: Procesamiento en lotes para grandes volúmenes
- **Validación**: Verificación de integridad de datos

### 2. Procesamiento de Datos
- **Limpieza**: Eliminación de valores faltantes y outliers
- **Transformación**: Conversión de tipos de datos
- **Consolidación**: Unificación de múltiples archivos CSV
- **Validación**: Verificación de rangos y consistencia

### 3. Análisis Exploratorio
- **Tendencias Temporales**: Análisis por año y mes
- **Análisis Espacial**: Visualización geográfica de datos
- **Detección de Outliers**: Identificación de valores atípicos
- **Estadísticas Descriptivas**: Resúmenes estadísticos

### 4. Visualizaciones
- **Mapas de Calor**: Distribución espacial de variables climáticas
- **Gráficos Temporales**: Evolución de variables en el tiempo
- **Comparativas**: Análisis entre diferentes períodos
- **Interactivas**: Dashboards dinámicos

## 📈 Análisis Realizados

### Datos Procesados
- **Período**: 2023-2024
- **Estaciones**: Múltiples estaciones en Cundinamarca
- **Variables**: Temperatura del aire, precipitación, humedad
- **Registros**: +500,000 observaciones

### Hallazgos Principales
1. **Tendencias de Temperatura**: Análisis de variaciones estacionales
2. **Patrones de Precipitación**: Identificación de épocas lluviosas
3. **Distribución Espacial**: Variaciones geográficas en el departamento
4. **Valores Atípicos**: Detección de eventos climáticos extremos

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.8+**: Lenguaje principal
- **FastAPI**: Framework web para API
- **Pandas**: Manipulación de datos
- **NumPy**: Computación numérica
- **GeoPandas**: Procesamiento geoespacial
- **SQLAlchemy**: ORM para base de datos
- **PostgreSQL**: Base de datos principal

### Análisis de Datos
- **Matplotlib**: Visualizaciones básicas
- **Seaborn**: Visualizaciones estadísticas
- **Plotly**: Gráficos interactivos
- **Folium**: Mapas interactivos
- **Scikit-learn**: Machine Learning

### Herramientas
- **Jupyter Notebooks**: Análisis exploratorio
- **Docker**: Containerización
- **Git**: Control de versiones
- **Postman**: Pruebas de API

## 📁 Estructura de Archivos

```
climaIa/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── data.py
│   │   │   ├── analysis.py
│   │   │   └── visualization.py
│   │   └── main.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_extraction.py
│   │   ├── data_processing.py
│   │   ├── analysis_service.py
│   │   └── visualization_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── schemas.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_cleaner.py
│   │   ├── geo_utils.py
│   │   └── validators.py
│   └── config/
│       ├── __init__.py
│       ├── settings.py
│       └── database.py
├── data/
│   ├── raw/
│   │   ├── data_1.csv
│   │   ├── data_2.csv
│   │   └── ...
│   ├── processed/
│   │   └── datos_limpios_total.csv
│   └── geo/
│       ├── Servicio-93/
│       └── MGN2021_DPTO_POLITICO/
├── notebooks/
│   ├── 01_data_extraction.ipynb
│   ├── 02_data_processing.ipynb
│   ├── 03_exploratory_analysis.ipynb
│   └── 04_visualization.ipynb
├── docs/
│   ├── api_documentation.md
│   ├── data_dictionary.md
│   └── analysis_reports.md
├── tests/
│   ├── test_data_extraction.py
│   ├── test_data_processing.py
│   └── test_analysis.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🔌 API Endpoints

### Datos
- `GET /api/data/` - Listar todos los datos
- `GET /api/data/{station_id}` - Datos por estación
- `GET /api/data/date-range` - Datos por rango de fechas
- `POST /api/data/upload` - Subir nuevos datos

### Análisis
- `GET /api/analysis/temperature-trends` - Tendencias de temperatura
- `GET /api/analysis/precipitation-patterns` - Patrones de precipitación
- `GET /api/analysis/outliers` - Valores atípicos
- `GET /api/analysis/statistics` - Estadísticas descriptivas

### Visualizaciones
- `GET /api/visualization/heatmap` - Mapa de calor
- `GET /api/visualization/timeline` - Gráfico temporal
- `GET /api/visualization/geographic` - Visualización geográfica

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
python -m pytest

# Ejecutar pruebas específicas
python -m pytest tests/test_data_extraction.py

# Cobertura de código
python -m pytest --cov=backend
```

## 📊 Monitoreo y Logs

- **Logs**: Configurados en `backend/config/logging.py`
- **Métricas**: Monitoreo de rendimiento de la API
- **Alertas**: Notificaciones para errores críticos

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- **Edisson Giraldo** - *Desarrollo inicial* - [TuGitHub](https://github.com/tu-usuario)
- **Universidad Sergio Arboleda** - *Institución académica*
- **Talento Tech Mintic** - *Programa de formación*

## 🙏 Agradecimientos

- **IDEAM** por proporcionar los datos meteorológicos
- **IGAC** por los datos geoespaciales
- **Universidad Sergio Arboleda** por el apoyo académico
- **Mintic** por la formación en tecnologías emergentes

## 📞 Contacto

- **Email**: tu-email@ejemplo.com
- **LinkedIn**: [Tu Perfil](https://linkedin.com/in/tu-perfil)
- **GitHub**: [Tu Usuario](https://github.com/tu-usuario)

## 🔄 Estado del Proyecto

- ✅ Extracción de datos implementada
- ✅ Procesamiento de datos completado
- ✅ Análisis exploratorio realizado
- 🔄 Backend en desarrollo
- ⏳ Frontend pendiente
- ⏳ API REST en desarrollo
- ⏳ Documentación en progreso

---

**Última actualización**: Enero 2024
**Versión**: 1.0.0

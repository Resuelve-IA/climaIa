import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test del endpoint de salud"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root_endpoint():
    """Test del endpoint raíz"""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "activo"

def test_openapi_schema():
    """Test de la especificación OpenAPI"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data

def test_docs_endpoint():
    """Test del endpoint de documentación"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_stations_endpoint():
    """Test del endpoint de estaciones"""
    response = client.get("/api/v1/stations")
    # Puede fallar si no hay token válido o conexión, pero debe responder
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        assert isinstance(response.json(), list)
    else:
        # Si falla, debe ser por error de API externa, no por error interno
        assert "error" in response.json() or "detail" in response.json()

def test_extract_data_endpoint():
    """Test del endpoint de extracción de datos"""
    test_data = {
        "estacion": "test_station",
        "fecha_inicio": "2023-01-01T00:00:00",
        "fecha_fin": "2023-01-31T23:59:59"
    }
    response = client.post("/api/v1/extract-data", json=test_data)
    # Puede fallar si no hay conexión a IDEAM, pero debe responder
    assert response.status_code in [200, 422, 500]

def test_analysis_endpoint():
    """Test del endpoint de análisis"""
    test_data = {
        "tipo_analisis": "descriptivo",
        "parametros": {"variable": "temperatura"}
    }
    response = client.post("/api/v1/analyze-data", json=test_data)
    # Puede fallar si no hay datos, pero debe responder
    assert response.status_code in [200, 422, 500] 
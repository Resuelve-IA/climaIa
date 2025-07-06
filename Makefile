.PHONY: help install test lint format clean run api-test start

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-asyncio flake8 black isort

test: ## Ejecutar tests
	pytest tests/ -v --cov=backend --cov-report=term-missing

test-html: ## Ejecutar tests con reporte HTML
	pytest tests/ -v --cov=backend --cov-report=html
	@echo "Reporte de cobertura generado en htmlcov/index.html"

lint: ## Ejecutar linting
	flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics
	black --check backend/

format: ## Formatear código
	black backend/
	isort backend/

clean: ## Limpiar archivos temporales
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

run: ## Ejecutar la API
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001

run-8000: ## Ejecutar la API en puerto 8000
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

api-test: ## Probar endpoints de la API
	@echo "Probando endpoints de la API..."
	@curl -s http://localhost:8000/api/v1/health | jq . || echo "API no está corriendo"
	@curl -s http://localhost:8000/api/v1/ | jq . || echo "API no está corriendo"

setup: ## Configurar el proyecto
	mkdir -p data/raw data/processed data/geo logs tests
	cp env.example .env
	@echo "Proyecto configurado. Edita .env con tus credenciales."

ci: ## Ejecutar CI localmente
	make lint
	make test
	make api-test

all: ## Ejecutar todo el pipeline
	make format
	make lint
	make test
	make api-test

start: ## Iniciar API con detección automática de puerto
	./start_api.sh 
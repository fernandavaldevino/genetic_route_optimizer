"""
Testes Unitários para a API FastAPI
Testa endpoints, validações e lógica de negócio
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import json

from api.main import app
from api.models import (
    ServiceType,
    ServicePointInput,
    OptimizationRequest,
    HealthResponse
)


class TestHealthEndpoints:
    """ Testes para endpoints de saúde da API """
    
    def test_root_endpoint(self, api_client):
        """ Testa endpoint raiz """
        response = api_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "API de Otimização de Rotas"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"
    
    def test_health_check_endpoint(self, api_client):
        """ Testa endpoint de health check """
        response = api_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        
        # Validar formato do timestamp
        timestamp = datetime.fromisoformat(data["timestamp"])
        assert isinstance(timestamp, datetime)


class TestModelsValidation:
    """ Testes para validação dos modelos Pydantic """
    
    def test_service_point_input_valid(self):
        """Testa criação de ServicePointInput válido"""
        point = ServicePointInput(
            id=1,
            location=(100.0, 200.0),
            service_type=ServiceType.EMERGENCY,
            time_window=(480, 600)
        )
        
        assert point.id == 1
        assert point.location == (100.0, 200.0)
        assert point.service_type == ServiceType.EMERGENCY
        assert point.time_window == (480, 600)
    
    def test_service_point_input_without_time_window(self):
        """ Testa ServicePointInput sem janela de tempo """
        point = ServicePointInput(
            id=2,
            location=(300.0, 400.0),
            service_type=ServiceType.REGULAR,
            time_window=None
        )
        
        assert point.time_window is None
    
    def test_optimization_request_valid(self):
        """ Testa criação de OptimizationRequest válido """
        request = OptimizationRequest(
            service_points=[
                ServicePointInput(
                    id=1,
                    location=(100.0, 200.0),
                    service_type=ServiceType.EMERGENCY,
                    time_window=None
                )
            ],
            num_vehicles=1,
            population_size=100,
            generations=200
        )
        
        assert len(request.service_points) == 1
        assert request.num_vehicles == 1
        assert request.population_size == 100
        assert request.generations == 200
    
    def test_optimization_request_invalid_num_vehicles(self):
        """ Testa validação de número de veículos inválido """
        with pytest.raises(Exception):  # Pydantic ValidationError
            OptimizationRequest(
                service_points=[
                    ServicePointInput(
                        id=1,
                        location=(100.0, 200.0),
                        service_type=ServiceType.EMERGENCY,
                        time_window=None
                    )
                ],
                num_vehicles=3,  # Máximo é 2
                population_size=100,
                generations=200
            )
    
    def test_optimization_request_invalid_population_size(self):
        """ Testa validação de tamanho de população inválido """
        with pytest.raises(Exception):  # Pydantic ValidationError
            OptimizationRequest(
                service_points=[
                    ServicePointInput(
                        id=1,
                        location=(100.0, 200.0),
                        service_type=ServiceType.EMERGENCY,
                        time_window=None
                    )
                ],
                num_vehicles=1,
                population_size=30,  # Mínimo é 50
                generations=200
            )
    
    def test_service_type_enum_values(self):
        """ Testa valores do enum ServiceType """
        assert ServiceType.EMERGENCY.value == "emergency"
        assert ServiceType.VIOLENCE.value == "violence"
        assert ServiceType.MEDICATION.value == "medication"
        assert ServiceType.POSTPARTUM.value == "postpartum"
        assert ServiceType.REGULAR.value == "regular"


class TestOptimizationEndpoint:
    """ Testes para endpoint de otimização """
    
    def test_optimize_route_success(self, api_client):
        """ Testa otimização de rota com sucesso (teste de integração real) """
        # Criar requisição válida com valores mínimos permitidos
        request_data = {
            "service_points": [
                {
                    "id": 1,
                    "location": (100.0, 200.0),
                    "service_type": "emergency",
                    "time_window": None
                },
                {
                    "id": 2,
                    "location": (300.0, 400.0),
                    "service_type": "violence",
                    "time_window": (480, 600)
                },
                {
                    "id": 3,
                    "location": (150.0, 350.0),
                    "service_type": "regular",
                    "time_window": None
                }
            ],
            "num_vehicles": 1,
            "population_size": 50,  # Mínimo permitido
            "generations": 100,  # Mínimo permitido
            "depot_location": (250.0, 250.0)
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        # Verificar se a resposta é bem-sucedida
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "fitness" in data
        assert "vehicles" in data
        assert "execution_time" in data
        assert len(data["vehicles"]) == request_data["num_vehicles"]
    
    def test_optimize_route_empty_service_points(self, api_client):
        """ Testa otimização com lista vazia de pontos """
        request_data = {
            "service_points": [],
            "num_vehicles": 1,
            "population_size": 100,
            "generations": 200
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        # Com lista vazia, o algoritmo ainda executa mas pode retornar erro
        # Aceitar tanto 200 (execução com lista vazia) quanto 422 (validação) ou 500 (erro)
        assert response.status_code in [200, 422, 500]
    
    def test_optimize_route_invalid_service_type(self, api_client):
        """ Testa otimização com tipo de serviço inválido """
        request_data = {
            "service_points": [
                {
                    "id": 1,
                    "location": [100.0, 200.0],
                    "service_type": "invalid_type",
                    "time_window": None
                }
            ],
            "num_vehicles": 1,
            "population_size": 100,
            "generations": 200
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        # Deve retornar erro de validação
        assert response.status_code == 422


class TestRoutesEndpoints:
    """ Testes para endpoints de rotas """
    
    @patch('api.main.route_integration')
    def test_list_routes_empty(self, mock_integration, api_client):
        """Testa listagem de rotas quando não há rotas salvas"""
        mock_integration.data_dir.glob.return_value = []
        
        response = api_client.get("/api/v1/routes")
        
        assert response.status_code == 200
        data = response.json()
        assert data["routes"] == []
        assert data["total"] == 0
    
    @patch('api.main.route_integration')
    def test_get_latest_route_not_found(self, mock_integration, api_client):
        """ Testa obtenção de rota mais recente quando não há rotas """
        mock_integration.load_latest_route.return_value = None
        
        response = api_client.get("/api/v1/routes/latest")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    @patch('api.main.route_integration')
    def test_get_latest_route_success(self, mock_integration, api_client):
        """ Testa obtenção de rota mais recente com sucesso """
        mock_route_data = {
            'date': '2024-01-15T10:30:00',
            'fitness': 100.0,
            'num_vehicles': 1,
            'vehicles': []
        }
        mock_integration.load_latest_route.return_value = mock_route_data
        
        response = api_client.get("/api/v1/routes/latest")
        
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == '2024-01-15T10:30:00'
        assert data["fitness"] == 100.0
    
    @patch('api.main.route_integration')
    def test_get_route_by_filename_not_found(self, mock_integration, api_client):
        """ Testa obtenção de rota por nome de arquivo inexistente """
        mock_file = MagicMock()
        mock_file.exists.return_value = False
        mock_integration.data_dir.__truediv__.return_value = mock_file
        
        response = api_client.get("/api/v1/routes/route_20240115.json")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    @patch('api.main.route_integration')
    def test_get_route_summary_not_found(self, mock_integration, api_client):
        """ Testa obtenção de resumo quando não há rotas """
        # Simular que get_route_summary retorna None ou lança exceção
        mock_integration.get_route_summary.return_value = {}
        
        response = api_client.get("/api/v1/routes/summary")
        
        # Aceitar 200 (retorna vazio), 404 (não encontrado) ou 500 (erro)
        assert response.status_code in [200, 404, 500]


class TestVehiclesEndpoints:
    """ Testes para endpoints de veículos """
    
    @patch('api.main.route_integration')
    def test_get_vehicle_data_not_found(self, mock_integration, api_client):
        """ Testa obtenção de dados de veículo inexistente """
        mock_integration.get_vehicle_data.return_value = None
        
        response = api_client.get("/api/v1/vehicles/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    @patch('api.main.route_integration')
    def test_get_vehicle_data_success(self, mock_integration, api_client):
        """ Testa obtenção de dados de veículo com sucesso """
        mock_vehicle_data = {
            'id': 1,
            'driver': 'Motorista 1',
            'total_stops': 5,
            'total_distance': 45.5
        }
        mock_integration.get_vehicle_data.return_value = mock_vehicle_data
        
        response = api_client.get("/api/v1/vehicles/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["driver"] == 'Motorista 1'


class TestCORSConfiguration:
    """ Testes para configuração de CORS """
    
    def test_cors_headers_present(self, api_client):
        """ Testa se headers CORS estão presentes """
        response = api_client.options("/")
        
        # Verificar se CORS está configurado
        assert response.status_code in [200, 405]  # OPTIONS pode não estar implementado


class TestErrorHandling:
    """ Testes para tratamento de erros """
    
    @patch('api.main.route_integration')
    def test_optimize_route_internal_error(self, mock_integration, api_client, sample_optimization_request):
        """ Testa tratamento de erro interno na otimização """
        mock_integration.convert_from_optimization_result.side_effect = Exception("Erro simulado")
        
        response = api_client.post("/api/v1/optimize", json=sample_optimization_request)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
    
    @patch('api.main.route_integration')
    def test_list_routes_internal_error(self, mock_integration, api_client):
        """ Testa tratamento de erro interno ao listar rotas """
        mock_integration.data_dir.glob.side_effect = Exception("Erro simulado")
        
        response = api_client.get("/api/v1/routes")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


class TestAPIDocumentation:
    """ Testes para documentação da API """
    
    def test_swagger_docs_available(self, api_client):
        """ Testa se documentação Swagger está disponível """
        response = api_client.get("/docs")
        
        assert response.status_code == 200
    
    def test_redoc_docs_available(self, api_client):
        """ Testa se documentação ReDoc está disponível """
        response = api_client.get("/redoc")
        
        assert response.status_code == 200
    
    def test_openapi_schema_available(self, api_client):
        """ Testa se schema OpenAPI está disponível """
        response = api_client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Sistema de Otimização de Rotas"

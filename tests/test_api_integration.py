"""
Testes de Integração para a API FastAPI
Testa fluxos completos e integração entre componentes
"""

import pytest
import json
import time
from pathlib import Path
from datetime import datetime

from api.models import ServiceType


@pytest.mark.integration
class TestOptimizationIntegration:
    """ Testes de integração para otimização de rotas """
    
    def test_full_optimization_flow_single_vehicle(self, api_client):
        """ Testa fluxo completo de otimização com 1 veículo """
        request_data = {
            "service_points": [
                {
                    "id": 1,
                    "location": [100.0, 200.0],
                    "service_type": "emergency",
                    "time_window": None
                },
                {
                    "id": 2,
                    "location": [300.0, 400.0],
                    "service_type": "violence",
                    "time_window": [480, 600]
                },
                {
                    "id": 3,
                    "location": [150.0, 350.0],
                    "service_type": "regular",
                    "time_window": None
                }
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100,
            "depot_location": [250.0, 250.0]
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validar estrutura da resposta
        assert data["success"] is True
        assert "message" in data
        assert "date" in data
        assert "fitness" in data
        assert "num_vehicles" in data
        assert data["num_vehicles"] == 1
        assert "vehicles" in data
        assert len(data["vehicles"]) == 1
        assert "execution_time" in data
        assert data["execution_time"] > 0
        
        # Validar dados do veículo
        vehicle = data["vehicles"][0]
        assert vehicle["id"] == 1
        assert "driver" in vehicle
        assert vehicle["total_stops"] >= 3
        assert vehicle["total_distance"] > 0
        assert "estimated_time" in vehicle
        assert "start_time" in vehicle
        assert "end_time" in vehicle
        assert "stops" in vehicle
    
    def test_full_optimization_flow_two_vehicles(self, api_client):
        """ Testa fluxo completo de otimização com 2 veículos """
        request_data = {
            "service_points": [
                {
                    "id": 1,
                    "location": [100.0, 100.0],
                    "service_type": "emergency",
                    "time_window": None
                },
                {
                    "id": 2,
                    "location": [200.0, 200.0],
                    "service_type": "violence",
                    "time_window": None
                },
                {
                    "id": 3,
                    "location": [300.0, 300.0],
                    "service_type": "medication",
                    "time_window": [480, 720]
                },
                {
                    "id": 4,
                    "location": [400.0, 400.0],
                    "service_type": "postpartum",
                    "time_window": None
                },
                {
                    "id": 5,
                    "location": [150.0, 350.0],
                    "service_type": "regular",
                    "time_window": None
                },
                {
                    "id": 6,
                    "location": [350.0, 150.0],
                    "service_type": "regular",
                    "time_window": None
                }
            ],
            "num_vehicles": 2,
            "population_size": 50,
            "generations": 100
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["num_vehicles"] == 2
        assert len(data["vehicles"]) == 2
        
        # Validar que ambos os veículos têm paradas
        for vehicle in data["vehicles"]:
            assert vehicle["total_stops"] > 0
            assert vehicle["total_distance"] > 0
    
    def test_optimization_with_all_service_types(self, api_client):
        """ Testa otimização com todos os tipos de serviço """
        request_data = {
            "service_points": [
                {
                    "id": 1,
                    "location": [100.0, 200.0],
                    "service_type": "emergency",
                    "time_window": None
                },
                {
                    "id": 2,
                    "location": [200.0, 300.0],
                    "service_type": "violence",
                    "time_window": [480, 600]
                },
                {
                    "id": 3,
                    "location": [300.0, 400.0],
                    "service_type": "medication",
                    "time_window": [600, 720]
                },
                {
                    "id": 4,
                    "location": [400.0, 100.0],
                    "service_type": "postpartum",
                    "time_window": None
                },
                {
                    "id": 5,
                    "location": [150.0, 350.0],
                    "service_type": "regular",
                    "time_window": None
                }
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verificar que todos os pontos foram incluídos
        vehicle = data["vehicles"][0]
        assert vehicle["total_stops"] == 5


@pytest.mark.integration
class TestRoutePersistenceIntegration:
    """ Testes de integração para persistência de rotas """
    
    def test_route_saved_after_optimization(self, api_client):
        """ Testa se a rota é salva após otimização """
        request_data = {
            "service_points": [
                {
                    "id": 1,
                    "location": [100.0, 200.0],
                    "service_type": "emergency",
                    "time_window": None
                },
                {
                    "id": 2,
                    "location": [300.0, 400.0],
                    "service_type": "regular",
                    "time_window": None
                }
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        # Executar otimização
        response = api_client.post("/api/v1/optimize", json=request_data)
        assert response.status_code == 200
        
        # Aguardar salvamento
        time.sleep(0.5)
        
        # Verificar se a rota foi salva
        response = api_client.get("/api/v1/routes")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] > 0
        assert len(data["routes"]) > 0
    
    def test_get_latest_route_after_optimization(self, api_client):
        """ Testa obtenção da rota mais recente após otimização """
        request_data = {
            "service_points": [
                {
                    "id": 1,
                    "location": [100.0, 200.0],
                    "service_type": "emergency",
                    "time_window": None
                }
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        # Executar otimização
        opt_response = api_client.post("/api/v1/optimize", json=request_data)
        assert opt_response.status_code == 200
        opt_data = opt_response.json()
        
        # Aguardar salvamento
        time.sleep(0.5)
        
        # Obter rota mais recente
        latest_response = api_client.get("/api/v1/routes/latest")
        assert latest_response.status_code == 200
        
        latest_data = latest_response.json()
        assert latest_data["date"] == opt_data["date"]
        assert latest_data["fitness"] == opt_data["fitness"]
    
    def test_get_route_summary_after_optimization(self, api_client):
        """ Testa obtenção de resumo após otimização """
        request_data = {
            "service_points": [
                {
                    "id": 1,
                    "location": [100.0, 200.0],
                    "service_type": "emergency",
                    "time_window": None
                },
                {
                    "id": 2,
                    "location": [300.0, 400.0],
                    "service_type": "regular",
                    "time_window": None
                }
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        # Executar otimização
        response = api_client.post("/api/v1/optimize", json=request_data)
        assert response.status_code == 200
        
        # Aguardar salvamento
        time.sleep(1.0)
        
        # Primeiro verificar se a rota foi salva
        routes_response = api_client.get("/api/v1/routes")
        assert routes_response.status_code == 200
        routes_data = routes_response.json()
        
        # Deve haver pelo menos uma rota salva após a otimização
        assert routes_data["total"] > 0, "Nenhuma rota foi salva após a otimização"
        
        # Obter a rota mais recente diretamente
        latest_response = api_client.get("/api/v1/routes/latest")
        assert latest_response.status_code == 200
        latest_data = latest_response.json()
        
        # Verificar estrutura da rota
        assert "vehicles" in latest_data
        assert len(latest_data["vehicles"]) > 0


@pytest.mark.integration
class TestVehicleDataIntegration:
    """ Testes de integração para dados de veículos """
    
    def test_get_vehicle_data_after_optimization(self, api_client):
        """ Testa obtenção de dados de veículo após otimização """
        request_data = {
            "service_points": [
                {
                    "id": 1,
                    "location": [100.0, 200.0],
                    "service_type": "emergency",
                    "time_window": None
                },
                {
                    "id": 2,
                    "location": [300.0, 400.0],
                    "service_type": "regular",
                    "time_window": None
                }
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        # Executar otimização
        response = api_client.post("/api/v1/optimize", json=request_data)
        assert response.status_code == 200
        
        # Aguardar salvamento
        time.sleep(0.5)
        
        # Obter dados do veículo 1
        vehicle_response = api_client.get("/api/v1/vehicles/1")
        assert vehicle_response.status_code == 200
        
        vehicle_data = vehicle_response.json()
        assert vehicle_data["id"] == 1
        assert "driver" in vehicle_data
        assert "total_stops" in vehicle_data


@pytest.mark.integration
class TestMultipleOptimizationsIntegration:
    """ Testes de integração para múltiplas otimizações """
    
    def test_multiple_optimizations_sequential(self, api_client):
        """ Testa múltiplas otimizações sequenciais """
        request_data_1 = {
            "service_points": [
                {
                    "id": 1,
                    "location": [100.0, 200.0],
                    "service_type": "emergency",
                    "time_window": None
                }
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        request_data_2 = {
            "service_points": [
                {
                    "id": 1,
                    "location": [200.0, 300.0],
                    "service_type": "violence",
                    "time_window": None
                },
                {
                    "id": 2,
                    "location": [400.0, 100.0],
                    "service_type": "regular",
                    "time_window": None
                }
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        # Primeira otimização
        response1 = api_client.post("/api/v1/optimize", json=request_data_1)
        assert response1.status_code == 200
        
        time.sleep(0.5)
        
        # Segunda otimização
        response2 = api_client.post("/api/v1/optimize", json=request_data_2)
        assert response2.status_code == 200
        
        time.sleep(0.5)
        
        # Verificar que ambas foram salvas
        routes_response = api_client.get("/api/v1/routes")
        assert routes_response.status_code == 200
        
        routes_data = routes_response.json()
        assert routes_data["total"] >= 2


@pytest.mark.integration
class TestAPIPerformance:
    """ Testes de performance da API """
    
    def test_optimization_performance_small_dataset(self, api_client):
        """ Testa performance com dataset pequeno """
        request_data = {
            "service_points": [
                {
                    "id": i,
                    "location": [100.0 * i, 200.0 * i],
                    "service_type": "regular",
                    "time_window": None
                }
                for i in range(1, 6)  # 5 pontos
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        start_time = time.time()
        response = api_client.post("/api/v1/optimize", json=request_data)
        execution_time = time.time() - start_time
        
        assert response.status_code == 200
        assert execution_time < 10.0  # Deve completar em menos de 10 segundos
    
    def test_optimization_performance_medium_dataset(self, api_client):
        """ Testa performance com dataset médio """
        request_data = {
            "service_points": [
                {
                    "id": i,
                    "location": [100.0 * (i % 5), 200.0 * (i // 5)],
                    "service_type": "regular" if i % 2 == 0 else "emergency",
                    "time_window": None
                }
                for i in range(1, 11)  # 10 pontos
            ],
            "num_vehicles": 2,
            "population_size": 50,
            "generations": 100
        }
        
        start_time = time.time()
        response = api_client.post("/api/v1/optimize", json=request_data)
        execution_time = time.time() - start_time
        
        assert response.status_code == 200
        assert execution_time < 15.0  # Deve completar em menos de 15 segundos


@pytest.mark.integration
class TestAPIEndToEnd:
    """ Testes end-to-end da API """
    
    def test_complete_workflow(self, api_client):
        """ Testa fluxo completo: otimizar -> listar -> obter detalhes """
        # 1. Verificar saúde da API
        health_response = api_client.get("/health")
        assert health_response.status_code == 200
        
        # 2. Executar otimização
        request_data = {
            "service_points": [
                {
                    "id": 1,
                    "location": [100.0, 200.0],
                    "service_type": "emergency",
                    "time_window": None
                },
                {
                    "id": 2,
                    "location": [300.0, 400.0],
                    "service_type": "violence",
                    "time_window": [480, 600]
                },
                {
                    "id": 3,
                    "location": [150.0, 350.0],
                    "service_type": "regular",
                    "time_window": None
                }
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        opt_response = api_client.post("/api/v1/optimize", json=request_data)
        assert opt_response.status_code == 200
        opt_data = opt_response.json()
        
        time.sleep(0.5)
        
        # 3. Listar rotas
        list_response = api_client.get("/api/v1/routes")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert list_data["total"] > 0
        
        # 4. Obter rota mais recente
        latest_response = api_client.get("/api/v1/routes/latest")
        assert latest_response.status_code == 200
        latest_data = latest_response.json()
        assert latest_data["date"] == opt_data["date"]
        
        # 5. Deve haver rotas salvas
        assert list_data["total"] > 0, "Nenhuma rota foi salva"
        
        # 6. Obter dados do veículo diretamente da rota mais recente
        vehicle_data = latest_data.get("vehicles", [])[0] if latest_data.get("vehicles") else None
        assert vehicle_data is not None, "Nenhum veículo encontrado na rota"
        assert vehicle_data["id"] == 1

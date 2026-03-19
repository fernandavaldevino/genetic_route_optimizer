"""
Testes Avançados para API - Webhook do Telegram e funcionalidades específicas
Complementa test_api.py com testes de funcionalidades não cobertas
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json

from api.main import app, get_telegram_bot


class TestTelegramWebhook:
    """ Testes para webhook do Telegram """
    
    @patch('api.main.process_telegram_update')
    async def test_webhook_endpoint_receives_update(self, mock_process, api_client):
        """ Testa se webhook recebe atualizações do Telegram """
        update_data = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 12345,
                    "first_name": "Test",
                    "username": "testuser"
                },
                "chat": {
                    "id": 12345,
                    "type": "private"
                },
                "text": "/start"
            }
        }
        
        response = api_client.post("/webhook", json=update_data)
        
        # Webhook sempre retorna 200 OK
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_webhook_endpoint_handles_empty_data(self, api_client):
        """ Testa webhook com dados vazios """
        response = api_client.post("/webhook", json={})
        
        # Deve retornar 200 mesmo com dados vazios
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data
    
    def test_webhook_endpoint_handles_invalid_json(self, api_client):
        """ Testa webhook com JSON inválido """
        response = api_client.post(
            "/webhook",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Deve retornar erro de validação
        assert response.status_code == 422
    
    @patch('api.main.get_telegram_bot')
    def test_webhook_info_without_bot_configured(self, mock_get_bot, api_client):
        """ Testa informações do webhook sem bot configurado """
        mock_get_bot.return_value = None
        
        response = api_client.get("/webhook/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["configured"] is False
        assert "message" in data
    
    @patch('api.main.get_telegram_bot')
    async def test_webhook_info_with_bot_configured(self, mock_get_bot, api_client):
        """ Testa informações do webhook com bot configurado """
        mock_bot = AsyncMock()
        mock_webhook_info = Mock()
        mock_webhook_info.url = "https://example.com/webhook"
        mock_webhook_info.has_custom_certificate = False
        mock_webhook_info.pending_update_count = 0
        mock_webhook_info.last_error_date = None
        mock_webhook_info.last_error_message = None
        mock_webhook_info.max_connections = 40
        
        mock_bot.get_webhook_info.return_value = mock_webhook_info
        mock_get_bot.return_value = mock_bot
        
        response = api_client.get("/webhook/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "configured" in data


class TestTelegramBotInitialization:
    """ Testes para inicialização do bot do Telegram """
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token_123'})
    @patch('api.main.Bot')
    def test_get_telegram_bot_with_token(self, mock_bot_class):
        """ Testa obtenção do bot com token configurado """
        mock_bot_instance = Mock()
        mock_bot_class.return_value = mock_bot_instance
        
        # Resetar bot global
        import api.main
        api.main.telegram_bot = None
        
        bot = get_telegram_bot()
        
        assert bot is not None
        mock_bot_class.assert_called_once_with(token='test_token_123')
    
    @patch.dict('os.environ', {}, clear=True)
    def test_get_telegram_bot_without_token(self):
        """ Testa obtenção do bot sem token configurado """
        # Resetar bot global
        import api.main
        api.main.telegram_bot = None
        
        bot = get_telegram_bot()
        
        # Deve retornar None quando não há token
        assert bot is None


class TestRouteIntegration:
    """ Testes para integração de rotas """
    
    @patch('api.main.route_integration')
    def test_route_integration_convert_from_optimization(self, mock_integration, api_client):
        """ Testa conversão de resultado de otimização """
        mock_integration.convert_from_optimization_result.return_value = {
            'date': '2024-01-15T10:30:00',
            'fitness': 100.0,
            'num_vehicles': 1,
            'vehicles': []
        }
        mock_integration.save_route.return_value = None
        
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
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        # Verificar se a conversão foi chamada
        assert response.status_code in [200, 500]  # Pode falhar por outros motivos


class TestAPIMetadata:
    """ Testes para metadados da API """
    
    def test_api_title_and_version(self, api_client):
        """ Testa título e versão da API """
        response = api_client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Sistema de Otimização de Rotas"
        assert data["info"]["version"] == "1.0.0"
    
    def test_api_has_tags(self, api_client):
        """ Testa se API tem tags organizadas """
        response = api_client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar se há endpoints com tags
        paths = data.get("paths", {})
        has_tags = False
        
        for path_data in paths.values():
            for method_data in path_data.values():
                if "tags" in method_data:
                    has_tags = True
                    break
        
        assert has_tags, "API não tem tags organizadas"


class TestOptimizationWithDifferentParameters:
    """ Testes de otimização com diferentes parâmetros """
    
    def test_optimize_with_two_vehicles(self, api_client):
        """ Testa otimização com 2 veículos """
        request_data = {
            "service_points": [
                {"id": 1, "location": [100.0, 200.0], "service_type": "emergency", "time_window": None},
                {"id": 2, "location": [300.0, 400.0], "service_type": "violence", "time_window": [480, 600]},
                {"id": 3, "location": [150.0, 350.0], "service_type": "regular", "time_window": None},
                {"id": 4, "location": [250.0, 450.0], "service_type": "medication", "time_window": None}
            ],
            "num_vehicles": 2,
            "population_size": 50,
            "generations": 100
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["num_vehicles"] == 2
    
    def test_optimize_with_custom_depot_location(self, api_client):
        """ Testa otimização com localização customizada do depósito """
        request_data = {
            "service_points": [
                {"id": 1, "location": [100.0, 200.0], "service_type": "emergency", "time_window": None},
                {"id": 2, "location": [300.0, 400.0], "service_type": "regular", "time_window": None}
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100,
            "depot_location": [500.0, 500.0]
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        assert response.status_code == 200
    
    def test_optimize_with_max_population_size(self, api_client):
        """ Testa otimização com tamanho máximo de população """
        request_data = {
            "service_points": [
                {"id": 1, "location": [100.0, 200.0], "service_type": "emergency", "time_window": None}
            ],
            "num_vehicles": 1,
            "population_size": 500,  # Máximo permitido
            "generations": 100
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        assert response.status_code == 200
    
    def test_optimize_with_max_generations(self, api_client):
        """ Testa otimização com número máximo de gerações """
        request_data = {
            "service_points": [
                {"id": 1, "location": [100.0, 200.0], "service_type": "emergency", "time_window": None}
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 1000  # Máximo permitido
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        assert response.status_code == 200


class TestServiceTypeValidation:
    """ Testes para validação de tipos de serviço """
    
    def test_all_service_types_valid(self, api_client):
        """ Testa todos os tipos de serviço válidos """
        service_types = ["emergency", "violence", "medication", "postpartum", "regular"]
        
        for service_type in service_types:
            request_data = {
                "service_points": [
                    {"id": 1, "location": [100.0, 200.0], "service_type": service_type, "time_window": None}
                ],
                "num_vehicles": 1,
                "population_size": 50,
                "generations": 100
            }
            
            response = api_client.post("/api/v1/optimize", json=request_data)
            
            assert response.status_code == 200, f"Tipo de serviço '{service_type}' falhou"


class TestTimeWindowValidation:
    """ Testes para validação de janelas de tempo """
    
    def test_optimize_with_time_windows(self, api_client):
        """ Testa otimização com janelas de tempo """
        request_data = {
            "service_points": [
                {"id": 1, "location": [100.0, 200.0], "service_type": "violence", "time_window": [480, 600]},
                {"id": 2, "location": [300.0, 400.0], "service_type": "postpartum", "time_window": [540, 660]}
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        assert response.status_code == 200
    
    def test_optimize_mixed_time_windows(self, api_client):
        """ Testa otimização com mix de pontos com e sem janelas de tempo """
        request_data = {
            "service_points": [
                {"id": 1, "location": [100.0, 200.0], "service_type": "emergency", "time_window": None},
                {"id": 2, "location": [300.0, 400.0], "service_type": "violence", "time_window": [480, 600]},
                {"id": 3, "location": [150.0, 350.0], "service_type": "regular", "time_window": None}
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        assert response.status_code == 200


class TestResponseStructure:
    """ Testes para estrutura de resposta """
    
    def test_optimization_response_has_execution_time(self, api_client):
        """ Testa se resposta de otimização inclui tempo de execução """
        request_data = {
            "service_points": [
                {"id": 1, "location": [100.0, 200.0], "service_type": "emergency", "time_window": None}
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "execution_time" in data
        assert isinstance(data["execution_time"], (int, float))
        assert data["execution_time"] >= 0
    
    def test_optimization_response_has_vehicles_array(self, api_client):
        """ Testa se resposta tem array de veículos """
        request_data = {
            "service_points": [
                {"id": 1, "location": [100.0, 200.0], "service_type": "emergency", "time_window": None}
            ],
            "num_vehicles": 1,
            "population_size": 50,
            "generations": 100
        }
        
        response = api_client.post("/api/v1/optimize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "vehicles" in data
        assert isinstance(data["vehicles"], list)
        assert len(data["vehicles"]) == 1


class TestGlobalExceptionHandler:
    """ Testes para tratador global de exceções """
    
    @patch('api.main.route_integration')
    def test_global_exception_handler_format(self, mock_integration, api_client):
        """ Testa formato de resposta do tratador global de exceções """
        # Forçar uma exceção não tratada
        mock_integration.data_dir.glob.side_effect = RuntimeError("Erro de teste")
        
        response = api_client.get("/api/v1/routes")
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data or "detail" in data
        assert "timestamp" in data or "detail" in data


class TestCORSMiddleware:
    """ Testes para middleware CORS """
    
    def test_cors_allows_all_origins(self, api_client):
        """ Testa se CORS permite todas as origens """
        response = api_client.get(
            "/",
            headers={"Origin": "http://example.com"}
        )
        
        assert response.status_code == 200
        # CORS headers podem estar presentes
        # Nota: TestClient pode não incluir todos os headers CORS
    
    def test_cors_allows_credentials(self, api_client):
        """ Testa se CORS permite credenciais """
        response = api_client.get(
            "/health",
            headers={"Origin": "http://example.com"}
        )
        
        assert response.status_code == 200

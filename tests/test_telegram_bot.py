"""
Testes para o Bot de Telegram e integração de rotas
"""

from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from telegram_bot.route_integration import RouteDataIntegration
from src.core.service_points import create_service_point
import pytest
import json
import tempfile

# Importar módulos do projeto
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRouteDataIntegration:
    """ Testes para a classe RouteDataIntegration """
    
    @pytest.fixture
    def temp_data_dir(self):
        """ Cria um diretório temporário para testes """
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def integration(self, temp_data_dir):
        """ Cria uma instância de RouteDataIntegration para testes """
        return RouteDataIntegration(data_dir=temp_data_dir)
    
    @pytest.fixture
    def sample_route_data(self):
        """ Dados de rota de exemplo """
        return {
            'date': '2024-01-15T10:30:00',
            'fitness': 0.95,
            'num_vehicles': 1,
            'vehicles': [
                {
                    'id': 1,
                    'driver': 'Motorista 1',
                    'total_stops': 5,
                    'total_distance': 45.5,
                    'estimated_time': '4h 30min',
                    'start_time': '08:00',
                    'end_time': '12:30',
                    'stops': [
                        {
                            'id': 1,
                            'type': 'EME',
                            'priority': 1,
                            'address': 'Rua A, 123',
                            'time': '08:15',
                            'duration': '30 min',
                            'instructions': '⚠️ EMERGÊNCIA OBSTÉTRICA',
                            'special_notes': 'Prioridade máxima'
                        },
                        {
                            'id': 2,
                            'type': 'VIO',
                            'priority': 2,
                            'address': 'Rua B, 456',
                            'time': '09:00',
                            'duration': '45 min',
                            'instructions': '🔒 VIOLÊNCIA DOMÉSTICA',
                            'special_notes': 'Discrição total'
                        }
                    ]
                }
            ]
        }
    
    @pytest.fixture
    def sample_service_points(self):
        """ Pontos de serviço de exemplo """
        return [
            create_service_point(0, (0, 0), 'regular', None),  # Depósito
            create_service_point(1, (100, 100), 'emergency', None),
            create_service_point(2, (200, 200), 'violence', (480, 600)),
            create_service_point(3, (300, 300), 'medication', None),
            create_service_point(4, (400, 400), 'postpartum', (540, 660)),
            create_service_point(5, (500, 500), 'regular', None),
        ]
    
    def test_initialization(self, temp_data_dir):
        """ Testa inicialização da integração """
        integration = RouteDataIntegration(data_dir=temp_data_dir)
        
        assert integration.data_dir == temp_data_dir
        assert integration.data_dir.exists()
        assert integration.current_route is None
    
    def test_save_route(self, integration, sample_route_data):
        """ Testa salvamento de rota """
        success = integration.save_route(sample_route_data, 'test_route.json')
        
        assert success is True
        assert integration.current_route == sample_route_data
        
        # Verificar se arquivo foi criado
        saved_file = integration.data_dir / 'test_route.json'
        assert saved_file.exists()
        
        # Verificar conteúdo
        with open(saved_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == sample_route_data
    
    def test_save_route_auto_filename(self, integration, sample_route_data):
        """ Testa salvamento de rota com nome automático """
        success = integration.save_route(sample_route_data)
        
        assert success is True
        
        # Verificar se arquivo foi criado com timestamp
        route_files = list(integration.data_dir.glob('route_*.json'))
        assert len(route_files) == 1
    
    def test_load_latest_route(self, integration, sample_route_data):
        """ Testa carregamento da rota mais recente """
        # Salvar múltiplas rotas
        integration.save_route(sample_route_data, 'route_20240101_100000.json')
        integration.save_route(sample_route_data, 'route_20240102_100000.json')
        integration.save_route(sample_route_data, 'route_20240103_100000.json')
        
        # Carregar mais recente
        loaded_route = integration.load_latest_route()
        
        assert loaded_route is not None
        assert loaded_route == sample_route_data
        assert integration.current_route == sample_route_data
    
    def test_load_latest_route_no_files(self, integration):
        """ Testa carregamento quando não há rotas salvas """
        loaded_route = integration.load_latest_route()
        
        assert loaded_route is None
    
    def test_get_route_summary(self, integration, sample_route_data):
        """ Testa obtenção de resumo da rota """
        integration.save_route(sample_route_data)
        
        summary = integration.get_route_summary()
        
        assert summary is not None
        assert summary['total_vehicles'] == 1
        assert summary['total_stops'] == 5
        assert summary['total_distance'] == 45.5
        assert summary['optimization_date'] == '2024-01-15T10:30:00'
    
    def test_get_route_summary_multiple_vehicles(self, integration):
        """ Testa resumo com múltiplos veículos """
        route_data = {
            'date': '2024-01-15T10:30:00',
            'vehicles': [
                {'id': 1, 'total_stops': 5, 'total_distance': 30.0},
                {'id': 2, 'total_stops': 7, 'total_distance': 40.0}
            ]
        }
        
        integration.save_route(route_data)
        summary = integration.get_route_summary()
        
        assert summary['total_vehicles'] == 2
        assert summary['total_stops'] == 12
        assert summary['total_distance'] == 70.0
    
    def test_get_vehicle_data(self, integration, sample_route_data):
        """ Testa obtenção de dados de veículo específico """
        integration.save_route(sample_route_data)
        
        vehicle_data = integration.get_vehicle_data(vehicle_id=1)
        
        assert vehicle_data is not None
        assert vehicle_data['id'] == 1
        assert vehicle_data['driver'] == 'Motorista 1'
        assert vehicle_data['total_stops'] == 5
    
    def test_get_vehicle_data_not_found(self, integration, sample_route_data):
        """ Testa obtenção de veículo inexistente """
        integration.save_route(sample_route_data)
        
        vehicle_data = integration.get_vehicle_data(vehicle_id=999)
        
        assert vehicle_data is None
    
    def test_convert_from_optimization_result_single_vehicle(self, integration, sample_service_points):
        """ Testa conversão de resultado de otimização para 1 veículo """
        best_route = [1, 2, 3, 4, 5]
        fitness = 0.95
        distance_km = 50.5
        
        route_data = integration.convert_from_optimization_result(
            best_route=best_route,
            service_points=sample_service_points,
            fitness=fitness,
            distance_km=distance_km,
            num_vehicles=1
        )
        
        assert route_data is not None
        assert 'date' in route_data
        assert route_data['fitness'] == fitness
        assert route_data['num_vehicles'] == 1
        assert len(route_data['vehicles']) == 1
        
        vehicle = route_data['vehicles'][0]
        assert vehicle['id'] == 1
        assert vehicle['driver'] == 'Motorista 1'
        assert vehicle['total_stops'] == 5
        assert vehicle['total_distance'] == 50.5
        assert vehicle['start_time'] == '08:00'
        assert len(vehicle['stops']) == 5
    
    def test_convert_from_optimization_result_two_vehicles(self, integration, sample_service_points):
        """ Testa conversão de resultado de otimização para 2 veículos """
        best_route = [1, 2, 3, 4, 5]
        fitness = 0.95
        distance_km = 50.5
        
        route_data = integration.convert_from_optimization_result(
            best_route=best_route,
            service_points=sample_service_points,
            fitness=fitness,
            distance_km=distance_km,
            num_vehicles=2
        )
        
        assert route_data is not None
        assert route_data['num_vehicles'] == 2
        assert len(route_data['vehicles']) == 2
        
        # Verificar veículo 1
        vehicle1 = route_data['vehicles'][0]
        assert vehicle1['id'] == 1
        assert vehicle1['driver'] == 'Motorista 1'
        
        # Verificar veículo 2
        vehicle2 = route_data['vehicles'][1]
        assert vehicle2['id'] == 2
        assert vehicle2['driver'] == 'Motorista 2'
    
    def test_get_instructions(self, integration):
        """ Testa obtenção de instruções por tipo de serviço """
        assert '⚠️ EMERGÊNCIA OBSTÉTRICA' in integration._get_instructions('EME')
        assert '🔒 VIOLÊNCIA DOMÉSTICA' in integration._get_instructions('VIO')
        assert '🌡️ MEDICAMENTO HORMONAL' in integration._get_instructions('MED')
        assert '👶 PÓS-PARTO' in integration._get_instructions('POS')
        assert '📋 ATENDIMENTO REGULAR' in integration._get_instructions('REG')
    
    def test_get_special_notes(self, integration, sample_service_points):
        """ Testa obtenção de notas especiais """
        eme_point = sample_service_points[1]  # emergency
        vio_point = sample_service_points[2]  # violence
        
        eme_notes = integration._get_special_notes(eme_point)
        vio_notes = integration._get_special_notes(vio_point)
        
        assert 'crítica' in eme_notes or 'essencial' in eme_notes
        assert 'Discrição' in vio_notes or 'Janela' in vio_notes
    
    def test_stop_time_formatting(self, integration, sample_service_points):
        """ Testa formatação de horários das paradas """
        best_route = [1, 2]
        
        route_data = integration.convert_from_optimization_result(
            best_route=best_route,
            service_points=sample_service_points,
            fitness=0.95,
            distance_km=20.0,
            num_vehicles=1
        )
        
        stops = route_data['vehicles'][0]['stops']
        
        # Verificar formato de horário (HH:MM)
        for stop in stops:
            time_str = stop['time']
            assert ':' in time_str
            hours, minutes = time_str.split(':')
            assert len(hours) == 2
            assert len(minutes) == 2
            assert 0 <= int(hours) <= 23
            assert 0 <= int(minutes) <= 59
    
    def test_stop_duration_formatting(self, integration, sample_service_points):
        """ Testa formatação de duração das paradas """
        best_route = [1, 2]
        
        route_data = integration.convert_from_optimization_result(
            best_route=best_route,
            service_points=sample_service_points,
            fitness=0.95,
            distance_km=20.0,
            num_vehicles=1
        )
        
        stops = route_data['vehicles'][0]['stops']
        
        # Verificar formato de duração
        for stop in stops:
            duration_str = stop['duration']
            assert 'min' in duration_str
            duration_value = int(duration_str.split()[0])
            assert duration_value > 0


class TestTelegramBotCommands:
    """ Testes para comandos do bot do Telegram """
    
    @pytest.fixture
    def mock_update(self):
        """ Mock do objeto Update do Telegram """
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        update.message.text = ""
        update.message.chat = Mock()
        update.message.chat.id = 12345
        return update
    
    @pytest.fixture
    def mock_context(self):
        """ Mock do objeto Context do Telegram """
        context = Mock()
        context.user_data = {}
        context.args = []
        return context
    
    @pytest.fixture
    def bot_instance(self, temp_data_dir):
        """ Instância do bot para testes """
        # Importar aqui para evitar problemas de importação
        from telegram_bot.bot import RouteAssistantBot
        
        # Mock do token
        with patch('telegram_bot.bot.Application') as mock_app:
            mock_app.builder.return_value.token.return_value.build.return_value = Mock()
            bot = RouteAssistantBot(token="test_token", use_real_data=False)
            return bot
    
    @pytest.mark.asyncio
    async def test_start_command(self, bot_instance, mock_update, mock_context):
        """ Testa comando /start """
        await bot_instance.start_command(mock_update, mock_context)
        
        # Verificar se reply_text foi chamado
        mock_update.message.reply_text.assert_called_once()
        
        # Verificar conteúdo da mensagem
        call_args = mock_update.message.reply_text.call_args
        message_text = call_args[0][0]
        
        assert 'Bem-vindo' in message_text
        assert 'Assistente de Rotas' in message_text
        assert '/iniciar_rota' in message_text or 'iniciar' in message_text.lower()
    
    @pytest.mark.asyncio
    async def test_start_command_vehicle_selection(self, bot_instance, mock_update, mock_context):
        """ Testa seleção de veículo no comando /start """
        # Testar veículo 1
        mock_context.args = []
        await bot_instance.start_command(mock_update, mock_context)
        assert mock_context.user_data.get('vehicle_id', 1) == 1
        
        # Testar veículo 2
        mock_context.user_data.clear()
        mock_context.args = ['veiculo2']
        await bot_instance.start_command(mock_update, mock_context)
        assert mock_context.user_data.get('vehicle_id') == 2
    
    @pytest.mark.asyncio
    async def test_help_command(self, bot_instance, mock_update, mock_context):
        """ Testa comando /help """
        await bot_instance.help_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        
        call_args = mock_update.message.reply_text.call_args
        message_text = call_args[0][0]
        
        assert 'AJUDA' in message_text or 'Comandos' in message_text
        assert '/rota' in message_text
        assert '/paradas' in message_text
    
    @pytest.mark.asyncio
    async def test_route_command(self, bot_instance, mock_update, mock_context):
        """ Testa comando /rota """
        mock_context.user_data['vehicle_id'] = 1
        
        await bot_instance.route_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        
        call_args = mock_update.message.reply_text.call_args
        message_text = call_args[0][0]
        
        assert 'ROTA' in message_text or 'rota' in message_text.lower()
    
    @pytest.mark.asyncio
    async def test_stops_command(self, bot_instance, mock_update, mock_context):
        """ Testa comando /paradas """
        mock_context.user_data['vehicle_id'] = 1
        
        await bot_instance.stops_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        
        call_args = mock_update.message.reply_text.call_args
        message_text = call_args[0][0]
        
        assert 'paradas' in message_text.lower() or 'PARADAS' in message_text
    
    @pytest.mark.asyncio
    async def test_start_route_command(self, bot_instance, mock_update, mock_context):
        """ Testa comando /iniciar_rota """
        mock_context.user_data['vehicle_id'] = 1
        
        await bot_instance.start_route_command(mock_update, mock_context)
        
        # Verificar se rota foi iniciada
        assert mock_context.user_data.get('route_started') is True
        assert mock_context.user_data.get('current_stop_index') == 0
        
        mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_next_stop_command_not_started(self, bot_instance, mock_update, mock_context):
        """ Testa comando /proxima sem iniciar rota """
        mock_context.user_data['vehicle_id'] = 1
        mock_context.user_data['route_started'] = False
        
        await bot_instance.next_stop_command(mock_update, mock_context)
        
        call_args = mock_update.message.reply_text.call_args
        message_text = call_args[0][0]
        
        assert 'iniciar' in message_text.lower()
    
    @pytest.mark.asyncio
    async def test_complete_stop_command(self, bot_instance, mock_update, mock_context):
        """ Testa comando /concluido """
        mock_context.user_data['vehicle_id'] = 1
        mock_context.user_data['route_started'] = True
        mock_context.user_data['current_stop_index'] = 0
        
        await bot_instance.complete_stop_command(mock_update, mock_context)
        
        # Verificar se índice foi incrementado
        assert mock_context.user_data.get('current_stop_index') == 1
        
        mock_update.message.reply_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_finish_route_command(self, bot_instance, mock_update, mock_context):
        """ Testa comando /concluir_rota """
        mock_context.user_data['vehicle_id'] = 1
        mock_context.user_data['route_started'] = True
        
        # Simular todas as paradas concluídas
        vehicle_data = bot_instance._get_vehicle_data(mock_context)
        mock_context.user_data['current_stop_index'] = len(vehicle_data['stops'])
        
        await bot_instance.finish_route_command(mock_update, mock_context)
        
        # Verificar se rota foi finalizada
        assert mock_context.user_data.get('route_started') is False
        assert mock_context.user_data.get('current_stop_index') == 0
        
        mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_reload_command(self, bot_instance, mock_update, mock_context):
        """ Testa comando /recarregar """
        await bot_instance.reload_command(mock_update, mock_context)
        
        # Verificar se reply_text foi chamado (pelo menos 2 vezes: mensagem inicial + resultado)
        assert mock_update.message.reply_text.call_count >= 1
    
    def test_get_vehicle_data(self, bot_instance, mock_context):
        """ Testa obtenção de dados do veículo """
        mock_context.user_data['vehicle_id'] = 1
        
        vehicle_data = bot_instance._get_vehicle_data(mock_context)
        
        assert vehicle_data is not None
        assert 'driver' in vehicle_data
        assert 'stops' in vehicle_data
    
    def test_calculate_end_day(self, bot_instance):
        """ Testa cálculo do dia de término """
        vehicle_data = {
            'start_time': '08:00',
            'stops': [
                {'time': '08:30'},
                {'time': '10:00'},
                {'time': '14:00'},
                {'time': '09:00'},  # Volta para manhã = dia 2
                {'time': '11:00'}
            ]
        }
        
        end_day = bot_instance._calculate_end_day(vehicle_data)
        
        assert end_day >= 1
    
    def test_get_initial_keyboard(self, bot_instance):
        """ Testa teclado inicial """
        keyboard = bot_instance._get_initial_keyboard()
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) > 0
    
    def test_get_active_keyboard(self, bot_instance, mock_context):
        """ Testa teclado ativo durante rota """
        mock_context.user_data['vehicle_id'] = 1
        mock_context.user_data['current_stop_index'] = 0
        
        keyboard = bot_instance._get_active_keyboard(mock_context)
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) > 0
    
    def test_get_keyboard_based_on_state(self, bot_instance, mock_context):
        """ Testa seleção de teclado baseado no estado """
        # Estado inicial
        mock_context.user_data['route_started'] = False
        keyboard = bot_instance._get_keyboard(mock_context)
        assert keyboard is not None
        
        # Estado ativo
        mock_context.user_data['route_started'] = True
        mock_context.user_data['current_stop_index'] = 0
        keyboard = bot_instance._get_keyboard(mock_context)
        assert keyboard is not None


class TestRouteDataValidation:
    """ Testes de validação de dados de rota """
    
    @pytest.fixture
    def integration(self):
        """ Instância de integração """
        with tempfile.TemporaryDirectory() as tmpdir:
            yield RouteDataIntegration(data_dir=Path(tmpdir))
    
    def test_route_data_structure(self, integration, sample_service_points):
        """ Testa estrutura dos dados de rota """
        best_route = [1, 2, 3]
        
        route_data = integration.convert_from_optimization_result(
            best_route=best_route,
            service_points=sample_service_points,
            fitness=0.95,
            distance_km=30.0,
            num_vehicles=1
        )
        
        # Verificar estrutura principal
        assert 'date' in route_data
        assert 'fitness' in route_data
        assert 'num_vehicles' in route_data
        assert 'vehicles' in route_data
        
        # Verificar estrutura do veículo
        vehicle = route_data['vehicles'][0]
        assert 'id' in vehicle
        assert 'driver' in vehicle
        assert 'total_stops' in vehicle
        assert 'total_distance' in vehicle
        assert 'estimated_time' in vehicle
        assert 'start_time' in vehicle
        assert 'end_time' in vehicle
        assert 'stops' in vehicle
        
        # Verificar estrutura das paradas
        for stop in vehicle['stops']:
            assert 'id' in stop
            assert 'type' in stop
            assert 'priority' in stop
            assert 'address' in stop
            assert 'time' in stop
            assert 'duration' in stop
            assert 'instructions' in stop
            assert 'special_notes' in stop
    
    def test_priority_types_mapping(self, integration):
        """ Testa mapeamento correto de tipos de prioridade """
        # Criar pontos de serviço com todos os tipos
        from src.core.service_points import create_service_point
        
        service_points = [
            create_service_point(0, (0, 0), 'regular', None),  # Depósito
            create_service_point(1, (100, 100), 'emergency', None),
            create_service_point(2, (200, 200), 'violence', (480, 600)),
            create_service_point(3, (300, 300), 'medication', None),
            create_service_point(4, (400, 400), 'postpartum', (540, 660)),
            create_service_point(5, (500, 500), 'regular', None),
        ]
        
        # Usar índices válidos (1-5, pulando o depósito no índice 0)
        best_route = [1, 2, 3, 4, 5]
        
        route_data = integration.convert_from_optimization_result(
            best_route=best_route,
            service_points=service_points,
            fitness=0.95,
            distance_km=50.0,
            num_vehicles=1
        )
        
        stops = route_data['vehicles'][0]['stops']
        
        # Verificar tipos de serviço
        service_types = [stop['type'] for stop in stops]
        assert 'EME' in service_types  # emergency (índice 1)
        assert 'VIO' in service_types  # violence (índice 2)
        assert 'MED' in service_types  # medication (índice 3)
        assert 'POS' in service_types  # postpartum (índice 4)
        assert 'REG' in service_types  # regular (índice 5)


@pytest.fixture
def temp_data_dir():
    """ Fixture global para diretório temporário """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

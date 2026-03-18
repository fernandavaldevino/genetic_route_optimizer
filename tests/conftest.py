"""
Configuração e fixtures compartilhadas para os testes com pytest
"""

import sys
import os
import pytest
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.service_points import create_service_point, ServicePriority


@pytest.fixture
def sample_service_points():
    """ Fixture que retorna pontos de serviço de exemplo para testes """
    return [
        create_service_point(1, (100, 100), 'emergency', None),
        create_service_point(2, (200, 200), 'violence', (480, 600)),
        create_service_point(3, (300, 300), 'medication', None),
        create_service_point(4, (400, 400), 'postpartum', (540, 660)),
        create_service_point(5, (500, 500), 'regular', None),
    ]


@pytest.fixture
def depot_point():
    """ Fixture que retorna um ponto de depósito """
    depot = create_service_point(0, (250, 250), 'regular', None)
    depot.service_duration = 0.0
    return depot


@pytest.fixture
def medication_route():
    """ Fixture que retorna uma rota com medicamentos para teste de temperatura """
    return [
        create_service_point(1, (100, 100), 'medication', None),
        create_service_point(2, (150, 150), 'regular', None),
        create_service_point(3, (200, 200), 'medication', None),
    ]


@pytest.fixture
def priority_ordered_route():
    """ Fixture que retorna uma rota ordenada por prioridade """
    return [
        create_service_point(1, (100, 100), 'emergency', None),
        create_service_point(2, (150, 150), 'violence', (480, 600)),
        create_service_point(3, (200, 200), 'medication', None),
        create_service_point(4, (250, 250), 'postpartum', (540, 660)),
        create_service_point(5, (300, 300), 'regular', None),
    ]


@pytest.fixture
def priority_reversed_route():
    """ Fixture que retorna uma rota com prioridades invertidas """
    return [
        create_service_point(1, (100, 100), 'regular', None),
        create_service_point(2, (150, 150), 'postpartum', (540, 660)),
        create_service_point(3, (200, 200), 'medication', None),
        create_service_point(4, (250, 250), 'violence', (480, 600)),
        create_service_point(5, (300, 300), 'emergency', None),
    ]


# ============================================================================
# Fixtures para testes da API
# ============================================================================

@pytest.fixture
def api_client():
    """ Fixture que retorna um cliente de teste para a API FastAPI """
    from api.main import app
    return TestClient(app)


@pytest.fixture
def temp_route_dir():
    """ Fixture que cria um diretório temporário para salvar rotas durante os testes """
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    yield temp_path
    
    # Limpar após os testes
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_optimization_request():
    """ Fixture que retorna uma requisição de otimização de exemplo """
    return {
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


@pytest.fixture
def sample_route_data():
    """ Fixture que retorna dados de rota de exemplo """
    return {
        'date': '2024-01-15T10:30:00',
        'fitness': 100.0,
        'num_vehicles': 1,
        'vehicles': [
            {
                'id': 1,
                'driver': 'Motorista 1',
                'total_stops': 3,
                'total_distance': 25.5,
                'estimated_time': '2h 30min',
                'start_time': '08:00',
                'end_time': '10:30',
                'stops': [
                    {
                        'id': 1,
                        'type': 'emergency',
                        'priority': 1,
                        'address': 'Endereço 1',
                        'coordinates': {'lat': 100.0, 'lng': 200.0},
                        'time': '08:15',
                        'duration': '30min',
                        'instructions': 'Instruções 1',
                        'special_notes': 'Notas 1'
                    }
                ]
            }
        ]
    }

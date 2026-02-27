"""
Configuração e fixtures compartilhadas para os testes com pytest
"""

import sys
import os
import pytest

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.service_points import create_service_point, ServicePriority


@pytest.fixture
def sample_service_points():
    """Fixture que retorna pontos de serviço de exemplo para testes"""
    return [
        create_service_point(1, (100, 100), 'emergency', None),
        create_service_point(2, (200, 200), 'violence', (480, 600)),
        create_service_point(3, (300, 300), 'medication', None),
        create_service_point(4, (400, 400), 'postpartum', (540, 660)),
        create_service_point(5, (500, 500), 'regular', None),
    ]


@pytest.fixture
def depot_point():
    """Fixture que retorna um ponto de depósito"""
    depot = create_service_point(0, (250, 250), 'regular', None)
    depot.service_duration = 0.0
    return depot


@pytest.fixture
def medication_route():
    """Fixture que retorna uma rota com medicamentos para teste de temperatura"""
    return [
        create_service_point(1, (100, 100), 'medication', None),
        create_service_point(2, (150, 150), 'regular', None),
        create_service_point(3, (200, 200), 'medication', None),
    ]


@pytest.fixture
def priority_ordered_route():
    """Fixture que retorna uma rota ordenada por prioridade"""
    return [
        create_service_point(1, (100, 100), 'emergency', None),
        create_service_point(2, (150, 150), 'violence', (480, 600)),
        create_service_point(3, (200, 200), 'medication', None),
        create_service_point(4, (250, 250), 'postpartum', (540, 660)),
        create_service_point(5, (300, 300), 'regular', None),
    ]


@pytest.fixture
def priority_reversed_route():
    """Fixture que retorna uma rota com prioridades invertidas"""
    return [
        create_service_point(1, (100, 100), 'regular', None),
        create_service_point(2, (150, 150), 'postpartum', (540, 660)),
        create_service_point(3, (200, 200), 'medication', None),
        create_service_point(4, (250, 250), 'violence', (480, 600)),
        create_service_point(5, (300, 300), 'emergency', None),
    ]

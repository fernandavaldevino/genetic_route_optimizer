"""
Testes para o módulo service_points
Testa criação de pontos, prioridades, janelas de tempo e validações
"""

import pytest
from src.core.service_points import (
    create_service_point,
    ServicePriority,
    sort_by_priority,
    validate_temperature_control_route,
    TimeWindow,
    calculate_distance
)


class TestServicePointCreation:
    """Testes para criação de pontos de serviço"""
    
    def test_create_emergency_point(self):
        """Testa criação de ponto de emergência obstétrica"""
        point = create_service_point(1, (100, 200), 'emergency', None)
        
        assert point.id == 1
        assert point.location == (100, 200)
        assert point.priority == ServicePriority.EMERGENCY_OBSTETRIC
        assert point.service_duration == 30.0
        assert point.time_window is None
    
    def test_create_violence_point(self):
        """Testa criação de ponto de violência doméstica com janela de tempo"""
        point = create_service_point(2, (300, 400), 'violence', (480, 600))
        
        assert point.id == 2
        assert point.priority == ServicePriority.DOMESTIC_VIOLENCE
        assert point.time_window is not None
        assert point.time_window.start_time == 480
        assert point.time_window.end_time == 600
    
    def test_create_medication_point(self):
        """Testa criação de ponto de medicamento hormonal"""
        point = create_service_point(3, (500, 600), 'medication', None)
        
        assert point.priority == ServicePriority.HORMONAL_MEDICATION
        assert point.requires_temperature_control is True
    
    def test_create_postpartum_point(self):
        """Testa criação de ponto de pós-parto"""
        point = create_service_point(4, (700, 800), 'postpartum', (540, 660))
        
        assert point.priority == ServicePriority.POSTPARTUM_CARE
        assert point.time_window is not None
    
    def test_create_regular_point(self):
        """Testa criação de ponto regular"""
        point = create_service_point(5, (900, 1000), 'regular', None)
        
        assert point.priority == ServicePriority.REGULAR
        assert point.service_duration == 15.0


class TestPriorityOrdering:
    """Testes para ordenação por prioridade"""
    
    def test_sort_by_priority_correct_order(self, sample_service_points):
        """Testa se a ordenação por prioridade está correta"""
        sorted_points = sort_by_priority(sample_service_points)
        
        expected_order = [
            ServicePriority.EMERGENCY_OBSTETRIC,
            ServicePriority.DOMESTIC_VIOLENCE,
            ServicePriority.HORMONAL_MEDICATION,
            ServicePriority.POSTPARTUM_CARE,
            ServicePriority.REGULAR
        ]
        
        actual_order = [p.priority for p in sorted_points]
        assert actual_order == expected_order
    
    def test_sort_preserves_all_points(self, sample_service_points):
        """Testa se a ordenação preserva todos os pontos"""
        sorted_points = sort_by_priority(sample_service_points)
        
        original_ids = set(p.id for p in sample_service_points)
        sorted_ids = set(p.id for p in sorted_points)
        
        assert original_ids == sorted_ids
    
    def test_priority_weights(self):
        """Testa se os pesos de prioridade estão corretos"""
        emergency = create_service_point(1, (0, 0), 'emergency', None)
        violence = create_service_point(2, (0, 0), 'violence', None)
        medication = create_service_point(3, (0, 0), 'medication', None)
        postpartum = create_service_point(4, (0, 0), 'postpartum', None)
        regular = create_service_point(5, (0, 0), 'regular', None)
        
        assert emergency.get_priority_weight() < violence.get_priority_weight()
        assert violence.get_priority_weight() < medication.get_priority_weight()
        assert medication.get_priority_weight() < postpartum.get_priority_weight()
        assert postpartum.get_priority_weight() < regular.get_priority_weight()


class TestTimeWindows:
    """Testes para janelas de tempo"""
    
    def test_time_window_valid_time(self):
        """Testa validação de tempo dentro da janela"""
        window = TimeWindow(480, 600)  # 8h às 10h
        
        assert window.is_valid_time(500) is True  # 8:20
        assert window.is_valid_time(480) is True  # 8:00 (início)
        assert window.is_valid_time(600) is True  # 10:00 (fim)
    
    def test_time_window_invalid_time_before(self):
        """Testa tempo antes da janela"""
        window = TimeWindow(480, 600)
        
        assert window.is_valid_time(450) is False  # 7:30
    
    def test_time_window_invalid_time_after(self):
        """Testa tempo depois da janela"""
        window = TimeWindow(480, 600)
        
        assert window.is_valid_time(650) is False  # 10:50
    
    def test_time_window_penalty_calculation(self):
        """Testa cálculo de penalidade por violação de janela"""
        window = TimeWindow(480, 600)
        
        # Dentro da janela: sem penalidade
        assert window.get_penalty(500) == 0.0
        
        # Fora da janela: deve ter penalidade
        penalty_before = window.get_penalty(450)
        penalty_after = window.get_penalty(650)
        
        assert penalty_before > 0
        assert penalty_after > 0


class TestTemperatureControl:
    """Testes para controle de temperatura"""
    
    def test_valid_temperature_route(self, medication_route):
        """Testa rota válida com medicamentos próximos"""
        is_valid, message = validate_temperature_control_route(
            medication_route,
            max_time_without_control=120.0
        )
        
        assert is_valid is True
        assert "válida" in message.lower()
    
    def test_invalid_temperature_route(self):
        """Testa rota inválida com medicamentos muito distantes"""
        route = [
            create_service_point(1, (100, 100), 'medication', None),
            create_service_point(2, (500, 500), 'regular', None),
            create_service_point(3, (1000, 1000), 'regular', None),
            create_service_point(4, (1500, 1500), 'medication', None),
        ]
        
        is_valid, message = validate_temperature_control_route(
            route,
            max_time_without_control=120.0
        )
        
        assert is_valid is False
        assert "excede" in message.lower() or "temperatura" in message.lower()
    
    def test_route_without_medication(self):
        """Testa rota sem medicamentos (sempre válida)"""
        route = [
            create_service_point(1, (100, 100), 'regular', None),
            create_service_point(2, (500, 500), 'regular', None),
        ]
        
        is_valid, message = validate_temperature_control_route(route)
        
        assert is_valid is True


class TestDistanceCalculation:
    """Testes para cálculo de distância"""
    
    def test_distance_same_point(self):
        """Testa distância entre o mesmo ponto"""
        distance = calculate_distance((100, 100), (100, 100))
        assert distance == 0.0
    
    def test_distance_horizontal(self):
        """Testa distância horizontal"""
        distance = calculate_distance((0, 0), (100, 0))
        assert distance == 100.0
    
    def test_distance_vertical(self):
        """Testa distância vertical"""
        distance = calculate_distance((0, 0), (0, 100))
        assert distance == 100.0
    
    def test_distance_diagonal(self):
        """Testa distância diagonal (Pitágoras)"""
        distance = calculate_distance((0, 0), (3, 4))
        assert distance == 5.0  # 3-4-5 triangle
    
    def test_distance_symmetry(self):
        """Testa se a distância é simétrica"""
        p1 = (100, 200)
        p2 = (300, 400)
        
        distance1 = calculate_distance(p1, p2)
        distance2 = calculate_distance(p2, p1)
        
        assert distance1 == distance2

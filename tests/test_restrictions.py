"""
Testes de integração para validar o sistema de roteamento com restrições
Mantido para compatibilidade - versão atualizada para pytest
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.service_points import (
    create_service_point, ServicePriority,
    sort_by_priority, validate_temperature_control_route,
    validate_special_protocol_sequence, TimeWindow
)
from src.core.genetic_algorithm import (
    calculate_constrained_fitness,
    generate_priority_aware_population,
    calculate_route_time_and_distance,
    constrained_order_crossover,
    constrained_mutate
)


class TestIntegrationPriorityOrdering:
    """Testes de integração para ordenação por prioridade"""
    
    def test_priority_ordering(self):
        """Testa se a ordenação por prioridade funciona corretamente"""
        points = [
            create_service_point(1, (100, 100), 'regular', None),
            create_service_point(2, (200, 200), 'emergency', None),
            create_service_point(3, (300, 300), 'medication', None),
            create_service_point(4, (400, 400), 'violence', None),
            create_service_point(5, (500, 500), 'postpartum', None),
        ]
        
        sorted_points = sort_by_priority(points)
        
        expected_order = [
            ServicePriority.EMERGENCY_OBSTETRIC,
            ServicePriority.DOMESTIC_VIOLENCE,
            ServicePriority.HORMONAL_MEDICATION,
            ServicePriority.POSTPARTUM_CARE,
            ServicePriority.REGULAR
        ]
        
        actual_order = [p.priority for p in sorted_points]
        assert actual_order == expected_order


class TestIntegrationTimeWindows:
    """Testes de integração para janelas de tempo"""
    
    def test_time_windows(self):
        """Testa validação de janelas de tempo"""
        window = TimeWindow(480, 600)  # 8h às 10h
        
        test_cases = [
            (450, False, "antes da janela", 0.0),  # Chegar cedo: sem penalidade (pode esperar)
            (500, True, "dentro da janela", 0.0),
            (650, False, "depois da janela", None),  # Atraso: deve ter penalidade
        ]
        
        for arrival_time, expected_valid, description, expected_penalty in test_cases:
            is_valid = window.is_valid_time(arrival_time)
            penalty = window.get_penalty(arrival_time)
            
            assert is_valid == expected_valid, f"Falhou para {description}"
            
            if expected_penalty is not None:
                assert penalty == expected_penalty, f"Penalidade deveria ser {expected_penalty} para {description}"
            else:
                # Atraso: deve ter penalidade > 0
                assert penalty > 0, f"Penalidade deveria ser > 0 para {description}"


class TestIntegrationTemperatureControl:
    """Testes de integração para controle de temperatura"""
    
    def test_temperature_control_valid_route(self):
        """Testa validação de controle de temperatura - rota válida"""
        route_valid = [
            create_service_point(1, (100, 100), 'medication', None),
            create_service_point(2, (150, 150), 'regular', None),
            create_service_point(3, (200, 200), 'medication', None),
        ]
        
        is_valid, message = validate_temperature_control_route(
            route_valid,
            max_time_without_control=120.0
        )
        
        assert is_valid is True
        assert "válida" in message.lower()
    
    def test_temperature_control_invalid_route(self):
        """Testa validação de controle de temperatura - rota inválida"""
        route_invalid = [
            create_service_point(1, (100, 100), 'medication', None),
            create_service_point(2, (500, 500), 'regular', None),
            create_service_point(3, (1000, 1000), 'regular', None),
            create_service_point(4, (1500, 1500), 'medication', None),
        ]
        
        is_valid, message = validate_temperature_control_route(
            route_invalid,
            max_time_without_control=120.0
        )
        
        assert is_valid is False


class TestIntegrationFitnessCalculation:
    """Testes de integração para cálculo de fitness"""
    
    def test_fitness_calculation(self):
        """Testa cálculo de fitness com restrições"""
        # Rota boa: emergências primeiro
        route_good = [
            create_service_point(1, (100, 100), 'emergency', None),
            create_service_point(2, (150, 150), 'violence', None),
            create_service_point(3, (200, 200), 'medication', None),
            create_service_point(4, (250, 250), 'regular', None),
        ]
        
        # Rota ruim: emergências por último
        route_bad = [
            create_service_point(1, (100, 100), 'regular', None),
            create_service_point(2, (150, 150), 'medication', None),
            create_service_point(3, (200, 200), 'violence', None),
            create_service_point(4, (250, 250), 'emergency', None),
        ]
        
        fitness_good = calculate_constrained_fitness(route_good)
        fitness_bad = calculate_constrained_fitness(route_bad)
        
        assert fitness_good < fitness_bad, "Rota com prioridades corretas deve ter melhor fitness"


class TestIntegrationPopulationGeneration:
    """Testes de integração para geração de população"""
    
    def test_population_generation(self):
        """Testa geração de população com viés de prioridade"""
        service_points = [
            create_service_point(1, (100, 100), 'emergency', None),
            create_service_point(2, (200, 200), 'violence', None),
            create_service_point(3, (300, 300), 'medication', None),
            create_service_point(4, (400, 400), 'postpartum', None),
            create_service_point(5, (500, 500), 'regular', None),
        ]
        
        population = generate_priority_aware_population(
            service_points,
            10,
            priority_bias=1.0
        )
        
        assert len(population) == 10, "População deve ter tamanho correto"
        
        # Verificar se emergências aparecem frequentemente no início
        emergency_first_count = sum(
            1 for route in population
            if route[0].priority == ServicePriority.EMERGENCY_OBSTETRIC
        )
        
        assert emergency_first_count >= 3, "Pelo menos 30% das rotas devem ter emergência primeiro"


class TestIntegrationGeneticOperators:
    """Testes de integração para operadores genéticos"""
    
    def test_genetic_operators(self):
        """Testa operadores genéticos (crossover e mutação)"""
        service_points = [
            create_service_point(1, (100, 100), 'emergency', None),
            create_service_point(2, (200, 200), 'violence', None),
            create_service_point(3, (300, 300), 'medication', None),
            create_service_point(4, (400, 400), 'regular', None),
        ]
        
        parent1 = service_points[:]
        parent2 = list(reversed(service_points))
        
        # Testar crossover
        child = constrained_order_crossover(parent1, parent2)
        
        child_ids = set(p.id for p in child)
        expected_ids = set(p.id for p in service_points)
        
        assert child_ids == expected_ids, "Crossover deve preservar todos os pontos"
        
        # Testar mutação
        mutated = constrained_mutate(child, mutation_probability=1.0)
        
        mutated_ids = set(p.id for p in mutated)
        assert mutated_ids == expected_ids, "Mutação deve preservar todos os pontos"


class TestIntegrationRouteCalculation:
    """Testes de integração para cálculos de rota"""
    
    def test_route_time_and_distance(self):
        """Testa cálculo de tempo e distância de rota"""
        depot = create_service_point(0, (250, 250), 'regular', None)
        depot.service_duration = 0.0
        
        route = [
            depot,
            create_service_point(1, (300, 300), 'emergency', None),
            create_service_point(2, (350, 350), 'regular', None),
        ]
        
        total_time, total_distance, arrival_times = calculate_route_time_and_distance(route)
        
        assert total_time > 0, "Tempo total deve ser positivo"
        assert total_distance > 0, "Distância total deve ser positiva"
        assert len(arrival_times) == len(route), "Deve haver tempo de chegada para cada ponto"
        
        # Verificar se tempos são crescentes
        for i in range(len(arrival_times) - 1):
            assert arrival_times[i] <= arrival_times[i + 1], "Tempos devem ser crescentes"


# Função para executar todos os testes (compatibilidade com versão antiga)
def run_all_tests():
    """Executa todos os testes usando pytest"""
    import subprocess
    result = subprocess.run(['pytest', __file__, '-v'], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    return result.returncode == 0


if __name__ == '__main__':
    # Executar com pytest
    pytest.main([__file__, '-v'])

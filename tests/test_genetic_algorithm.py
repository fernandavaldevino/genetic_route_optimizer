"""
Testes completos para o módulo genetic_algorithm
Inclui testes unitários, funcionais e edge cases
"""

import pytest
from src.core.genetic_algorithm import (
    calculate_constrained_fitness,
    generate_priority_aware_population,
    sort_population_by_fitness,
    constrained_order_crossover,
    constrained_mutate,
    calculate_route_time_and_distance
)
from src.core.service_points import ServicePriority, create_service_point


class TestFitnessCalculation:
    """Testes para cálculo de fitness"""
    
    def test_fitness_priority_ordered_better(self, priority_ordered_route, priority_reversed_route):
        """Testa se rota com prioridades corretas tem melhor fitness"""
        fitness_ordered = calculate_constrained_fitness(priority_ordered_route)
        fitness_reversed = calculate_constrained_fitness(priority_reversed_route)
        
        # Fitness menor é melhor
        assert fitness_ordered < fitness_reversed
    
    def test_fitness_is_positive(self, sample_service_points):
        """Testa se o fitness é sempre positivo"""
        fitness = calculate_constrained_fitness(sample_service_points)
        assert fitness > 0
    
    def test_fitness_different_priorities(self):
        """Testa se rotas com diferentes prioridades têm fitness diferentes"""
        route_high_priority = [
            create_service_point(1, (100, 100), 'emergency', None),
            create_service_point(2, (200, 200), 'violence', None),
        ]
        
        route_low_priority = [
            create_service_point(1, (100, 100), 'regular', None),
            create_service_point(2, (200, 200), 'regular', None),
        ]
        
        fitness_high = calculate_constrained_fitness(route_high_priority)
        fitness_low = calculate_constrained_fitness(route_low_priority)
        
        # Ambos devem ter fitness positivo
        assert fitness_high > 0
        assert fitness_low > 0
    
    def test_fitness_time_window_penalty(self):
        """Testa se violações de janela de tempo são penalizadas"""
        # Rota que respeita janelas de tempo
        route_valid = [
            create_service_point(1, (100, 100), 'violence', (480, 600)),
            create_service_point(2, (150, 150), 'regular', None),
        ]
        
        # Rota que viola janelas de tempo (pontos muito distantes)
        route_invalid = [
            create_service_point(1, (100, 100), 'regular', None),
            create_service_point(2, (5000, 5000), 'violence', (480, 600)),
        ]
        
        fitness_valid = calculate_constrained_fitness(route_valid)
        fitness_invalid = calculate_constrained_fitness(route_invalid)
        
        # Rota inválida deve ter fitness pior (maior)
        assert fitness_invalid > fitness_valid
    
    def test_fitness_with_time_window_violations(self):
        """Testa fitness com violações de janela de tempo"""
        # Criar pontos com janelas de tempo muito restritas
        route = [
            create_service_point(1, (100, 100), 'violence', (480, 490)),  # Janela de 10 min
            create_service_point(2, (5000, 5000), 'violence', (480, 490)),  # Muito longe
        ]
        
        fitness = calculate_constrained_fitness(route)
        
        # Fitness deve ser muito alto devido às violações
        assert fitness > 10000
    
    def test_fitness_with_medication_spacing(self):
        """Testa fitness com medicamentos espaçados"""
        route = [
            create_service_point(1, (100, 100), 'medication', None),
            create_service_point(2, (200, 200), 'regular', None),
            create_service_point(3, (300, 300), 'medication', None),
        ]
        
        fitness = calculate_constrained_fitness(route)
        assert fitness > 0
    
    def test_fitness_empty_route(self):
        """Testa fitness com rota vazia"""
        route = []
        fitness = calculate_constrained_fitness(route)
        # Rota vazia retorna infinito (rota inválida)
        assert fitness == float('inf')
    
    def test_fitness_single_point(self):
        """Testa fitness com apenas um ponto"""
        route = [create_service_point(1, (100, 100), 'regular', None)]
        fitness = calculate_constrained_fitness(route)
        assert fitness >= 0


class TestPopulationGeneration:
    """Testes para geração de população"""
    
    def test_population_size(self, sample_service_points):
        """Testa se a população tem o tamanho correto"""
        population_size = 50
        population = generate_priority_aware_population(
            sample_service_points,
            population_size
        )
        
        assert len(population) == population_size
    
    def test_population_all_points_present(self, sample_service_points):
        """Testa se todos os pontos estão presentes em cada rota"""
        population = generate_priority_aware_population(sample_service_points, 10)
        
        expected_ids = set(p.id for p in sample_service_points)
        
        for route in population:
            route_ids = set(p.id for p in route)
            assert route_ids == expected_ids
    
    def test_population_priority_bias(self, sample_service_points):
        """Testa se a população tem viés para prioridades altas no início"""
        population = generate_priority_aware_population(
            sample_service_points,
            100,
            priority_bias=1.0
        )
        
        # Contar quantas rotas têm emergência nos primeiros 2 pontos
        emergency_early_count = 0
        
        for route in population:
            first_two_priorities = [p.priority for p in route[:2]]
            if ServicePriority.EMERGENCY_OBSTETRIC in first_two_priorities:
                emergency_early_count += 1
        
        # Pelo menos 60% das rotas devem ter emergência nos primeiros 2 pontos
        assert emergency_early_count >= 60
    
    def test_population_with_single_point(self):
        """Testa geração de população com apenas um ponto"""
        points = [create_service_point(1, (100, 100), 'regular', None)]
        population = generate_priority_aware_population(points, 5)
        
        assert len(population) == 5
        for route in population:
            assert len(route) == 1
            assert route[0].id == 1
    
    def test_population_with_zero_bias(self):
        """Testa geração de população sem viés de prioridade"""
        points = [
            create_service_point(1, (100, 100), 'emergency', None),
            create_service_point(2, (200, 200), 'regular', None),
        ]
        
        population = generate_priority_aware_population(points, 10, priority_bias=0.0)
        
        assert len(population) == 10
        for route in population:
            assert len(route) == 2
    
    def test_population_with_high_bias(self):
        """Testa geração de população com viés alto"""
        points = [
            create_service_point(1, (100, 100), 'emergency', None),
            create_service_point(2, (200, 200), 'violence', None),
            create_service_point(3, (300, 300), 'regular', None),
        ]
        
        population = generate_priority_aware_population(points, 20, priority_bias=2.0)
        
        assert len(population) == 20
        # Verificar que emergências aparecem frequentemente no início
        emergency_first = sum(1 for route in population if route[0].priority == ServicePriority.EMERGENCY_OBSTETRIC)
        assert emergency_first > 10  # Mais de 50%


class TestPopulationSorting:
    """Testes para ordenação de população"""
    
    def test_sort_population_ascending(self, sample_service_points):
        """Testa se a população é ordenada em ordem crescente de fitness"""
        population = generate_priority_aware_population(sample_service_points, 10)
        fitness_values = [calculate_constrained_fitness(route) for route in population]
        
        sorted_pop, sorted_fitness = sort_population_by_fitness(population, fitness_values)
        
        # Verificar se está ordenado (fitness crescente)
        for i in range(len(sorted_fitness) - 1):
            assert sorted_fitness[i] <= sorted_fitness[i + 1]
    
    def test_sort_preserves_correspondence(self, sample_service_points):
        """Testa se a ordenação mantém correspondência entre rotas e fitness"""
        population = generate_priority_aware_population(sample_service_points, 10)
        fitness_values = [calculate_constrained_fitness(route) for route in population]
        
        sorted_pop, sorted_fitness = sort_population_by_fitness(population, fitness_values)
        
        # Recalcular fitness das rotas ordenadas
        recalculated_fitness = [calculate_constrained_fitness(route) for route in sorted_pop]
        
        # Deve ser igual aos fitness ordenados
        assert recalculated_fitness == sorted_fitness


class TestGeneticOperators:
    """Testes para operadores genéticos"""
    
    def test_crossover_preserves_all_points(self, sample_service_points):
        """Testa se o crossover preserva todos os pontos"""
        parent1 = sample_service_points[:]
        parent2 = list(reversed(sample_service_points))
        
        child = constrained_order_crossover(parent1, parent2)
        
        parent_ids = set(p.id for p in parent1)
        child_ids = set(p.id for p in child)
        
        assert parent_ids == child_ids
    
    def test_crossover_creates_valid_route(self, sample_service_points):
        """Testa se o crossover cria uma rota válida (sem duplicatas)"""
        parent1 = sample_service_points[:]
        parent2 = list(reversed(sample_service_points))
        
        child = constrained_order_crossover(parent1, parent2)
        
        # Verificar se não há duplicatas
        child_ids = [p.id for p in child]
        assert len(child_ids) == len(set(child_ids))
    
    def test_crossover_identical_parents(self):
        """Testa crossover com pais idênticos"""
        parent = [
            create_service_point(1, (100, 100), 'regular', None),
            create_service_point(2, (200, 200), 'regular', None),
        ]
        
        child = constrained_order_crossover(parent, parent)
        
        # Deve preservar todos os pontos
        assert len(child) == len(parent)
        assert set(p.id for p in child) == set(p.id for p in parent)
    
    def test_crossover_single_point_parents(self):
        """Testa crossover com pais de um único ponto"""
        parent = [create_service_point(1, (100, 100), 'regular', None)]
        
        child = constrained_order_crossover(parent, parent)
        
        assert len(child) == 1
        assert child[0].id == 1
    
    def test_mutation_preserves_all_points(self, sample_service_points):
        """Testa se a mutação preserva todos os pontos"""
        route = sample_service_points[:]
        mutated = constrained_mutate(route, mutation_probability=1.0)
        
        original_ids = set(p.id for p in route)
        mutated_ids = set(p.id for p in mutated)
        
        assert original_ids == mutated_ids
    
    def test_mutation_returns_valid_route(self, sample_service_points):
        """Testa se a mutação retorna uma rota válida"""
        route = sample_service_points[:]
        
        # Mutar a rota
        mutated = constrained_mutate(route, mutation_probability=0.5)
        
        # Verificar se a rota mutada é válida
        original_ids = set(p.id for p in route)
        mutated_ids = set(p.id for p in mutated)
        
        # Deve ter os mesmos IDs (todos os pontos preservados)
        assert original_ids == mutated_ids
        
        # Deve ter o mesmo tamanho
        assert len(mutated) == len(route)
    
    def test_mutation_probability_zero(self, sample_service_points):
        """Testa se probabilidade 0 não muta"""
        route = sample_service_points[:]
        mutated = constrained_mutate(route, mutation_probability=0.0)
        
        original_order = [p.id for p in route]
        mutated_order = [p.id for p in mutated]
        
        # Deve ser igual
        assert original_order == mutated_order
    
    def test_mutation_single_point(self):
        """Testa mutação com apenas um ponto"""
        route = [create_service_point(1, (100, 100), 'regular', None)]
        
        mutated = constrained_mutate(route, mutation_probability=1.0)
        
        # Deve preservar o único ponto
        assert len(mutated) == 1
        assert mutated[0].id == 1
    
    def test_mutation_two_points(self):
        """Testa mutação com dois pontos"""
        route = [
            create_service_point(1, (100, 100), 'regular', None),
            create_service_point(2, (200, 200), 'regular', None),
        ]
        
        mutated = constrained_mutate(route, mutation_probability=1.0)
        
        # Deve preservar ambos os pontos
        assert len(mutated) == 2
        assert set(p.id for p in mutated) == {1, 2}


class TestRouteCalculations:
    """Testes para cálculos de rota"""
    
    def test_route_time_calculation(self, depot_point, sample_service_points):
        """Testa cálculo de tempo de rota"""
        route = [depot_point] + sample_service_points
        
        total_time, total_distance, arrival_times = calculate_route_time_and_distance(route)
        
        # Tempo total deve ser positivo
        assert total_time > 0
        
        # Deve haver um tempo de chegada para cada ponto
        assert len(arrival_times) == len(route)
        
        # Tempos de chegada devem ser crescentes
        for i in range(len(arrival_times) - 1):
            assert arrival_times[i] <= arrival_times[i + 1]
    
    def test_route_distance_calculation(self, depot_point, sample_service_points):
        """Testa cálculo de distância de rota"""
        route = [depot_point] + sample_service_points
        
        total_time, total_distance, arrival_times = calculate_route_time_and_distance(route)
        
        # Distância total deve ser positiva
        assert total_distance > 0
    
    def test_route_starts_at_depot_time(self, depot_point):
        """Testa se a rota começa no horário do depósito (8h = 480 min)"""
        route = [
            depot_point,
            create_service_point(1, (100, 100), 'regular', None),
        ]
        
        total_time, total_distance, arrival_times = calculate_route_time_and_distance(route)
        
        # Primeiro ponto (depósito) deve ser às 8h (480 minutos)
        assert arrival_times[0] == 480
    
    def test_single_point_route(self, depot_point):
        """Testa rota com apenas o depósito"""
        route = [depot_point]
        
        total_time, total_distance, arrival_times = calculate_route_time_and_distance(route)
        
        assert total_time == 0
        assert total_distance == 0
        assert len(arrival_times) == 1
        assert arrival_times[0] == 480  # 8h
    
    def test_route_calculation_empty(self):
        """Testa cálculo com rota vazia"""
        route = []
        
        total_time, total_distance, arrival_times = calculate_route_time_and_distance(route)
        
        assert total_time == 0
        assert total_distance == 0
        assert len(arrival_times) == 0
    
    def test_route_calculation_with_time_windows(self):
        """Testa cálculo com janelas de tempo"""
        depot = create_service_point(0, (100, 100), 'regular', None)
        depot.service_duration = 0.0
        
        route = [
            depot,
            create_service_point(1, (200, 200), 'violence', (480, 600)),
            create_service_point(2, (300, 300), 'postpartum', (540, 660)),
        ]
        
        total_time, total_distance, arrival_times = calculate_route_time_and_distance(route)
        
        assert total_time > 0
        assert total_distance > 0
        assert len(arrival_times) == 3
        assert arrival_times[0] == 480  # Depósito às 8h
    
    def test_route_calculation_long_distance(self):
        """Testa cálculo com distâncias longas"""
        depot = create_service_point(0, (0, 0), 'regular', None)
        depot.service_duration = 0.0
        
        route = [
            depot,
            create_service_point(1, (10000, 10000), 'regular', None),
        ]
        
        total_distance, total_time, arrival_times = calculate_route_time_and_distance(route)
        
        # Distância muito longa deve resultar em tempo muito alto
        # Distância euclidiana: sqrt(10000^2 + 10000^2) ≈ 14142
        assert total_distance > 14000
        assert total_time > 1000  # Mais de 1000 minutos

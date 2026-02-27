"""
Testes de integração end-to-end
Testa fluxos completos do sistema de otimização
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
from src.core.service_points import (
    create_service_point,
    ServicePriority,
    sort_by_priority,
    validate_temperature_control_route
)


class TestEndToEndOptimization:
    """Testes de integração para fluxo completo de otimização"""
    
    def test_complete_optimization_cycle(self):
        """Testa um ciclo completo de otimização"""
        # 1. Criar pontos de serviço
        service_points = [
            create_service_point(1, (100, 100), 'emergency', None),
            create_service_point(2, (200, 200), 'violence', (480, 600)),
            create_service_point(3, (300, 300), 'medication', None),
            create_service_point(4, (400, 400), 'postpartum', (540, 660)),
            create_service_point(5, (500, 500), 'regular', None),
        ]
        
        # 2. Gerar população inicial
        population = generate_priority_aware_population(service_points, 20)
        assert len(population) == 20
        
        # 3. Calcular fitness
        fitness_values = [calculate_constrained_fitness(route) for route in population]
        assert len(fitness_values) == 20
        assert all(f >= 0 for f in fitness_values)
        
        # 4. Ordenar população
        sorted_pop, sorted_fitness = sort_population_by_fitness(population, fitness_values)
        assert len(sorted_pop) == 20
        assert sorted_fitness[0] <= sorted_fitness[-1]  # Melhor fitness primeiro
        
        # 5. Aplicar crossover
        parent1 = sorted_pop[0]
        parent2 = sorted_pop[1]
        child = constrained_order_crossover(parent1, parent2)
        assert len(child) == len(parent1)
        
        # 6. Aplicar mutação
        mutated = constrained_mutate(child, mutation_probability=0.5)
        assert len(mutated) == len(child)
        
        # 7. Calcular fitness do filho
        child_fitness = calculate_constrained_fitness(mutated)
        assert child_fitness >= 0
    
    def test_multi_generation_evolution(self):
        """Testa evolução através de múltiplas gerações"""
        service_points = [
            create_service_point(1, (100, 100), 'emergency', None),
            create_service_point(2, (200, 200), 'violence', None),
            create_service_point(3, (300, 300), 'regular', None),
        ]
        
        population = generate_priority_aware_population(service_points, 10)
        
        best_fitness_history = []
        
        # Simular 5 gerações
        for generation in range(5):
            # Calcular fitness
            fitness_values = [calculate_constrained_fitness(route) for route in population]
            
            # Ordenar
            population, fitness_values = sort_population_by_fitness(population, fitness_values)
            
            # Guardar melhor fitness
            best_fitness_history.append(fitness_values[0])
            
            # Criar nova população
            new_population = [population[0]]  # Elitismo
            
            while len(new_population) < 10:
                parent1 = population[0]
                parent2 = population[1]
                child = constrained_order_crossover(parent1, parent2)
                child = constrained_mutate(child, mutation_probability=0.3)
                new_population.append(child)
            
            population = new_population
        
        # Verificar que temos histórico de 5 gerações
        assert len(best_fitness_history) == 5
        
        # Fitness deve ser positivo em todas as gerações
        assert all(f > 0 for f in best_fitness_history)


class TestIntegrationWithConstraints:
    """Testes de integração com restrições"""
    
    def test_priority_ordering_integration(self):
        """Testa integração de ordenação por prioridade com fitness"""
        points = [
            create_service_point(1, (100, 100), 'regular', None),
            create_service_point(2, (200, 200), 'emergency', None),
            create_service_point(3, (300, 300), 'violence', None),
        ]
        
        # Ordenar por prioridade
        sorted_points = sort_by_priority(points)
        
        # Verificar que a ordenação está correta
        assert sorted_points[0].priority.value == 1  # Emergency primeiro
        assert sorted_points[1].priority.value == 2  # Violence segundo
        assert sorted_points[2].priority.value == 5  # Regular último
        
        # Calcular fitness de ambas as rotas
        fitness_sorted = calculate_constrained_fitness(sorted_points)
        fitness_unsorted = calculate_constrained_fitness(points)
        
        # Ambos devem ter fitness válido (>= 0)
        assert fitness_sorted >= 0
        assert fitness_unsorted >= 0
    
    def test_temperature_control_integration(self):
        """Testa integração de controle de temperatura com otimização"""
        route = [
            create_service_point(1, (100, 100), 'medication', None),
            create_service_point(2, (150, 150), 'regular', None),
            create_service_point(3, (200, 200), 'medication', None),
        ]
        
        # Validar controle de temperatura
        is_valid, message = validate_temperature_control_route(route)
        
        # Calcular fitness
        fitness = calculate_constrained_fitness(route)
        
        # Se rota é válida, fitness não deve ter penalidade extrema
        if is_valid:
            assert fitness < 10000
    
    def test_time_window_integration(self):
        """Testa integração de janelas de tempo com cálculo de rota"""
        depot = create_service_point(0, (100, 100), 'regular', None)
        depot.service_duration = 0.0
        
        route = [
            depot,
            create_service_point(1, (200, 200), 'violence', (480, 600)),
        ]
        
        # Calcular tempos de chegada
        total_time, total_distance, arrival_times = calculate_route_time_and_distance(route)
        
        # Verificar se chegada está dentro da janela
        violence_point = route[1]
        arrival_at_violence = arrival_times[1]
        
        # Calcular fitness
        fitness = calculate_constrained_fitness(route)
        
        # Se chegada está dentro da janela, fitness deve ser razoável
        if violence_point.time_window.is_valid_time(arrival_at_violence):
            assert fitness < 5000


class TestRobustness:
    """Testes de robustez do sistema"""
    
    def test_large_population(self):
        """Testa com população grande"""
        points = [
            create_service_point(i, (i*100, i*100), 'regular', None)
            for i in range(1, 11)
        ]
        
        population = generate_priority_aware_population(points, 100)
        
        assert len(population) == 100
        for route in population:
            assert len(route) == 10
    
    def test_many_generations(self):
        """Testa estabilidade através de muitas gerações"""
        points = [
            create_service_point(1, (100, 100), 'emergency', None),
            create_service_point(2, (200, 200), 'regular', None),
        ]
        
        population = generate_priority_aware_population(points, 5)
        
        # Simular 20 gerações
        for _ in range(20):
            fitness_values = [calculate_constrained_fitness(route) for route in population]
            population, fitness_values = sort_population_by_fitness(population, fitness_values)
            
            new_population = [population[0]]
            while len(new_population) < 5:
                child = constrained_order_crossover(population[0], population[1])
                child = constrained_mutate(child, mutation_probability=0.3)
                new_population.append(child)
            
            population = new_population
        
        # Sistema deve permanecer estável
        final_fitness = [calculate_constrained_fitness(route) for route in population]
        assert all(f >= 0 for f in final_fitness)
    
    def test_extreme_distances(self):
        """Testa com distâncias extremas"""
        depot = create_service_point(0, (0, 0), 'regular', None)
        depot.service_duration = 0.0
        
        route = [
            depot,
            create_service_point(1, (50000, 50000), 'regular', None),
        ]
        
        total_time, total_distance, arrival_times = calculate_route_time_and_distance(route)
        
        # Sistema deve lidar com distâncias extremas sem crash
        assert total_time > 0
        assert total_distance > 0
        assert len(arrival_times) == 2

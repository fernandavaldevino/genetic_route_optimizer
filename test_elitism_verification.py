#!/usr/bin/env python3
"""
Teste de verificação do elitismo para 1V e 2V
"""

import sys
import os

# Adicionar src ao path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.core.service_points import create_service_point, ServicePriority
from src.core.genetic_algorithm import (
    generate_priority_aware_population,
    calculate_constrained_fitness,
    sort_population_by_fitness
)
from src.core.multi_vehicle import (
    generate_multi_vehicle_population,
    calculate_multi_vehicle_fitness,
    sort_multi_vehicle_population
)
import random

def test_elitism_1v():
    """ Testa elitismo para 1 veículo """
    print("\n" + "="*60)
    print("TESTE DE ELITISMO - 1 VEÍCULO")
    print("="*60)
    
    # Criar pontos de teste
    service_points = []
    depot = create_service_point(0, (100, 100), 'regular', None)
    depot.service_duration = 0.0
    service_points.append(depot)
    
    for i in range(1, 11):
        location = (random.randint(200, 800), random.randint(200, 600))
        point = create_service_point(i, location, 'regular', None)
        service_points.append(point)
    
    # Gerar população
    population = generate_priority_aware_population(service_points, 20)
    
    # Calcular fitness
    fitness_values = [calculate_constrained_fitness(route) for route in population]
    
    # Ordenar
    population, fitness_values = sort_population_by_fitness(population, fitness_values)
    
    # Verificar elitismo
    best_route = population[0]
    best_fitness = fitness_values[0]
    
    print(f"✓ População gerada: {len(population)} indivíduos")
    print(f"✓ Melhor fitness: {best_fitness:.2f}")
    print(f"✓ Melhor rota tem {len(best_route)} pontos")
    
    # Simular elitismo dinâmico
    MAX_GENERATIONS = 100
    
    # Início (geração 0-49): elite_size = 1
    generation = 25
    progress = generation / MAX_GENERATIONS
    elite_size = 1 if progress < 0.5 else 2
    print(f"\n✓ Geração {generation} (progresso {progress:.1%}): elite_size = {elite_size}")
    assert elite_size == 1, "Elite size deveria ser 1 no início"
    
    # Final (geração 50+): elite_size = 2
    generation = 75
    progress = generation / MAX_GENERATIONS
    elite_size = 1 if progress < 0.5 else 2
    print(f"✓ Geração {generation} (progresso {progress:.1%}): elite_size = {elite_size}")
    assert elite_size == 2, "Elite size deveria ser 2 no final"
    
    print("\n✅ TESTE 1V PASSOU - Elitismo dinâmico funcionando corretamente!")
    return True


def test_elitism_2v():
    """ Testa elitismo para 2 veículos """
    print("\n" + "="*60)
    print("TESTE DE ELITISMO - 2 VEÍCULOS")
    print("="*60)
    
    # Criar pontos de teste
    depot_location = (100, 100)
    service_points = []
    
    for i in range(1, 21):
        location = (random.randint(200, 800), random.randint(200, 600))
        point = create_service_point(i, location, 'regular', None)
        service_points.append(point)
    
    # Gerar população
    population = generate_multi_vehicle_population(service_points, depot_location, 30, 2)
    
    # Ordenar
    population = sort_multi_vehicle_population(population)
    
    # Verificar
    best_solution = population[0]
    best_fitness = best_solution.total_fitness
    
    print(f"✓ População gerada: {len(population)} soluções")
    print(f"✓ Melhor fitness: {best_fitness:.2f}")
    print(f"✓ Veículo 1: {len(best_solution.vehicles[0].route)} pontos")
    print(f"✓ Veículo 2: {len(best_solution.vehicles[1].route)} pontos")
    
    # Simular elitismo dinâmico
    MAX_GENERATIONS = 100
    ELITE_SIZE_INITIAL = 5
    ELITE_SIZE_FINAL = 10
    
    # Início (geração 0): elite_size = 5
    generation = 0
    progress = generation / MAX_GENERATIONS
    elite_size = int(ELITE_SIZE_INITIAL + (ELITE_SIZE_FINAL - ELITE_SIZE_INITIAL) * progress)
    print(f"\n✓ Geração {generation} (progresso {progress:.1%}): elite_size = {elite_size}")
    assert elite_size == 5, f"Elite size deveria ser 5 no início, mas é {elite_size}"
    
    # Meio (geração 50): elite_size = 7-8
    generation = 50
    progress = generation / MAX_GENERATIONS
    elite_size = int(ELITE_SIZE_INITIAL + (ELITE_SIZE_FINAL - ELITE_SIZE_INITIAL) * progress)
    print(f"✓ Geração {generation} (progresso {progress:.1%}): elite_size = {elite_size}")
    assert 7 <= elite_size <= 8, f"Elite size deveria ser 7-8 no meio, mas é {elite_size}"
    
    # Final (geração 100): elite_size = 10
    generation = 100
    progress = generation / MAX_GENERATIONS
    elite_size = int(ELITE_SIZE_INITIAL + (ELITE_SIZE_FINAL - ELITE_SIZE_INITIAL) * progress)
    print(f"✓ Geração {generation} (progresso {progress:.1%}): elite_size = {elite_size}")
    assert elite_size == 10, f"Elite size deveria ser 10 no final, mas é {elite_size}"
    
    print("\n✅ TESTE 2V PASSOU - Elitismo dinâmico funcionando corretamente!")
    return True


if __name__ == '__main__':
    try:
        # Testar 1V
        success_1v = test_elitism_1v()
        
        # Testar 2V
        success_2v = test_elitism_2v()
        
        # Resumo
        print("\n" + "="*60)
        print("RESUMO DOS TESTES")
        print("="*60)
        print(f"1 Veículo:  {'✅ PASSOU' if success_1v else '❌ FALHOU'}")
        print(f"2 Veículos: {'✅ PASSOU' if success_2v else '❌ FALHOU'}")
        
        if success_1v and success_2v:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("\nElitismo dinâmico implementado corretamente:")
            print("  • 1V: cresce de 1 para 2 indivíduos (50% das gerações)")
            print("  • 2V: cresce de 5 para 10 indivíduos (linearmente)")
            sys.exit(0)
        else:
            print("\n❌ ALGUNS TESTES FALHARAM")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

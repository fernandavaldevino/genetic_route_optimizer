"""
Testes para validar o sistema de roteamento com restrições
"""

import sys
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.service_points import (
    create_service_point, ServicePriority,
    sort_by_priority, validate_temperature_control_route,
    validate_special_protocol_sequence, TimeWindow
)
from core.genetic_algorithm import (
    calculate_constrained_fitness,
    generate_priority_aware_population,
    calculate_route_time_and_distance,
    constrained_order_crossover,
    constrained_mutate
)


def test_priority_ordering():
    """Testa se a ordenação por prioridade funciona corretamente"""
    print("\n" + "="*60)
    print("TESTE 1: Ordenação por Prioridade")
    print("="*60)
    
    points = [
        create_service_point(1, (100, 100), 'regular'),
        create_service_point(2, (200, 200), 'emergency'),
        create_service_point(3, (300, 300), 'medication'),
        create_service_point(4, (400, 400), 'violence'),
        create_service_point(5, (500, 500), 'postpartum'),
    ]
    
    sorted_points = sort_by_priority(points)
    
    print("\nOrdem original:")
    for p in points:
        print(f"  ID {p.id}: {p.priority.name}")
    
    print("\nOrdem após ordenação por prioridade:")
    for p in sorted_points:
        print(f"  ID {p.id}: {p.priority.name} (peso: {p.get_priority_weight()})")
    
    # Verificar se está ordenado corretamente
    expected_order = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE,
        ServicePriority.REGULAR
    ]
    
    actual_order = [p.priority for p in sorted_points]
    
    if actual_order == expected_order:
        print("\n✓ TESTE PASSOU: Ordenação correta!")
        return True
    else:
        print("\n✗ TESTE FALHOU: Ordenação incorreta!")
        return False


def test_time_windows():
    """Testa validação de janelas de tempo"""
    print("\n" + "="*60)
    print("TESTE 2: Janelas de Tempo")
    print("="*60)
    
    # Criar janela de tempo: 8h às 10h (480 a 600 minutos)
    time_window = TimeWindow(480, 600)
    
    test_cases = [
        (450, "antes da janela"),
        (500, "dentro da janela"),
        (650, "depois da janela"),
    ]
    
    print("\nJanela de tempo: 08:00 - 10:00")
    all_passed = True
    
    for arrival_time, description in test_cases:
        hours = int(arrival_time // 60)
        minutes = int(arrival_time % 60)
        is_valid = time_window.is_valid_time(arrival_time)
        penalty = time_window.get_penalty(arrival_time)
        
        print(f"\nChegada às {hours:02d}:{minutes:02d} ({description}):")
        print(f"  Válido: {is_valid}")
        print(f"  Penalidade: {penalty:.2f}")
        
        # Verificar lógica
        if description == "dentro da janela" and not is_valid:
            print("  ✗ ERRO: Deveria ser válido!")
            all_passed = False
        elif description != "dentro da janela" and is_valid:
            print("  ✗ ERRO: Não deveria ser válido!")
            all_passed = False
        else:
            print("  ✓ OK")
    
    if all_passed:
        print("\n✓ TESTE PASSOU: Janelas de tempo funcionando!")
        return True
    else:
        print("\n✗ TESTE FALHOU: Problemas com janelas de tempo!")
        return False


def test_temperature_control():
    """Testa validação de controle de temperatura"""
    print("\n" + "="*60)
    print("TESTE 3: Controle de Temperatura")
    print("="*60)
    
    # Rota válida: medicamentos próximos
    route_valid = [
        create_service_point(1, (100, 100), 'medication'),
        create_service_point(2, (150, 150), 'regular'),
        create_service_point(3, (200, 200), 'medication'),
    ]
    
    # Rota inválida: medicamentos muito distantes
    route_invalid = [
        create_service_point(1, (100, 100), 'medication'),
        create_service_point(2, (500, 500), 'regular'),
        create_service_point(3, (1000, 1000), 'regular'),
        create_service_point(4, (1500, 1500), 'medication'),
    ]
    
    print("\nTestando rota válida (medicamentos próximos):")
    is_valid, message = validate_temperature_control_route(route_valid, max_time_without_control=120.0)
    print(f"  Resultado: {message}")
    print(f"  {'✓ OK' if is_valid else '✗ ERRO'}")
    
    print("\nTestando rota inválida (medicamentos distantes):")
    is_valid2, message2 = validate_temperature_control_route(route_invalid, max_time_without_control=120.0)
    print(f"  Resultado: {message2}")
    print(f"  {'✓ OK' if not is_valid2 else '✗ ERRO: Deveria ser inválida!'}")
    
    if is_valid and not is_valid2:
        print("\n✓ TESTE PASSOU: Validação de temperatura funcionando!")
        return True
    else:
        print("\n✗ TESTE FALHOU: Problemas na validação de temperatura!")
        return False


def test_fitness_calculation():
    """Testa cálculo de fitness com restrições"""
    print("\n" + "="*60)
    print("TESTE 4: Cálculo de Fitness")
    print("="*60)
    
    # Rota boa: emergências primeiro
    route_good = [
        create_service_point(1, (100, 100), 'emergency'),
        create_service_point(2, (150, 150), 'violence'),
        create_service_point(3, (200, 200), 'medication'),
        create_service_point(4, (250, 250), 'regular'),
    ]
    
    # Rota ruim: emergências por último
    route_bad = [
        create_service_point(1, (100, 100), 'regular'),
        create_service_point(2, (150, 150), 'medication'),
        create_service_point(3, (200, 200), 'violence'),
        create_service_point(4, (250, 250), 'emergency'),
    ]
    
    fitness_good = calculate_constrained_fitness(route_good)
    fitness_bad = calculate_constrained_fitness(route_bad)
    
    print(f"\nFitness da rota boa (emergências primeiro): {fitness_good:.2f}")
    print(f"Fitness da rota ruim (emergências por último): {fitness_bad:.2f}")
    
    if fitness_good < fitness_bad:
        print("\n✓ TESTE PASSOU: Rota com prioridades corretas tem melhor fitness!")
        return True
    else:
        print("\n✗ TESTE FALHOU: Fitness não está penalizando ordem incorreta!")
        return False


def test_population_generation():
    """Testa geração de população com viés de prioridade"""
    print("\n" + "="*60)
    print("TESTE 5: Geração de População")
    print("="*60)
    
    service_points = [
        create_service_point(1, (100, 100), 'emergency'),
        create_service_point(2, (200, 200), 'violence'),
        create_service_point(3, (300, 300), 'medication'),
        create_service_point(4, (400, 400), 'postpartum'),
        create_service_point(5, (500, 500), 'regular'),
    ]
    
    population = generate_priority_aware_population(service_points, 10, priority_bias=1.0)
    
    print(f"\nGerada população de {len(population)} indivíduos")
    print("\nPrimeiros 3 pontos de cada rota:")
    
    emergency_first_count = 0
    
    for i, route in enumerate(population[:5]):
        first_three = [f"P{p.id}({p.priority.name[:3]})" for p in route[:3]]
        print(f"  Rota {i+1}: {' -> '.join(first_three)}")
        
        if route[0].priority == ServicePriority.EMERGENCY_OBSTETRIC:
            emergency_first_count += 1
    
    print(f"\nRotas com emergência em primeiro: {emergency_first_count}/5")
    
    if emergency_first_count >= 3:
        print("\n✓ TESTE PASSOU: População tem viés para prioridades!")
        return True
    else:
        print("\n✗ TESTE FALHOU: População não está respeitando prioridades!")
        return False


def test_genetic_operators():
    """Testa operadores genéticos (crossover e mutação)"""
    print("\n" + "="*60)
    print("TESTE 6: Operadores Genéticos")
    print("="*60)
    
    service_points = [
        create_service_point(1, (100, 100), 'emergency'),
        create_service_point(2, (200, 200), 'violence'),
        create_service_point(3, (300, 300), 'medication'),
        create_service_point(4, (400, 400), 'regular'),
    ]
    
    parent1 = service_points[:]
    parent2 = list(reversed(service_points))
    
    print("\nPai 1:", [f"P{p.id}" for p in parent1])
    print("Pai 2:", [f"P{p.id}" for p in parent2])
    
    # Testar crossover
    child = constrained_order_crossover(parent1, parent2)
    print("\nFilho (crossover):", [f"P{p.id}" for p in child])
    
    # Verificar se todos os pontos estão presentes
    child_ids = set(p.id for p in child)
    expected_ids = set(p.id for p in service_points)
    
    crossover_valid = child_ids == expected_ids
    print(f"Crossover válido (todos os pontos presentes): {crossover_valid}")
    
    # Testar mutação
    mutated = constrained_mutate(child, mutation_probability=1.0)
    print("\nFilho mutado:", [f"P{p.id}" for p in mutated])
    
    mutated_ids = set(p.id for p in mutated)
    mutation_valid = mutated_ids == expected_ids
    print(f"Mutação válida (todos os pontos presentes): {mutation_valid}")
    
    if crossover_valid and mutation_valid:
        print("\n✓ TESTE PASSOU: Operadores genéticos funcionando!")
        return True
    else:
        print("\n✗ TESTE FALHOU: Problemas nos operadores genéticos!")
        return False


def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("EXECUTANDO SUITE DE TESTES")
    print("="*60)
    
    tests = [
        ("Ordenação por Prioridade", test_priority_ordering),
        ("Janelas de Tempo", test_time_windows),
        ("Controle de Temperatura", test_temperature_control),
        ("Cálculo de Fitness", test_fitness_calculation),
        ("Geração de População", test_population_generation),
        ("Operadores Genéticos", test_genetic_operators),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ ERRO no teste '{test_name}': {str(e)}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"Resultado Final: {passed}/{total} testes passaram")
    print("="*60)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

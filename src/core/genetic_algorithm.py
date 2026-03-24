"""
Algoritmo Genético com Restrições para Roteamento de Atendimentos
Incorpora prioridades, janelas de tempo e requisitos especiais
"""

import random
import math
import copy
from typing import List, Tuple, Optional
from .service_points import (
    ServicePoint, ServicePriority, TimeWindow,
    calculate_distance, calculate_travel_time,
    sort_by_priority, validate_temperature_control_route,
    validate_special_protocol_sequence
)


def calculate_route_time_and_distance(route: List[ServicePoint],
                                      start_time: float = 480.0,
                                      speed: float = 60.0,
                                      work_start: float = 480.0,
                                      work_end: float = 1080.0) -> Tuple[float, float, List[float]]:
    """
    Calcula tempo total e distância de uma rota, considerando tempos de serviço
    e pausas noturnas (horário comercial: 8h-18h)
    """
    if not route:
        return 0.0, 0.0, []
    
    total_distance = 0.0
    current_time = start_time
    arrival_times = []
    
    for i in range(len(route)):
        # Se passou do horário comercial, pausar até o próximo dia
        current_day = int(current_time // 1440)  # Dia atual (1440 min = 24h)
        time_of_day = current_time % 1440  # Hora do dia atual
        
        # Se estamos fora do horário comercial, avançar para o próximo dia às 8h
        if time_of_day < work_start or time_of_day >= work_end:
            # Calcular próximo horário de início
            if time_of_day >= work_end:
                # Passou das 18h, ir para 8h do dia seguinte
                current_time = (current_day + 1) * 1440 + work_start
            else:
                # Antes das 8h, ir para 8h do mesmo dia
                current_time = current_day * 1440 + work_start
        
        arrival_times.append(current_time)
        
        # Adicionar tempo de serviço
        current_time += route[i].service_duration
        
        # Verificar se o serviço termina após 18h
        time_after_service = current_time % 1440
        if time_after_service >= work_end:
            # Serviço terminou após 18h, próxima entrega será no dia seguinte
            current_day = int(current_time // 1440)
            current_time = (current_day + 1) * 1440 + work_start
        
        # Calcular distância e tempo até o próximo ponto
        if i < len(route) - 1:
            distance = calculate_distance(route[i].location, route[i + 1].location)
            total_distance += distance
            travel_time = calculate_travel_time(route[i].location, route[i + 1].location, speed)
            current_time += travel_time
            
            # Verificar se a viagem termina após 18h
            time_after_travel = current_time % 1440
            if time_after_travel >= work_end:
                # Viagem terminou após 18h, pausar até 8h do dia seguinte
                current_day = int(current_time // 1440)
                current_time = (current_day + 1) * 1440 + work_start
    
    # Adicionar retorno ao depósito (ponto 0)
    if len(route) > 1:
        depot = route[0]
        last_point = route[-1]
        
        # Calcular distância e tempo de retorno ao depósito
        return_distance = calculate_distance(last_point.location, depot.location)
        total_distance += return_distance
        return_travel_time = calculate_travel_time(last_point.location, depot.location, speed)
        current_time += return_travel_time
        
        # Verificar se o retorno termina após 18h
        time_after_return = current_time % 1440
        if time_after_return >= work_end:
            # Retorno terminou após 18h, pausar até 8h do dia seguinte
            current_day = int(current_time // 1440)
            current_time = (current_day + 1) * 1440 + work_start
    
    total_time = current_time - start_time
    return total_distance, total_time, arrival_times


def calculate_constrained_fitness(route: List[ServicePoint],
                                  start_time: float = 480.0,
                                  speed: float = 60.0,
                                  priority_deadline: float = 1440.0) -> float:
    """
    Calcula fitness balanceando distância e prioridades:
    - Ordem de prioridades: EME → VIO → MED → POS → REG
    - Permite até 1 parada entre pontos da mesma prioridade para otimizar distância
    - Penaliza violações de ordem, mas prioriza minimização de distância
    """
    if not route:
        return float('inf')
    
    # Calcular distância e tempos
    total_distance, total_time, arrival_times = calculate_route_time_and_distance(
        route, start_time, speed
    )
    
    # Fitness base: Distância (peso principal)
    fitness = total_distance * 10  # Multiplicar para dar peso à distância
    
    # Encontrar posições de cada prioridade
    priority_positions = {
        ServicePriority.EMERGENCY_OBSTETRIC: [],
        ServicePriority.DOMESTIC_VIOLENCE: [],
        ServicePriority.HORMONAL_MEDICATION: [],
        ServicePriority.POSTPARTUM_CARE: [],
        ServicePriority.REGULAR: []
    }
    
    for i, point in enumerate(route):
        priority_positions[point.priority].append(i)
    
    # Verificar ordem: EME < VIO < MED < POS < REG
    priority_order = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE,
        ServicePriority.REGULAR
    ]
    
    # Penalidade moderada por violação de ordem (permite otimização)
    priority_order_penalty = 0.0
    for i in range(len(priority_order) - 1):
        current_priority = priority_order[i]
        next_priority = priority_order[i + 1]
        
        current_positions = priority_positions[current_priority]
        next_positions = priority_positions[next_priority]
        
        if current_positions and next_positions:
            max_current = max(current_positions)
            min_next = min(next_positions)
            
            # Se ordem for violada: penalidade proporcional à violação
            if min_next < max_current:
                violation_size = max_current - min_next
                priority_order_penalty += violation_size * 5000  # Penalidade moderada
    
    # Penalidade leve por gaps (permite 1 parada)
    gap_penalty = 0.0
    for priority, positions in priority_positions.items():
        if len(positions) > 1:
            for i in range(len(positions) - 1):
                gap = positions[i + 1] - positions[i] - 1
                if gap > 1:  # Mais de 1 parada
                    gap_penalty += (gap - 1) * 1000
    
    # Penalidades por violação de janelas de tempo
    time_window_penalty = 0.0
    for point, arrival_time in zip(route, arrival_times):
        if point.time_window:
            penalty = point.time_window.get_penalty(arrival_time)
            time_window_penalty += penalty
    
    # Restrição: Medicamentos prioritários devem ser entregues antes do deadline
    priority_deadline_penalty = 0.0
    priority_types = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE
    ]
    
    for point, arrival_time in zip(route, arrival_times):
        if point.priority in priority_types:
            # Verificar se passou do deadline
            if arrival_time > priority_deadline:
                # Penalidade forte se medicamento prioritário passar do deadline: 10.000 por minuto de atraso
                delay = arrival_time - priority_deadline
                priority_deadline_penalty += delay * 10000
    
    # Validação de controle de temperatura: penalidade alta se rota não atender requisitos - 50000
    temp_valid, temp_message = validate_temperature_control_route(route)
    temperature_penalty = 0.0 if temp_valid else 50000
    
    # Validação de protocolos especiais: penalidade alta se sequência de protocolos for violada - 20000
    protocol_valid, protocol_message = validate_special_protocol_sequence(route)
    protocol_penalty = 0.0 if protocol_valid else 20000
    
    # Penalidade por tempo total excessivo
    max_work_time = 480.0  # 8 horas
    overtime_penalty = max(0, total_time - max_work_time) * 100
    
    # Fitness total: distância é o fator principal
    total_fitness = (
        fitness +                    # Distância x10 (peso principal)
        priority_order_penalty +     # Penalidade moderada por ordem
        gap_penalty +                # Penalidade leve por gaps
        time_window_penalty +        # Penalidade por janelas de tempo
        temperature_penalty +
        protocol_penalty +
        overtime_penalty +
        priority_deadline_penalty    # Penalidade por deadline de prioritários
    )
    
    return total_fitness


def generate_priority_aware_population(service_points: List[ServicePoint],
                                       population_size: int,
                                       priority_bias: float = 0.9) -> List[List[ServicePoint]]:
    """
    Gera população inicial com viés para ordem de prioridade
    Sempre coloca o depósito (ID=0) como primeiro ponto """
    population = []
    
    # Separar depósito dos outros pontos
    depot = None
    other_points = []
    for point in service_points:
        if point.id == 0:
            depot = point
        else:
            other_points.append(point)
    
    for _ in range(population_size):
        if random.random() < priority_bias:
            # Criar rota baseada em prioridade com alguma aleatoriedade
            sorted_points = sort_by_priority(other_points)
            
            # Embaralhar dentro de grupos de mesma prioridade
            route = []
            current_priority = None
            priority_group = []
            
            for point in sorted_points:
                if point.priority != current_priority:
                    if priority_group:
                        random.shuffle(priority_group)
                        route.extend(priority_group)
                    priority_group = [point]
                    current_priority = point.priority
                else:
                    priority_group.append(point)
            
            if priority_group:
                random.shuffle(priority_group)
                route.extend(priority_group)
            
            # Adicionar depósito no início
            if depot:
                route.insert(0, depot)
            
            population.append(route)
        else:
            # Rota completamente aleatória (mas depósito sempre primeiro)
            route = random.sample(other_points, len(other_points))
            if depot:
                route.insert(0, depot)
            population.append(route)
    
    return population


def constrained_order_crossover(parent1: List[ServicePoint],
                                parent2: List[ServicePoint],
                                preserve_priority_blocks: bool = True) -> List[ServicePoint]:
    """ Crossover que preserva ordem de prioridades
    Sempre mantém o depósito (ID=0) na primeira posição """
    length = len(parent1)
    
    # Separar depósito dos outros pontos
    depot = None
    parent1_no_depot = []
    parent2_no_depot = []
    
    for point in parent1:
        if point.id == 0:
            depot = point
        else:
            parent1_no_depot.append(point)
    
    for point in parent2:
        if point.id != 0:
            parent2_no_depot.append(point)
    
    # 80% das vezes preservar ordem de prioridades
    if preserve_priority_blocks and random.random() < 0.8:
        # Separar por grupos de prioridade
        priority_groups = {}
        for point in parent1_no_depot:
            if point.priority not in priority_groups:
                priority_groups[point.priority] = []
            priority_groups[point.priority].append(point)
        
        # Ordem de prioridades
        priority_order = [
            ServicePriority.EMERGENCY_OBSTETRIC,
            ServicePriority.DOMESTIC_VIOLENCE,
            ServicePriority.HORMONAL_MEDICATION,
            ServicePriority.POSTPARTUM_CARE,
            ServicePriority.REGULAR
        ]
        
        # Construir filho mantendo ordem de prioridades
        child = []
        for priority in priority_order:
            if priority in priority_groups:
                # Embaralhar dentro do grupo para variedade
                group = priority_groups[priority].copy()
                random.shuffle(group)
                child.extend(group)
        
        # Adicionar depósito no início
        if depot:
            child.insert(0, depot)
        
        return child
    
    # 20% das vezes: Crossover padrão (para diversidade)
    if len(parent1_no_depot) < 2:
        child = parent1_no_depot.copy()
    else:
        start_index = random.randint(0, len(parent1_no_depot) - 1)
        end_index = random.randint(start_index + 1, len(parent1_no_depot))
        
        child = parent1_no_depot[start_index:end_index]
        remaining_positions = [i for i in range(len(parent1_no_depot)) if i < start_index or i >= end_index]
        remaining_genes = [gene for gene in parent2_no_depot if gene not in child]
        
        for position, gene in zip(remaining_positions, remaining_genes):
            child.insert(position, gene)
    
    # Adicionar depósito no início
    if depot:
        child.insert(0, depot)
    
    return child


def constrained_mutate(route: List[ServicePoint],
                       mutation_probability: float,
                       respect_priorities: bool = True) -> List[ServicePoint]:
    """ Mutação que respeita ordem de prioridades
    Sempre mantém o depósito (ID=0) na primeira posição """
    if random.random() >= mutation_probability:
        return route
    
    mutated_route = copy.deepcopy(route)
    
    if len(route) < 2:
        return mutated_route
    
    # Identificar se há depósito e sua posição
    depot_idx = None
    for i, point in enumerate(route):
        if point.id == 0:
            depot_idx = i
            break
    
    # 90% das vezes: trocar apenas dentro do mesmo grupo de prioridade
    if respect_priorities and random.random() < 0.9:
        # Agrupar índices por prioridade (excluindo depósito)
        priority_indices = {}
        for i, point in enumerate(route):
            if point.id != 0:  # Não incluir depósito
                if point.priority not in priority_indices:
                    priority_indices[point.priority] = []
                priority_indices[point.priority].append(i)
        
        # Escolher um grupo que tenha pelo menos 2 elementos
        valid_groups = [indices for indices in priority_indices.values() if len(indices) >= 2]
        
        if valid_groups:
            # Escolher um grupo aleatório
            group = random.choice(valid_groups)
            
            # Trocar dois elementos dentro desse grupo
            idx1, idx2 = random.sample(group, 2)
            mutated_route[idx1], mutated_route[idx2] = mutated_route[idx2], mutated_route[idx1]
        
        return mutated_route
    
    # 10% das vezes: mutação livre (para diversidade, exceto depósito)
    mutation_type = random.choice(['swap', 'inversion'])
    
    # Criar lista de índices válidos (sem o depósito)
    valid_indices = [i for i in range(len(route)) if route[i].id != 0]
    
    if len(valid_indices) >= 2:
        if mutation_type == 'swap':
            idx1, idx2 = random.sample(valid_indices, 2)
            mutated_route[idx1], mutated_route[idx2] = mutated_route[idx2], mutated_route[idx1]
        else:  # inversion
            idx1 = random.choice(valid_indices[:-1])
            idx2 = random.choice([i for i in valid_indices if i > idx1])
            mutated_route[idx1:idx2+1] = list(reversed(mutated_route[idx1:idx2+1]))
    
    return mutated_route


def sort_population_by_fitness(population: List[List[ServicePoint]],
                               fitness_values: List[float]) -> Tuple[List[List[ServicePoint]], List[float]]:
    """ Ordena população por fitness (menor = melhor) """
    combined = list(zip(population, fitness_values))
    sorted_combined = sorted(combined, key=lambda x: x[1])
    sorted_population, sorted_fitness = zip(*sorted_combined)
    return list(sorted_population), list(sorted_fitness)

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

        # Adicionar tempo de serviço (depósito não tem tempo de atendimento)
        if route[i].id != 0:
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
    
    # Fitness base: distância sem multiplicador — penalidades expressas em "unidades de distância equivalente"
    fitness = total_distance

    # A ordem de prioridades DEVE ser respeitada (EME → VIO → MED → POS → REG)
    # Exceção: pode atender ponto de menor prioridade se estiver no caminho E não atrapalhar time_window
    priority_order = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE,
        ServicePriority.REGULAR
    ]
    priority_positions: dict = {p: [] for p in priority_order}
    for i, point in enumerate(route):
        if point.priority in priority_positions:
            priority_positions[point.priority].append(i)

    priority_order_penalty = 0.0
    for i in range(len(priority_order) - 1):
        cur_p = priority_order[i]
        nxt_p = priority_order[i + 1]
        cur_pos = priority_positions[cur_p]
        nxt_pos = priority_positions[nxt_p]
        if cur_pos and nxt_pos:
            if min(nxt_pos) < max(cur_pos):
                # Penalidade 500 por violação - equilibrada com outras penalidades
                priority_order_penalty += (max(cur_pos) - min(nxt_pos)) * 500

    # Penalidade leve por gaps dentro do mesmo grupo (incentiva pontos de mesma prioridade juntos)
    gap_penalty = 0.0
    for positions in priority_positions.values():
        if len(positions) > 1:
            for k in range(len(positions) - 1):
                gap = positions[k + 1] - positions[k] - 1
                if gap > 1:
                    gap_penalty += (gap - 1) * 20

    # Penalidades por violação de janelas de tempo
    # Cada minuto de atraso ≈ 30 unidades de distância (proporcional à distância base)
    time_window_penalty = 0.0
    for point, arrival_time in zip(route, arrival_times):
        # Filtrar depósito
        if point.id == 0:
            continue
        if point.time_window and arrival_time > point.time_window.end_time:
            minutes_late = arrival_time - point.time_window.end_time
            time_window_penalty += minutes_late * 30
    
    # Restrição: Medicamentos prioritários devem ser entregues antes do deadline
    priority_deadline_penalty = 0.0
    priority_types = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE
    ]
    
    for point, arrival_time in zip(route, arrival_times):
        # Filtrar depósito
        if point.id == 0:
            continue
        if point.priority in priority_types:
            # Penalidade forte por passar do deadline: ≈ 150 unidades de distância por minuto
            # (mais grave que atraso de janela de tempo, menos que restrição hard)
            if arrival_time > priority_deadline:
                delay = arrival_time - priority_deadline
                priority_deadline_penalty += delay * 150
    
    # Restrições hard: penalidades equivalem a descartar a rota inteira (~10x distância típica)
    # Temperatura: medicamento estragado é inaceitável — equivale a ~10 rotas completas
    temp_valid, temp_message = validate_temperature_control_route(route)
    temperature_penalty = 0.0 if temp_valid else 5000

    # Protocolo de violência: não respeitar protocolo é inaceitável — equivale a ~4 rotas completas
    protocol_valid, protocol_message = validate_special_protocol_sequence(route)
    protocol_penalty = 0.0 if protocol_valid else 2000

    # Penalidade por tempo total excessivo (soft constraint)
    # Cada minuto extra ≈ 5 unidades de distância — incentiva caber no horário, mas não domina
    max_work_time = 480.0  # 8 horas
    overtime_penalty = max(0, total_time - max_work_time) * 5
    
    # Fitness total: todos os componentes em escala de "distância equivalente"
    # Quanto menor, melhor. Distância é o fator de desempate quando restrições são satisfeitas.
    total_fitness = (
        fitness +                    # Distância real (base de comparação)
        priority_order_penalty +     # 100/violação  — moderado, pode ser "comprado" por distância
        gap_penalty +                # 20/gap extra  — leve
        time_window_penalty +        # 30/min tarde  — proporcional
        temperature_penalty +        # 5000 fixo     — hard constraint (inaceitável)
        protocol_penalty +           # 2000 fixo     — hard constraint
        overtime_penalty +           # 5/min extra   — soft constraint
        priority_deadline_penalty    # 150/min tarde — forte mas proporcional
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
            route: List[ServicePoint] = []
            current_priority = None
            priority_group: List[ServicePoint] = []

            for point in sorted_points:
                if point.priority != current_priority:
                    if priority_group:
                        random.shuffle(priority_group)
                        route.extend(priority_group)
                    priority_group = [point]
                    current_priority = point.priority
                else:
                    priority_group.append(point)

            # Último grupo: para REG, ~20% das vezes usar nearest neighbor
            # em vez de shuffle para uma melhor semente inicial
            if priority_group:
                use_nn = (
                    current_priority == ServicePriority.REGULAR
                    and len(priority_group) >= 3
                    and random.random() < 0.20
                )
                if use_nn:
                    start_loc = route[-1].location if route else (
                        depot.location if depot else priority_group[0].location
                    )
                    nn_group: List[ServicePoint] = []
                    remaining = priority_group[:]
                    current_loc = start_loc
                    while remaining:
                        nearest = min(remaining,
                                      key=lambda p: calculate_distance(current_loc, p.location))
                        nn_group.append(nearest)
                        current_loc = nearest.location
                        remaining.remove(nearest)
                    route.extend(nn_group)
                else:
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
    """
    OX por grupo de prioridade: combina a ordenação espacial de p1 e p2
    dentro de cada bloco, garantindo que a ordem de prioridades seja preservada.
    Depot (ID=0) permanece na posição 0.
    """
    depot = None
    priority_order = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE,
        ServicePriority.REGULAR
    ]
    p1_groups: dict = {p: [] for p in priority_order}
    p2_groups: dict = {p: [] for p in priority_order}

    for pt in parent1:
        if pt.id == 0:
            depot = pt
        elif pt.priority in p1_groups:
            p1_groups[pt.priority].append(pt)
    for pt in parent2:
        if pt.id != 0 and pt.priority in p2_groups:
            p2_groups[pt.priority].append(pt)

    def _ox(seq1: List[ServicePoint], seq2: List[ServicePoint]) -> List[ServicePoint]:
        # Garantir que todos os pontos sejam preservados
        n = len(seq1)
        if n <= 1:
            return seq1[:]
        a = random.randint(0, n - 1)
        b = random.randint(a, n - 1)
        inherited = seq1[a:b + 1]
        inherited_ids = {pt.id for pt in inherited}
        # Usar seq1 como fallback para pontos não encontrados em seq2
        remainder = [pt for pt in seq2 if pt.id not in inherited_ids]
        missing = [pt for pt in seq1 if pt.id not in inherited_ids and pt.id not in {r.id for r in remainder}]
        remainder.extend(missing)
        return remainder[:a] + inherited + remainder[a:]

    child: List[ServicePoint] = []
    for p in priority_order:
        g1, g2 = p1_groups[p], p2_groups[p]
        if not g1:
            continue
        child.extend(_ox(g1, g2) if len(g1) > 1 else g1[:])

    if depot:
        child.insert(0, depot)
    return child


def validate_and_repair_route(route: List[ServicePoint]) -> List[ServicePoint]:
    """Garante que a rota é válida:
    1. Depósito (ID=0) na posição 0
    2. Ordem de prioridades respeitada (EME → VIO → MED → POS → REG)
    3. Sem duplicatas
    A ordem dentro de cada grupo de prioridade é preservada (não embaralhada),
    para que o GA possa otimizar a sequência intra-grupo.
    """
    if not route:
        return route

    seen_ids: set = set()
    depot = None
    priority_order = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE,
        ServicePriority.REGULAR
    ]
    groups: dict = {p: [] for p in priority_order}

    for point in route:
        if point.id in seen_ids:
            continue
        seen_ids.add(point.id)
        if point.id == 0:
            depot = point
        elif point.priority in groups:
            groups[point.priority].append(point)

    repaired: List[ServicePoint] = []
    if depot:
        repaired.append(depot)
    for p in priority_order:
        repaired.extend(groups[p])
    return repaired


def constrained_mutate(route: List[ServicePoint],
                       mutation_probability: float,
                       respect_priorities: bool = True) -> List[ServicePoint]:
    """
    Mutação que respeita grupos de prioridade na maioria dos casos.
    - 80%: swap dentro do mesmo grupo de prioridade (mantém estrutura)
    - 20%: swap/inversão livre (permite cruzar grupos quando vale a pena geometricamente)
    Depósito (ID=0) permanece sempre na posição 0.
    """
    if random.random() >= mutation_probability:
        return route

    mutated_route = copy.deepcopy(route)
    valid_indices = [i for i, p in enumerate(mutated_route) if p.id != 0]
    if len(valid_indices) < 2:
        return mutated_route

    if respect_priorities and random.random() < 0.8:
        # Swap dentro do mesmo grupo de prioridade
        priority_indices: dict = {}
        for i, p in enumerate(mutated_route):
            if p.id != 0:
                priority_indices.setdefault(p.priority, []).append(i)
        valid_groups = [idxs for idxs in priority_indices.values() if len(idxs) >= 2]
        if valid_groups:
            group = random.choice(valid_groups)
            i1, i2 = random.sample(group, 2)
            mutated_route[i1], mutated_route[i2] = mutated_route[i2], mutated_route[i1]
    else:
        # Operação livre (swap ou inversão de qualquer segmento)
        if random.random() < 0.6:
            i1, i2 = random.sample(valid_indices, 2)
            mutated_route[i1], mutated_route[i2] = mutated_route[i2], mutated_route[i1]
        else:
            i1 = random.choice(valid_indices[:-1])
            i2 = random.choice([i for i in valid_indices if i > i1])
            mutated_route[i1:i2 + 1] = list(reversed(mutated_route[i1:i2 + 1]))

    return mutated_route


def sort_population_by_fitness(population: List[List[ServicePoint]],
                               fitness_values: List[float]) -> Tuple[List[List[ServicePoint]], List[float]]:
    """ Ordena população por fitness (menor = melhor) """
    combined = list(zip(population, fitness_values))
    sorted_combined = sorted(combined, key=lambda x: x[1])
    sorted_population, sorted_fitness = zip(*sorted_combined)
    return list(sorted_population), list(sorted_fitness)


def perturb_route(route: List[ServicePoint]) -> List[ServicePoint]:
    """
    Double-bridge dentro de cada grupo de prioridade.
    Perturba a ordem intra-grupo sem violar a sequência EME→VIO→MED→POS→REG.
    """
    if len(route) < 5:
        return route[:]

    priority_order = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE,
        ServicePriority.REGULAR
    ]
    depot = route[0] if route[0].id == 0 else None
    groups: dict = {p: [] for p in priority_order}
    for pt in route:
        if pt.id != 0 and pt.priority in groups:
            groups[pt.priority].append(pt)

    def _perturb_group(pts: List[ServicePoint]) -> List[ServicePoint]:
        """
        Double-bridge adaptativo para perturbação intra-grupo.
        - Grupos pequenos (n<4): swap simples de 2 pontos
        - Grupos grandes (n≥4): double-bridge com 3 cortes aleatórios
        Reorganiza a ordem dos pontos sem sair do grupo de prioridade.
        """
        n = len(pts)
        if n < 4:
            if n >= 2:
                res = pts[:]
                i1, i2 = random.sample(range(n), 2)
                res[i1], res[i2] = res[i2], res[i1]
                return res
            return pts[:]
        cuts = sorted(random.sample(range(1, n), 3))
        a, b, c = cuts
        return pts[:a] + pts[b:c] + pts[a:b] + pts[c:]

    result: List[ServicePoint] = []
    if depot:
        result.append(depot)
    for p in priority_order:
        g = groups[p]
        result.extend(_perturb_group(g) if len(g) >= 2 else g)

    return result


def two_opt_within_priority_groups(route: List[ServicePoint]) -> List[ServicePoint]:
    """
    Otimização 2-opt que respeita grupos de prioridade.
    Aplica busca local dentro de cada grupo de prioridade separadamente, usando o contexto correto de entrada/saída de cada grupo.
    Sempre mantém o depósito (ID=0) na primeira posição.
    Aplicado na melhor solução a cada N gerações, não em todos os indivíduos (custo O(n²) por grupo).
    """
    if len(route) <= 3:
        return route[:]

    # Separar depósito
    depot = route[0] if route[0].id == 0 else None
    working_points = [p for p in route if p.id != 0]

    if len(working_points) <= 2:
        return route[:]

    priority_order = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE,
        ServicePriority.REGULAR
    ]

    # Agrupar pontos por prioridade, mantendo apenas grupos não-vazios
    priority_groups: dict = {p: [] for p in priority_order}
    for point in working_points:
        if point.priority in priority_groups:
            priority_groups[point.priority].append(point)

    active_priorities = [p for p in priority_order if priority_groups[p]]

    def _optimize_group(pts: List[ServicePoint],
                        prev_loc: Tuple[float, float],
                        next_loc: Optional[Tuple[float, float]]) -> List[ServicePoint]:
        """ 2-opt num grupo com contexto de entrada/saída """
        if len(pts) <= 2:
            return pts[:]

        def group_dist(p_list: List[ServicePoint]) -> float:
            total = calculate_distance(prev_loc, p_list[0].location)
            for k in range(len(p_list) - 1):
                total += calculate_distance(p_list[k].location, p_list[k + 1].location)
            if next_loc:
                total += calculate_distance(p_list[-1].location, next_loc)
            return total

        best = pts[:]
        best_dist = group_dist(best)
        improved = True
        max_iter = 50
        itr = 0

        while improved and itr < max_iter:
            improved = False
            itr += 1
            for i in range(len(best) - 1):
                for j in range(i + 2, len(best) + 1):
                    candidate = best[:i] + list(reversed(best[i:j])) + best[j:]
                    d = group_dist(candidate)
                    if d < best_dist - 1e-9:
                        best = candidate
                        best_dist = d
                        improved = True
                        break
                if improved:
                    break

        return best

    depot_loc = depot.location if depot else working_points[0].location
    final_points: List[ServicePoint] = []
    current_last_loc = depot_loc

    for idx, priority in enumerate(active_priorities):
        group = priority_groups[priority]

        # Próximo ponto de referência: início do próximo grupo ou retorno ao depósito
        if idx < len(active_priorities) - 1:
            next_p = active_priorities[idx + 1]
            next_loc = priority_groups[next_p][0].location
        else:
            next_loc = depot_loc

        optimized_group = _optimize_group(group, current_last_loc, next_loc)
        final_points.extend(optimized_group)
        current_last_loc = optimized_group[-1].location

    result = []
    if depot:
        result.append(depot)
    result.extend(final_points)
    return result


def two_opt_global(route: List[ServicePoint]) -> List[ServicePoint]:
    """2-opt padrão sobre a rota completa. Após otimizar, aplica
    validate_and_repair_route para garantir a ordem de prioridades.
    Depot (ID=0) permanece fixo na posição 0.
    """
    if len(route) <= 3:
        return route[:]

    depot = route[0] if route[0].id == 0 else None
    pts = [p for p in route if p.id != 0]
    n = len(pts)
    if n <= 2:
        return route[:]

    depot_loc = depot.location if depot else pts[0].location

    def total_dist(seq: List[ServicePoint]) -> float:
        d = calculate_distance(depot_loc, seq[0].location)
        for k in range(len(seq) - 1):
            d += calculate_distance(seq[k].location, seq[k + 1].location)
        d += calculate_distance(seq[-1].location, depot_loc)
        return d

    best = pts[:]
    best_d = total_dist(best)
    improved = True

    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                candidate = best[:i] + list(reversed(best[i:j + 1])) + best[j + 1:]
                d = total_dist(candidate)
                if d < best_d - 1e-9:
                    best = candidate
                    best_d = d
                    improved = True
                    break
            if improved:
                break

    result = ([depot] if depot else []) + best
    return validate_and_repair_route(result)

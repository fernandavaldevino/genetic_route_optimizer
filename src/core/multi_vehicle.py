"""
Sistema de Otimização de Rotas com Múltiplos Veículos
Gerencia 2 veículos para atender todos os pontos em 1 dia
- Pontos prioritários (EME, VIO, MED, POS) devem ser atendidos até 12h
- Pontos regulares (REG) podem ser atendidos após 12h
- Veículos partem e retornam ao mesmo depósito
"""

from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import copy
import random
from .service_points import ServicePoint, ServicePriority, calculate_distance, calculate_travel_time

# Ponto de partida/depósito (será definido dinamicamente)
DEPOT_LOCATION: Optional[Tuple[float, float]] = None


@dataclass
class VehicleRoute:
    """Representa a rota de um veículo"""
    vehicle_id: int
    route: List[ServicePoint]
    total_distance: float = 0.0
    total_time: float = 0.0
    arrival_times: List[float] = None
    
    def __post_init__(self):
        if self.arrival_times is None:
            self.arrival_times = []


@dataclass
class MultiVehicleSolution:
    """Representa uma solução completa com múltiplos veículos"""
    vehicles: List[VehicleRoute]
    total_fitness: float = float('inf')
    
    def get_all_points(self) -> List[ServicePoint]:
        """Retorna todos os pontos de todas as rotas"""
        all_points = []
        for vehicle in self.vehicles:
            all_points.extend(vehicle.route)
        return all_points
    
    def get_point_ids(self) -> set:
        """Retorna conjunto de IDs de todos os pontos"""
        return {point.id for vehicle in self.vehicles for point in vehicle.route}


def calculate_vehicle_route_time_and_distance(
    route: List[ServicePoint],
    depot_location: Tuple[float, float],
    start_time: float = 450.0,  # 7:30h (7*60 + 30 = 450 min)
    speed: float = 40.0,
    work_start: float = 450.0,  # 7:30h
    work_end: float = 1080.0    # 18h
) -> Tuple[float, float, List[float]]:
    """
    Calcula tempo total e distância de uma rota de veículo
    Inclui viagem do depósito ao primeiro ponto e do último ponto ao depósito
    
    Args:
        route: Lista de pontos de atendimento na ordem
        depot_location: Localização do depósito (ponto de partida/retorno)
        start_time: Tempo de início em minutos (default: 7:30h = 450 min)
        speed: Velocidade média em km/h
        work_start: Início do horário comercial em minutos (default: 7:30h = 450 min)
        work_end: Fim do horário comercial em minutos (default: 18h = 1080 min)
    
    Returns:
        Tupla (distância_total, tempo_total, lista_de_tempos_de_chegada)
    """
    if not route:
        return 0.0, 0.0, []
    
    total_distance = 0.0
    current_time = start_time
    arrival_times = []
    
    # Viagem do depósito ao primeiro ponto
    distance_to_first = calculate_distance(depot_location, route[0].location)
    total_distance += distance_to_first
    travel_time_to_first = calculate_travel_time(depot_location, route[0].location, speed)
    current_time += travel_time_to_first
    
    for i in range(len(route)):
        # Verificar se está dentro do horário comercial
        time_of_day = current_time % 1440
        
        # Se passou das 18h, parar (não continuar no dia seguinte)
        if time_of_day >= work_end:
            # Marcar tempo como inválido (penalidade será aplicada)
            arrival_times.append(current_time)
            current_time += route[i].service_duration
            if i < len(route) - 1:
                distance = calculate_distance(route[i].location, route[i + 1].location)
                total_distance += distance
                travel_time = calculate_travel_time(route[i].location, route[i + 1].location, speed)
                current_time += travel_time
            continue
        
        arrival_times.append(current_time)
        
        # Adicionar tempo de serviço
        current_time += route[i].service_duration
        
        # Calcular distância e tempo até o próximo ponto
        if i < len(route) - 1:
            distance = calculate_distance(route[i].location, route[i + 1].location)
            total_distance += distance
            travel_time = calculate_travel_time(route[i].location, route[i + 1].location, speed)
            current_time += travel_time
    
    # Viagem do último ponto de volta ao depósito
    distance_to_depot = calculate_distance(route[-1].location, depot_location)
    total_distance += distance_to_depot
    travel_time_to_depot = calculate_travel_time(route[-1].location, depot_location, speed)
    current_time += travel_time_to_depot
    
    total_time = current_time - start_time
    return total_distance, total_time, arrival_times


def split_points_by_priority(service_points: List[ServicePoint]) -> Tuple[List[ServicePoint], List[ServicePoint]]:
    """
    Divide pontos em prioritários e regulares
    
    Returns:
        Tupla (pontos_prioritários, pontos_regulares)
    """
    priority_types = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE
    ]
    
    priority_points = [p for p in service_points if p.priority in priority_types]
    regular_points = [p for p in service_points if p.priority == ServicePriority.REGULAR]
    
    return priority_points, regular_points


def divide_priority_points_geographically(
    priority_points: List[ServicePoint],
    num_vehicles: int = 2
) -> List[List[ServicePoint]]:
    """
    Divide pontos prioritários geograficamente entre veículos usando K-means
    Cria territórios distintos para minimizar cruzamentos
    
    Args:
        priority_points: Lista de pontos prioritários
        num_vehicles: Número de veículos (default: 2)
    
    Returns:
        Lista de listas, uma para cada veículo
    """
    if not priority_points:
        return [[] for _ in range(num_vehicles)]
    
    if len(priority_points) <= num_vehicles:
        result = [[] for _ in range(num_vehicles)]
        for i, point in enumerate(priority_points):
            result[i % num_vehicles].append(point)
        return result
    
    # K-means simples para criar clusters geográficos
    # Inicializar centros nos extremos (esquerda-baixo e direita-cima)
    min_x = min(p.location[0] for p in priority_points)
    max_x = max(p.location[0] for p in priority_points)
    min_y = min(p.location[1] for p in priority_points)
    max_y = max(p.location[1] for p in priority_points)
    
    # Centros iniciais em cantos opostos (maximiza separação)
    centers = [
        (min_x + (max_x - min_x) * 0.25, min_y + (max_y - min_y) * 0.25),  # Canto inferior esquerdo
        (min_x + (max_x - min_x) * 0.75, min_y + (max_y - min_y) * 0.75)   # Canto superior direito
    ]
    
    # Executar K-means (3 iterações)
    for _ in range(3):
        # Atribuir pontos ao centro mais próximo
        clusters = [[] for _ in range(num_vehicles)]
        for point in priority_points:
            distances = []
            for center in centers:
                dx = point.location[0] - center[0]
                dy = point.location[1] - center[1]
                dist = (dx**2 + dy**2) ** 0.5
                distances.append(dist)
            
            closest = distances.index(min(distances))
            clusters[closest].append(point)
        
        # Recalcular centros
        for i in range(num_vehicles):
            if clusters[i]:
                avg_x = sum(p.location[0] for p in clusters[i]) / len(clusters[i])
                avg_y = sum(p.location[1] for p in clusters[i]) / len(clusters[i])
                centers[i] = (avg_x, avg_y)
    
    # Balancear clusters se muito desiguais
    if len(clusters[0]) > len(clusters[1]) + 2:
        # Mover pontos mais próximos do outro centro
        while len(clusters[0]) > len(clusters[1]) + 1:
            # Encontrar ponto de clusters[0] mais próximo de centers[1]
            closest_point = min(clusters[0], key=lambda p:
                ((p.location[0] - centers[1][0])**2 + (p.location[1] - centers[1][1])**2)**0.5)
            clusters[0].remove(closest_point)
            clusters[1].append(closest_point)
    elif len(clusters[1]) > len(clusters[0]) + 2:
        while len(clusters[1]) > len(clusters[0]) + 1:
            closest_point = min(clusters[1], key=lambda p:
                ((p.location[0] - centers[0][0])**2 + (p.location[1] - centers[0][1])**2)**0.5)
            clusters[1].remove(closest_point)
            clusters[0].append(closest_point)
    
    return clusters


def count_route_crossings(vehicles: List[VehicleRoute]) -> int:
    """
    Conta número de cruzamentos entre rotas de diferentes veículos
    Usa detecção de interseção de segmentos de linha
    
    Args:
        vehicles: Lista de veículos com rotas
    
    Returns:
        Número de cruzamentos detectados
    """
    if len(vehicles) < 2:
        return 0
    
    def segments_intersect(p1, p2, p3, p4):
        """Verifica se segmento p1-p2 cruza com p3-p4"""
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
    
    crossings = 0
    
    # Comparar rotas de cada par de veículos
    for i in range(len(vehicles)):
        for j in range(i + 1, len(vehicles)):
            route1 = vehicles[i].route
            route2 = vehicles[j].route
            
            # Criar segmentos da rota 1
            segments1 = []
            for k in range(len(route1) - 1):
                segments1.append((route1[k].location, route1[k + 1].location))
            
            # Criar segmentos da rota 2
            segments2 = []
            for k in range(len(route2) - 1):
                segments2.append((route2[k].location, route2[k + 1].location))
            
            # Verificar cruzamentos entre todos os pares de segmentos
            for seg1 in segments1:
                for seg2 in segments2:
                    if segments_intersect(seg1[0], seg1[1], seg2[0], seg2[1]):
                        crossings += 1
    
    return crossings


def validate_solution(solution: MultiVehicleSolution, expected_points: int = 20) -> Tuple[bool, str]:
    """
    Valida se solução tem exatamente os pontos esperados sem duplicação
    
    Args:
        solution: Solução a validar
        expected_points: Número esperado de pontos únicos (default: 20)
    
    Returns:
        Tupla (é_válida, mensagem_erro)
    """
    point_ids = solution.get_point_ids()
    total_points = len(point_ids)
    
    # Contar pontos totais (incluindo duplicados)
    all_points = solution.get_all_points()
    total_with_duplicates = len(all_points)
    
    if total_points != expected_points:
        return False, f"Esperado {expected_points} pontos únicos, encontrado {total_points}"
    
    if total_with_duplicates != expected_points:
        duplicates = total_with_duplicates - total_points
        return False, f"Encontradas {duplicates} duplicações de pontos"
    
    return True, "Solução válida"


def calculate_multi_vehicle_fitness(
    solution: MultiVehicleSolution,
    depot_location: Tuple[float, float],
    start_time: float = 450.0,  # 7:30h (7*60 + 30 = 450 min)
    priority_deadline: float = 720.0,  # 12h (meio-dia)
    speed: float = 40.0
) -> float:
    """
    Calcula fitness para solução com múltiplos veículos
    
    Restrições:
    - TODOS os 20 pontos devem estar presentes SEM duplicação
    - Pontos prioritários DEVEM ser atendidos até 12h (720 min)
    - Todos os pontos devem ser atendidos em 1 dia (até 18h = 1080 min)
    - Minimizar distância total
    - Balancear carga entre veículos
    - Veículos partem e retornam ao depósito
    
    Args:
        solution: Solução com múltiplos veículos
        depot_location: Localização do depósito
        start_time: Horário de início (7:30h = 450 min)
        priority_deadline: Deadline para pontos prioritários (12h = 720 min)
        speed: Velocidade média em km/h
    
    Returns:
        Fitness (menor = melhor)
    """
    # VALIDAÇÃO CRÍTICA: Verificar unicidade de pontos
    is_valid, error_msg = validate_solution(solution, expected_points=20)
    if not is_valid:
        # PENALIDADE MASSIVA para soluções inválidas
        return float('inf')
    
    fitness = 0.0
    total_distance = 0.0
    vehicle_times = []
    
    priority_types = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE
    ]
    
    for vehicle in solution.vehicles:
        if not vehicle.route:
            continue
        
        # Calcular distância e tempos (incluindo depósito)
        distance, total_time, arrival_times = calculate_vehicle_route_time_and_distance(
            vehicle.route, depot_location, start_time, speed
        )
        
        total_distance += distance
        vehicle_times.append(total_time)
        
        # Atualizar dados do veículo
        vehicle.total_distance = distance
        vehicle.total_time = total_time
        vehicle.arrival_times = arrival_times
        
        # Verificar restrições de tempo para pontos prioritários
        for point, arrival_time in zip(vehicle.route, arrival_times):
            if point.priority in priority_types:
                # Pontos prioritários DEVEM ser atendidos até 12h
                if arrival_time > priority_deadline:
                    # Penalidade MASSIVA por violar deadline de prioridade
                    overtime = arrival_time - priority_deadline
                    fitness += overtime * 10000  # Aumentado de 1000 para 10000
            
            # Verificar se passou das 18h (fim do dia)
            time_of_day = arrival_time % 1440
            if time_of_day >= 1080:  # 18h
                # Penalidade MASSIVA por passar das 18h
                overtime_18h = time_of_day - 1080
                fitness += 500000 + (overtime_18h * 10000)  # Aumentado de 100k para 500k base
        
        # Penalidade por violação de janelas de tempo
        for point, arrival_time in zip(vehicle.route, arrival_times):
            if point.time_window:
                penalty = point.time_window.get_penalty(arrival_time)
                fitness += penalty
    
    # Fitness base: distância total (peso baixo para priorizar restrições)
    fitness += total_distance * 1  # Reduzido de 2 para 1
    
    # Penalidade FORTE por desbalanceamento entre veículos
    if len(vehicle_times) > 1:
        max_time = max(vehicle_times)
        min_time = min(vehicle_times)
        imbalance = max_time - min_time
        # Penalidade forte para balanceamento (evitar um veículo sobrecarregado)
        fitness += imbalance * 500  # Aumentado de 100 para 500
    
    # Penalidade FORTE por desbalanceamento de número de pontos
    if len(solution.vehicles) >= 2:
        point_counts = [len(v.route) for v in solution.vehicles]
        max_points = max(point_counts)
        min_points = min(point_counts)
        point_imbalance = max_points - min_points
        # Penalidade forte por diferença de pontos (deve ser equilibrado)
        fitness += point_imbalance * 5000  # Aumentado de 1000 para 5000
    
    # Penalidade moderada por cruzamento de rotas
    if len(solution.vehicles) >= 2:
        crossings = count_route_crossings(solution.vehicles)
        # Penalidade moderada por cruzamento
        fitness += crossings * 2000  # Reduzido de 5000 para 2000
    
    solution.total_fitness = fitness
    return fitness


def create_initial_multi_vehicle_solution(
    service_points: List[ServicePoint],
    depot_location: Tuple[float, float],
    num_vehicles: int = 2,
    apply_2opt: bool = False
) -> MultiVehicleSolution:
    """
    Cria solução inicial dividindo pontos entre veículos
    
    Estratégia:
    1. Dividir pontos prioritários geograficamente entre veículos
    2. Cada veículo atende seus pontos prioritários primeiro
    3. Distribuir pontos regulares entre veículos após prioridades
    4. Veículos partem e retornam ao depósito
    
    Args:
        service_points: Lista de todos os pontos
        depot_location: Localização do depósito
        num_vehicles: Número de veículos (default: 2)
        apply_2opt: Se True, aplica otimização 2-opt (default: False)
    
    Returns:
        Solução inicial com múltiplos veículos
    """
    # Separar pontos por prioridade
    priority_points, regular_points = split_points_by_priority(service_points)
    
    # Dividir pontos prioritários geograficamente
    priority_groups = divide_priority_points_geographically(priority_points, num_vehicles)
    
    # Ordenar pontos prioritários de cada grupo por prioridade
    for group in priority_groups:
        group.sort(key=lambda p: p.priority.value)
    
    # Distribuir pontos regulares alternadamente
    random.shuffle(regular_points)
    regular_groups = [[] for _ in range(num_vehicles)]
    for i, point in enumerate(regular_points):
        regular_groups[i % num_vehicles].append(point)
    
    # Criar rotas dos veículos (prioridades primeiro, depois regulares)
    vehicles = []
    for i in range(num_vehicles):
        route = priority_groups[i] + regular_groups[i]
        # Aplicar otimização 2-opt APENAS se solicitado
        if apply_2opt:
            route = two_opt_optimize(route, depot_location)
        vehicle = VehicleRoute(vehicle_id=i + 1, route=route)
        vehicles.append(vehicle)
    
    solution = MultiVehicleSolution(vehicles=vehicles)
    calculate_multi_vehicle_fitness(solution, depot_location)
    
    return solution


def generate_multi_vehicle_population(
    service_points: List[ServicePoint],
    depot_location: Tuple[float, float],
    population_size: int,
    num_vehicles: int = 2
) -> List[MultiVehicleSolution]:
    """
    Gera população inicial de soluções com múltiplos veículos
    COM DIVERSIDADE: Apenas 20% das soluções são otimizadas com 2-opt
    
    Args:
        service_points: Lista de todos os pontos
        depot_location: Localização do depósito
        population_size: Tamanho da população
        num_vehicles: Número de veículos
    
    Returns:
        Lista de soluções
    """
    population = []
    
    # Debug: imprimir informação sobre geração da população
    print(f"Gerando população: 0% com 2-opt (máxima diversidade inicial)")
    
    for i in range(population_size):
        # MUDANÇA RADICAL: NUNCA aplicar 2-opt na população inicial
        # Isso garante máxima diversidade e espaço para evolução
        apply_2opt = False
        
        solution = create_initial_multi_vehicle_solution(service_points, depot_location, num_vehicles, apply_2opt=apply_2opt)
        
        # Adicionar MÁXIMA variação: embaralhar TUDO (exceto ordem de prioridades)
        for vehicle in solution.vehicles:
            priority_points, regular_points = split_points_by_priority(vehicle.route)
            
            # Embaralhar pontos de mesma prioridade
            priority_dict = {}
            for point in priority_points:
                if point.priority not in priority_dict:
                    priority_dict[point.priority] = []
                priority_dict[point.priority].append(point)
            
            # Reconstruir rota com ordem de prioridade mas TOTALMENTE embaralhado dentro
            new_route = []
            for priority in sorted(priority_dict.keys(), key=lambda p: p.value):
                group = priority_dict[priority]
                random.shuffle(group)
                new_route.extend(group)
            
            # Adicionar pontos regulares TOTALMENTE embaralhados
            random.shuffle(regular_points)
            new_route.extend(regular_points)
            
            vehicle.route = new_route
        
        # Recalcular fitness
        calculate_multi_vehicle_fitness(solution, depot_location)
        population.append(solution)
    
    return population


def multi_vehicle_crossover(
    parent1: MultiVehicleSolution,
    parent2: MultiVehicleSolution,
    depot_location: Tuple[float, float]
) -> MultiVehicleSolution:
    """
    Crossover entre duas soluções multi-veículo
    GARANTIA: Todos os 20 pontos são preservados sem duplicação
    """
    num_vehicles = len(parent1.vehicles)
    
    # Coletar TODOS os pontos de ambos os pais
    all_points_p1 = parent1.get_all_points()
    all_points_p2 = parent2.get_all_points()
    
    # Criar dicionário de pontos por ID (para acesso rápido)
    points_dict = {p.id: p for p in all_points_p1}
    
    # Rastrear IDs já alocados GLOBALMENTE
    global_used_ids = set()
    child_vehicles = []
    
    for i in range(num_vehicles):
        route1 = parent1.vehicles[i].route
        route2 = parent2.vehicles[i].route
        
        # Separar por prioridade
        priority1, regular1 = split_points_by_priority(route1)
        priority2, regular2 = split_points_by_priority(route2)
        
        # Combinar prioridades (escolher de um dos pais)
        child_priority = []
        source_priority = priority1 if random.random() < 0.5 else priority2
        
        for point in source_priority:
            if point.id not in global_used_ids:
                child_priority.append(point)
                global_used_ids.add(point.id)
        
        # Combinar regulares (misturar de ambos pais)
        child_regular = []
        for point in regular1 + regular2:
            if point.id not in global_used_ids:
                child_regular.append(point)
                global_used_ids.add(point.id)
        
        # Criar rota do veículo filho
        child_route = child_priority + child_regular
        child_vehicle = VehicleRoute(vehicle_id=i + 1, route=child_route)
        child_vehicles.append(child_vehicle)
    
    # CRÍTICO: Garantir que TODOS os 20 pontos estão presentes
    # Se faltam pontos, adicionar ao veículo com menos pontos
    expected_ids = set(range(1, 21))  # IDs de 1 a 20
    missing_ids = expected_ids - global_used_ids
    
    if missing_ids:
        # Adicionar pontos faltantes ao veículo com menos pontos
        vehicle_with_least = min(child_vehicles, key=lambda v: len(v.route))
        
        for missing_id in missing_ids:
            if missing_id in points_dict:
                missing_point = points_dict[missing_id]
                
                # Inserir ponto faltante na posição apropriada
                priority_types = [
                    ServicePriority.EMERGENCY_OBSTETRIC,
                    ServicePriority.DOMESTIC_VIOLENCE,
                    ServicePriority.HORMONAL_MEDICATION,
                    ServicePriority.POSTPARTUM_CARE
                ]
                
                if missing_point.priority in priority_types:
                    # Inserir no início (com outras prioridades)
                    priority_pts, regular_pts = split_points_by_priority(vehicle_with_least.route)
                    priority_pts.append(missing_point)
                    priority_pts.sort(key=lambda p: p.priority.value)
                    vehicle_with_least.route = priority_pts + regular_pts
                else:
                    # Adicionar no final (com regulares)
                    vehicle_with_least.route.append(missing_point)
    
    # Otimizar rotas com 2-opt 80% das vezes (aumentado para compensar população inicial sem 2-opt)
    if random.random() < 0.8:
        for vehicle in child_vehicles:
            vehicle.route = two_opt_optimize(vehicle.route, depot_location)
    
    child = MultiVehicleSolution(vehicles=child_vehicles)
    calculate_multi_vehicle_fitness(child, depot_location)
    return child


def multi_vehicle_mutate(
    solution: MultiVehicleSolution,
    depot_location: Tuple[float, float],
    mutation_probability: float
) -> MultiVehicleSolution:
    """
    Mutação de solução multi-veículo com BALANCEAMENTO INTELIGENTE
    - Transfere pontos prioritários atrasados para veículo com tempo disponível
    - Troca pontos dentro do mesmo veículo
    - Troca pontos entre veículos (SWAP seguro)
    """
    if random.random() >= mutation_probability:
        return solution
    
    mutated = copy.deepcopy(solution)
    
    # Calcular fitness atual para ter tempos de chegada
    calculate_multi_vehicle_fitness(mutated, depot_location)
    
    # 60% das vezes: MUTAÇÃO INTELIGENTE - transferir prioridades atrasadas
    if random.random() < 0.6 and len(mutated.vehicles) >= 2:
        priority_deadline = 720.0  # 12h
        priority_types = [
            ServicePriority.EMERGENCY_OBSTETRIC,
            ServicePriority.DOMESTIC_VIOLENCE,
            ServicePriority.HORMONAL_MEDICATION,
            ServicePriority.POSTPARTUM_CARE
        ]
        
        # Encontrar veículo com prioridades atrasadas
        vehicle_with_late = None
        late_priority_idx = None
        
        for vehicle in mutated.vehicles:
            for i, (point, arrival) in enumerate(zip(vehicle.route, vehicle.arrival_times)):
                if point.priority in priority_types and arrival > priority_deadline:
                    vehicle_with_late = vehicle
                    late_priority_idx = i
                    break
            if vehicle_with_late:
                break
        
        # Se encontrou prioridade atrasada, tentar transferir para veículo com tempo
        if vehicle_with_late and late_priority_idx is not None:
            late_point = vehicle_with_late.route[late_priority_idx]
            
            # Encontrar veículo com tempo disponível (terminou prioridades cedo)
            for other_vehicle in mutated.vehicles:
                if other_vehicle.vehicle_id == vehicle_with_late.vehicle_id:
                    continue
                
                # Verificar quando terminou as prioridades
                last_priority_time = 0
                for point, arrival in zip(other_vehicle.route, other_vehicle.arrival_times):
                    if point.priority in priority_types:
                        last_priority_time = arrival
                
                # Se terminou antes de 12h, tem tempo disponível
                if last_priority_time < priority_deadline - 60:  # Pelo menos 1h de folga
                    # Encontrar um ponto regular para trocar
                    _, regular_points = split_points_by_priority(other_vehicle.route)
                    
                    if regular_points:
                        # Trocar prioridade atrasada por regular
                        regular_point = random.choice(regular_points)
                        reg_idx = other_vehicle.route.index(regular_point)
                        
                        # SWAP: prioridade atrasada vai para veículo com tempo
                        vehicle_with_late.route[late_priority_idx] = regular_point
                        other_vehicle.route[reg_idx] = late_point
                        
                        # Reordenar prioridades no veículo que recebeu
                        priority_pts, regular_pts = split_points_by_priority(other_vehicle.route)
                        priority_pts.sort(key=lambda p: p.priority.value)
                        other_vehicle.route = priority_pts + regular_pts
                        
                        # Recalcular e retornar
                        calculate_multi_vehicle_fitness(mutated, depot_location)
                        return mutated
    
    # 40% das vezes: mutar dentro de um veículo
    elif random.random() < 0.67:  # 40% de 60% restantes
        vehicle = random.choice(mutated.vehicles)
        
        if len(vehicle.route) >= 2:
            priority_points, regular_points = split_points_by_priority(vehicle.route)
            
            # Trocar dentro de pontos regulares
            if len(regular_points) >= 2:
                idx1, idx2 = random.sample(range(len(regular_points)), 2)
                regular_points[idx1], regular_points[idx2] = regular_points[idx2], regular_points[idx1]
            
            # Aplicar 2-opt após mutação 90% das vezes (aumentado para compensar população inicial)
            if random.random() < 0.9:
                vehicle.route = two_opt_optimize(priority_points + regular_points, depot_location)
            else:
                vehicle.route = priority_points + regular_points
    
    # 20% das vezes: trocar pontos regulares entre veículos
    else:
        if len(mutated.vehicles) >= 2:
            v1, v2 = random.sample(mutated.vehicles, 2)
            
            _, reg1 = split_points_by_priority(v1.route)
            _, reg2 = split_points_by_priority(v2.route)
            
            if reg1 and reg2:
                point1 = random.choice(reg1)
                point2 = random.choice(reg2)
                
                if point1 in v1.route and point2 in v2.route:
                    idx1 = v1.route.index(point1)
                    idx2 = v2.route.index(point2)
                    v1.route[idx1] = point2
                    v2.route[idx2] = point1
    
    # Recalcular fitness
    calculate_multi_vehicle_fitness(mutated, depot_location)
    return mutated


def two_opt_optimize(route: List[ServicePoint], depot_location: Tuple[float, float]) -> List[ServicePoint]:
    """
    Otimização 2-opt SIMPLIFICADA para eliminar cruzamentos em uma rota
    Mantém pontos prioritários no início, otimiza apenas pontos regulares
    
    Args:
        route: Rota a otimizar
        depot_location: Localização do depósito
    
    Returns:
        Rota otimizada
    """
    if len(route) <= 3:
        return route
    
    # Separar prioridades e regulares
    priority_points, regular_points = split_points_by_priority(route)
    
    # Otimizar apenas pontos regulares (prioridades devem manter ordem)
    if len(regular_points) <= 2:
        return route
    
    # Calcular distância total de uma rota
    def calc_total_distance(points):
        if not points:
            return 0
        total = 0
        # Do último ponto prioritário (ou depósito) ao primeiro regular
        if priority_points:
            total += calculate_distance(priority_points[-1].location, points[0].location)
        else:
            total += calculate_distance(depot_location, points[0].location)
        
        # Entre pontos regulares
        for i in range(len(points) - 1):
            total += calculate_distance(points[i].location, points[i + 1].location)
        
        # Do último regular de volta ao depósito
        total += calculate_distance(points[-1].location, depot_location)
        return total
    
    improved = True
    max_iterations = 30
    iteration = 0
    
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        best_distance = calc_total_distance(regular_points)
        
        for i in range(len(regular_points) - 1):
            for j in range(i + 2, len(regular_points) + 1):
                # Tentar reverter segmento [i:j]
                new_route = regular_points[:i] + list(reversed(regular_points[i:j])) + regular_points[j:]
                new_distance = calc_total_distance(new_route)
                
                # Se melhorou, aplicar
                if new_distance < best_distance - 0.1:
                    regular_points = new_route
                    best_distance = new_distance
                    improved = True
                    break
            
            if improved:
                break
    
    return priority_points + regular_points


def sort_multi_vehicle_population(
    population: List[MultiVehicleSolution]
) -> List[MultiVehicleSolution]:
    """Ordena população por fitness (menor = melhor)"""
    return sorted(population, key=lambda s: s.total_fitness)

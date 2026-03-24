"""
Sistema de Otimização de Rotas com Múltiplos Veículos
Gerencia 2 veículos para atender todos os pontos em até 1 dia
- Pontos prioritários (EME, VIO, MED, POS) devem ser atendidos até 12h
- Pontos regulares (REG) podem ser atendidos após a entrega dos prioritários, mas devem ser concluídos até 18h
- Veículos partem e retornam ao mesmo depósito
"""

from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import copy
import random
from .service_points import ServicePoint, ServicePriority, calculate_distance, calculate_travel_time

# Ponto de partida/depósito (será definido dinamicamente)
DEPOT_LOCATION: Optional[Tuple[float, float]] = None

# Mapeamento global de pontos para clusters (mantém divisão K-means)
POINT_TO_CLUSTER: Dict[int, int] = {}


@dataclass
class VehicleRoute:
    """ Representa a rota de um veículo """
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
    """ Representa uma solução completa com múltiplos veículos """
    vehicles: List[VehicleRoute]
    total_fitness: float = float('inf')
    
    def get_all_points(self) -> List[ServicePoint]:
        """ Retorna todos os pontos de todas as rotas """
        all_points = []
        for vehicle in self.vehicles:
            all_points.extend(vehicle.route)
        return all_points
    
    def get_point_ids(self) -> set:
        """ Retorna conjunto de IDs de todos os pontos """
        return {point.id for vehicle in self.vehicles for point in vehicle.route}


def calculate_vehicle_route_time_and_distance(route: List[ServicePoint],
                                              depot_location: Tuple[float, float],
                                              start_time: float = 450.0,  # 7:30h (7*60 + 30 = 450 min)
                                              speed: float = 60.0,
                                              work_start: float = 450.0,  # 7:30h      # 1080.0 = 18h
                                              work_end: float = 1080.0) -> Tuple[float, float, List[float]]:
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


def divide_priority_points_geographically(priority_points: List[ServicePoint],
                                          depot_location: Tuple[float, float],
                                          num_vehicles: int = 2) -> List[List[ServicePoint]]:
    """
    Divide pontos prioritários geograficamente entre veículos usando K-means clustering
    Divisão inteligente que minimiza distâncias e cruzamentos
    
    Args:
        priority_points: Lista de pontos prioritários
        depot_location: Localização do depósito
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
    
    # Usar K-means clustering para divisão inteligente
    import numpy as np
    
    # Extrair coordenadas dos pontos
    coords = np.array([p.location for p in priority_points])
    
    # Inicializar centroides de forma inteligente
    # Centroide 1: ponto mais distante do depósito
    distances_from_depot = [calculate_distance(depot_location, p.location) for p in priority_points]
    farthest_idx = np.argmax(distances_from_depot)
    centroid1 = coords[farthest_idx]
    
    # Centroide 2: ponto mais distante do centroide 1
    distances_from_c1 = [calculate_distance(tuple(centroid1), p.location) for p in priority_points]
    farthest_from_c1_idx = np.argmax(distances_from_c1)
    centroid2 = coords[farthest_from_c1_idx]
    
    centroids = np.array([centroid1, centroid2])
    
    # K-means: iterar até convergência (máximo 20 iterações)
    max_iterations = 20
    for iteration in range(max_iterations):
        # Atribuir cada ponto ao centroide mais próximo
        clusters = [[] for _ in range(num_vehicles)]
        cluster_indices = [[] for _ in range(num_vehicles)]
        
        for idx, point in enumerate(priority_points):
            distances = [calculate_distance(tuple(centroids[i]), point.location) for i in range(num_vehicles)]
            closest_cluster = np.argmin(distances)
            clusters[closest_cluster].append(point)
            cluster_indices[closest_cluster].append(idx)
        
        # Recalcular centroides
        new_centroids = []
        for i in range(num_vehicles):
            if cluster_indices[i]:
                cluster_coords = coords[cluster_indices[i]]
                new_centroid = np.mean(cluster_coords, axis=0)
                new_centroids.append(new_centroid)
            else:
                # Se cluster vazio, manter centroide anterior
                new_centroids.append(centroids[i])
        
        new_centroids = np.array(new_centroids)
        
        # Verificar convergência
        if np.allclose(centroids, new_centroids, atol=1.0):
            break
        
        centroids = new_centroids
    
    # Balancear clusters se muito desiguais (diferença máxima de 2 pontos)
    while len(clusters[0]) > len(clusters[1]) + 2:
        # Mover ponto de clusters[0] mais próximo do centroide de clusters[1]
        distances_to_c2 = [calculate_distance(tuple(centroids[1]), p.location) for p in clusters[0]]
        closest_idx = np.argmin(distances_to_c2)
        point_to_move = clusters[0].pop(closest_idx)
        clusters[1].append(point_to_move)
    
    while len(clusters[1]) > len(clusters[0]) + 2:
        distances_to_c1 = [calculate_distance(tuple(centroids[0]), p.location) for p in clusters[1]]
        closest_idx = np.argmin(distances_to_c1)
        point_to_move = clusters[1].pop(closest_idx)
        clusters[0].append(point_to_move)
    
    return clusters


def get_division_line_for_visualization(service_points: List[ServicePoint],
                                        depot_location: Tuple[float, float]) -> Optional[Dict]:
    """
    Retorna dados da linha divisória baseada em K-MEANS CLUSTERING
    Mostra linha que passa pelo DEPÓSITO e pelo ponto médio entre os 2 centroides
    
    Args:
        service_points: Lista de todos os pontos de atendimento
        depot_location: Localização do depósito
    
    Returns:
        Dicionário com dados da linha e centroides ou None se não houver pontos suficientes
    """
    if len(service_points) <= 2:
        return None
    
    import numpy as np
    
    # Usar K-means para encontrar 2 clusters
    coords = np.array([p.location for p in service_points])
    
    # Inicializar centroides
    distances_from_depot = [calculate_distance(depot_location, p.location) for p in service_points]
    farthest_idx = np.argmax(distances_from_depot)
    centroid1 = coords[farthest_idx]
    
    distances_from_c1 = [calculate_distance(tuple(centroid1), p.location) for p in service_points]
    farthest_from_c1_idx = np.argmax(distances_from_c1)
    centroid2 = coords[farthest_from_c1_idx]
    
    centroids = np.array([centroid1, centroid2])
    
    # K-means: iterar até convergência
    max_iterations = 20
    for iteration in range(max_iterations):
        cluster_indices = [[], []]
        
        for idx, point in enumerate(service_points):
            distances = [calculate_distance(tuple(centroids[i]), point.location) for i in range(2)]
            closest_cluster = np.argmin(distances)
            cluster_indices[closest_cluster].append(idx)
        
        new_centroids = []
        for i in range(2):
            if cluster_indices[i]:
                cluster_coords = coords[cluster_indices[i]]
                new_centroid = np.mean(cluster_coords, axis=0)
                new_centroids.append(new_centroid)
            else:
                new_centroids.append(centroids[i])
        
        new_centroids = np.array(new_centroids)
        
        if np.allclose(centroids, new_centroids, atol=1.0):
            break
        
        centroids = new_centroids
    
    # Calcular ponto médio entre centroides
    midpoint = (centroids[0] + centroids[1]) / 2
    
    # Criar linha que passa pelo DEPÓSITO e pelo PONTO MÉDIO entre centroides
    depot_array = np.array(depot_location)
    
    # Vetor do depósito ao ponto médio
    direction_vector = midpoint - depot_array
    
    # Normalizar vetor
    vector_length = np.linalg.norm(direction_vector)
    if vector_length > 0:
        direction_vector = direction_vector / vector_length
    
    # Criar linha que passa pelos dois pontos (depósito e midpoint)
    line_length = 2000
    p1 = tuple(depot_array - direction_vector * line_length)
    p2 = tuple(depot_array + direction_vector * line_length)
    
    return {
        'center': tuple(midpoint),
        'depot': depot_location,
        'p1': p1,
        'p2': p2,
        'centroid1': tuple(centroids[0]),
        'centroid2': tuple(centroids[1])
    }


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
        """ Verifica se segmento p1-p2 cruza com p3-p4 """
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


def validate_solution(solution: MultiVehicleSolution, 
                      expected_points: int = 20) -> Tuple[bool, str]:
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


def calculate_multi_vehicle_fitness(solution: MultiVehicleSolution,
                                    depot_location: Tuple[float, float],
                                    start_time: float = 450.0,          # 7:30h (7*60 + 30 = 450 min)
                                    priority_deadline: float = 720.0,   # 12h (meio-dia)
                                    speed: float = 60.0) -> float:
    """
    Calcula fitness para solução com múltiplos veículos
    
    Restrições:
    - Todos os 20 pontos devem estar presentes sem duplicação
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
        # Penalidade forte para soluções inválidas
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
                # Pontos prioritários devem ser atendidos até 12h
                if arrival_time > priority_deadline:
                    # Penalidade forte por violar deadline de prioridade: 10000 por minuto de atraso
                    overtime = arrival_time - priority_deadline
                    fitness += overtime * 10000
            
            # Verificar se passou das 18h (fim do dia)
            time_of_day = arrival_time % 1440
            if time_of_day >= 1080:  # 18h
                # Penalidade pesada por passar das 18h: 500000 base + 10000 por minuto de atraso
                overtime_18h = time_of_day - 1080
                fitness += 500000 + (overtime_18h * 10000)
        
        # Penalidade por violação de janelas de tempo
        for point, arrival_time in zip(vehicle.route, arrival_times):
            if point.time_window:
                penalty = point.time_window.get_penalty(arrival_time)
                fitness += penalty
    
    # Fitness base: distância total (peso baixo para priorizar restrições)
    fitness += total_distance * 1
    
    # Penalidade forte por desbalanceamento entre veículos: 500 por minuto de diferença
    if len(vehicle_times) > 1:
        max_time = max(vehicle_times)
        min_time = min(vehicle_times)
        imbalance = max_time - min_time
        fitness += imbalance * 500
    
    # Penalidade forte por desbalanceamento de número de pontos: 5000 por ponto de diferença
    if len(solution.vehicles) >= 2:
        point_counts = [len(v.route) for v in solution.vehicles]
        max_points = max(point_counts)
        min_points = min(point_counts)
        point_imbalance = max_points - min_points
        fitness += point_imbalance * 5000 
    
    # Penalidade MASSIVA por cruzamento de rotas: 500000 por cruzamento
    # Cruzamentos são INACEITÁVEIS e devem ser eliminados imediatamente
    # Aumentado de 50000 para 500000 (10x mais forte)
    if len(solution.vehicles) >= 2:
        crossings = count_route_crossings(solution.vehicles)
        fitness += crossings * 500000
    
    solution.total_fitness = fitness
    return fitness


def _build_nearest_neighbor_route(points: List[ServicePoint],
                                   start_location: Tuple[float, float]) -> List[ServicePoint]:
    """
    Constrói rota usando algoritmo do vizinho mais próximo
    Sempre escolhe o ponto não visitado mais próximo da posição atual """
    if not points:
        return []
    
    if len(points) == 1:
        return points[:]
    
    route = []
    remaining = points[:]
    current_location = start_location
    
    while remaining:
        # Encontrar ponto mais próximo da localização atual
        nearest_point = None
        nearest_distance = float('inf')
        nearest_idx = -1
        
        for idx, point in enumerate(remaining):
            distance = calculate_distance(current_location, point.location)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_point = point
                nearest_idx = idx
        
        # Adicionar ponto mais próximo à rota
        route.append(nearest_point)
        current_location = nearest_point.location
        remaining.pop(nearest_idx)
    
    return route


def fix_cluster_assignment(solution: MultiVehicleSolution,
                           service_points: List[ServicePoint]) -> MultiVehicleSolution:
    """
    Corrige atribuição de pontos aos veículos baseado no mapeamento K-means global
    Garante que cada ponto permaneça no cluster correto durante toda a evolução """
    global POINT_TO_CLUSTER
    
    if not POINT_TO_CLUSTER:
        # Se não há mapeamento, retornar solução sem alteração
        return solution
    
    # Criar novos veículos com pontos corretos
    corrected_vehicles = []
    num_vehicles = len(solution.vehicles)
    
    # Agrupar pontos por cluster correto
    cluster_points = [[] for _ in range(num_vehicles)]
    
    # Coletar todos os pontos da solução
    all_solution_points = solution.get_all_points()
    
    # Redistribuir pontos para clusters corretos
    for point in all_solution_points:
        correct_cluster = POINT_TO_CLUSTER.get(point.id, 0)
        cluster_points[correct_cluster].append(point)
    
    # Criar veículos com pontos corretos
    for i in range(num_vehicles):
        points = cluster_points[i]
        
        # Separar prioridades e regulares
        priority_points, regular_points = split_points_by_priority(points)
        
        # Ordenar prioridades por nível
        priority_points.sort(key=lambda p: p.priority.value)
        
        # Criar rota: prioridades primeiro, depois regulares
        route = priority_points + regular_points
        
        vehicle = VehicleRoute(vehicle_id=i + 1, route=route)
        corrected_vehicles.append(vehicle)
    
    corrected_solution = MultiVehicleSolution(vehicles=corrected_vehicles)
    return corrected_solution


def create_initial_multi_vehicle_solution(service_points: List[ServicePoint],
                                          depot_location: Tuple[float, float],
                                          num_vehicles: int = 2,
                                          apply_2opt: bool = False) -> MultiVehicleSolution:
    """
    Cria solução inicial dividindo pontos entre veículos usando K-MEANS CLUSTERING
    ARMAZENA mapeamento INICIAL de pontos para clusters (pode mudar durante evolução)
    
    Estratégia:
    1. Dividir pontos usando K-means clustering (divisão geográfica inteligente)
    2. Cada veículo atende um cluster de pontos próximos
    3. Cada veículo atende seus pontos prioritários primeiro, depois regulares
    4. Veículos partem e retornam ao depósito
    5. ARMAZENA cluster inicial (pode ser ajustado pelo algoritmo genético)
    
    Args:
        service_points: Lista de todos os pontos
        depot_location: Localização do depósito
        num_vehicles: Número de veículos (default: 2)
        apply_2opt: Se True, aplica otimização 2-opt (default: False)
    
    Returns:
        Solução inicial com múltiplos veículos
    """
    global POINT_TO_CLUSTER
    import numpy as np
    
    if len(service_points) <= num_vehicles:
        # Poucos pontos: distribuir manualmente
        all_points_groups = [[] for _ in range(num_vehicles)]
        for i, point in enumerate(service_points):
            all_points_groups[i % num_vehicles].append(point)
            POINT_TO_CLUSTER[point.id] = i % num_vehicles  # Armazenar cluster
    else:
        # Usar K-means clustering para divisão inteligente
        coords = np.array([p.location for p in service_points])
        
        # Inicializar centroides de forma inteligente
        # Centroide 1: ponto mais distante do depósito
        distances_from_depot = [calculate_distance(depot_location, p.location) for p in service_points]
        farthest_idx = np.argmax(distances_from_depot)
        centroid1 = coords[farthest_idx]
        
        # Centroide 2: ponto mais distante do centroide 1
        distances_from_c1 = [calculate_distance(tuple(centroid1), p.location) for p in service_points]
        farthest_from_c1_idx = np.argmax(distances_from_c1)
        centroid2 = coords[farthest_from_c1_idx]
        
        centroids = np.array([centroid1, centroid2])
        
        # K-means: iterar até convergência (máximo 20 iterações)
        max_iterations = 20
        for iteration in range(max_iterations):
            # Atribuir cada ponto ao centroide mais próximo
            clusters = [[] for _ in range(num_vehicles)]
            cluster_indices = [[] for _ in range(num_vehicles)]
            
            for idx, point in enumerate(service_points):
                distances = [calculate_distance(tuple(centroids[i]), point.location) for i in range(num_vehicles)]
                closest_cluster = np.argmin(distances)
                clusters[closest_cluster].append(point)
                cluster_indices[closest_cluster].append(idx)
            
            # Recalcular centroides
            new_centroids = []
            for i in range(num_vehicles):
                if cluster_indices[i]:
                    cluster_coords = coords[cluster_indices[i]]
                    new_centroid = np.mean(cluster_coords, axis=0)
                    new_centroids.append(new_centroid)
                else:
                    # Se cluster vazio, manter centroide anterior
                    new_centroids.append(centroids[i])
            
            new_centroids = np.array(new_centroids)
            
            # Verificar convergência
            if np.allclose(centroids, new_centroids, atol=1.0):
                break
            
            centroids = new_centroids
        
        # Balancear clusters se muito desiguais (diferença máxima de 2 pontos)
        while len(clusters[0]) > len(clusters[1]) + 2:
            # Mover ponto de clusters[0] mais próximo do centroide de clusters[1]
            distances_to_c2 = [calculate_distance(tuple(centroids[1]), p.location) for p in clusters[0]]
            closest_idx = np.argmin(distances_to_c2)
            point_to_move = clusters[0].pop(closest_idx)
            clusters[1].append(point_to_move)
        
        while len(clusters[1]) > len(clusters[0]) + 2:
            distances_to_c1 = [calculate_distance(tuple(centroids[0]), p.location) for p in clusters[1]]
            closest_idx = np.argmin(distances_to_c1)
            point_to_move = clusters[1].pop(closest_idx)
            clusters[0].append(point_to_move)
        
        all_points_groups = clusters
        
        # ARMAZENAR mapeamento INICIAL de pontos para clusters
        POINT_TO_CLUSTER.clear()
        for cluster_id, group in enumerate(all_points_groups):
            for point in group:
                POINT_TO_CLUSTER[point.id] = cluster_id
    
    # Para cada grupo, construir rota com ALTA DIVERSIDADE
    # Usar nearest neighbor APENAS se apply_2opt=True (soluções de qualidade)
    # Caso contrário, usar embaralhamento para diversidade
    vehicles = []
    for i in range(num_vehicles):
        group_points = all_points_groups[i]
        
        # Separar prioridades e regulares dentro do grupo
        priority_points, regular_points = split_points_by_priority(group_points)
        
        if apply_2opt:
            # NEAREST NEIGHBOR: Construir rota otimizada
            # Ordenar prioridades por nível primeiro
            priority_points.sort(key=lambda p: p.priority.value)
            
            # Aplicar nearest neighbor nos pontos regulares
            if regular_points:
                # Começar do último ponto prioritário (ou depósito se não houver)
                if priority_points:
                    current_pos = priority_points[-1].location
                else:
                    current_pos = depot_location
                
                regular_route = _build_nearest_neighbor_route(regular_points, current_pos, depot_location)
                route = priority_points + regular_route
            else:
                route = priority_points
        else:
            # EMBARALHAMENTO: Máxima diversidade
            # ORDENAR prioridades por nível (EME > VIO > MED > POS)
            priority_points.sort(key=lambda p: p.priority.value)
            
            # EMBARALHAR pontos de mesma prioridade para diversidade
            priority_dict = {}
            for point in priority_points:
                if point.priority not in priority_dict:
                    priority_dict[point.priority] = []
                priority_dict[point.priority].append(point)
            
            priority_route = []
            for priority in sorted(priority_dict.keys(), key=lambda p: p.value):
                group = priority_dict[priority]
                random.shuffle(group)  # Embaralhar dentro do mesmo nível
                priority_route.extend(group)
            
            # EMBARALHAR regulares completamente
            random.shuffle(regular_points)
            
            # Combinar rotas: prioridades primeiro, depois regulares
            route = priority_route + regular_points
        
        # Aplicar otimização 2-opt apenas se solicitado
        if apply_2opt:
            route = two_opt_optimize(route, depot_location)
        
        vehicle = VehicleRoute(vehicle_id=i + 1, route=route)
        vehicles.append(vehicle)
    
    solution = MultiVehicleSolution(vehicles=vehicles)
    calculate_multi_vehicle_fitness(solution, depot_location)
    
    return solution


def generate_multi_vehicle_population(service_points: List[ServicePoint],
                                      depot_location: Tuple[float, float],
                                      population_size: int,
                                      num_vehicles: int = 2) -> List[MultiVehicleSolution]:
    """
    Gera população inicial de soluções com múltiplos veículos
    ALTA DIVERSIDADE: Nenhuma solução usa 2-opt na criação inicial
    Permite que o AG explore e evolua naturalmente
    
    Args:
        service_points: Lista de todos os pontos
        depot_location: Localização do depósito
        population_size: Tamanho da população
        num_vehicles: Número de veículos
    
    Returns:
        Lista de soluções
    """
    population = []
    
    for i in range(population_size):
        # NUNCA aplicar 2-opt na população inicial para máxima diversidade
        # Deixar o AG evoluir naturalmente
        apply_2opt = False
        
        solution = create_initial_multi_vehicle_solution(service_points, depot_location, num_vehicles, apply_2opt=apply_2opt)
        
        # Adicionar ALTA variação para manter diversidade
        for vehicle in solution.vehicles:
            priority_points, regular_points = split_points_by_priority(vehicle.route)
            
            # Embaralhar pontos de mesma prioridade (90% das vezes para MÁXIMA diversidade)
            if random.random() < 0.9:
                priority_dict = {}
                for point in priority_points:
                    if point.priority not in priority_dict:
                        priority_dict[point.priority] = []
                    priority_dict[point.priority].append(point)
                
                # Reconstruir rota com ordem de prioridade
                new_route = []
                for priority in sorted(priority_dict.keys(), key=lambda p: p.value):
                    group = priority_dict[priority]
                    if len(group) > 1:
                        random.shuffle(group)
                    new_route.extend(group)
                
                # Embaralhar regulares 90% das vezes
                if len(regular_points) > 1 and random.random() < 0.9:
                    random.shuffle(regular_points)
                new_route.extend(regular_points)
                
                vehicle.route = new_route
            else:
                # Manter rota como está
                vehicle.route = priority_points + regular_points
        
        # Recalcular fitness
        calculate_multi_vehicle_fitness(solution, depot_location)
        population.append(solution)
    
    return population


def multi_vehicle_crossover(parent1: MultiVehicleSolution,
                            parent2: MultiVehicleSolution,
                            depot_location: Tuple[float, float],
                            service_points: List[ServicePoint]) -> MultiVehicleSolution:
    """
    Crossover entre duas soluções multi-veículo
    PERMITE trocas frequentes de pontos entre veículos (40% de chance)
    Garantia: Todos os 20 pontos são preservados sem duplicação
    """
    num_vehicles = len(parent1.vehicles)
    
    # 40% de chance de permitir troca de 1-3 pontos entre veículos (aumentado de 15%)
    allow_swap = random.random() < 0.40
    
    if allow_swap and num_vehicles == 2:
        # Coletar todos os pontos de ambos os veículos do parent1
        all_points_v1 = parent1.vehicles[0].route[:]
        all_points_v2 = parent1.vehicles[1].route[:]
        
        # Escolher 1-3 pontos aleatórios para trocar (aumentado de 1-2)
        num_swaps = random.randint(1, 3)
        
        # Trocar pontos entre veículos
        for _ in range(num_swaps):
            if all_points_v1 and all_points_v2:
                # Escolher ponto aleatório de cada veículo
                point_from_v1 = random.choice(all_points_v1)
                point_from_v2 = random.choice(all_points_v2)
                
                # Trocar os pontos
                all_points_v1.remove(point_from_v1)
                all_points_v2.remove(point_from_v2)
                all_points_v1.append(point_from_v2)
                all_points_v2.append(point_from_v1)
        
        # Criar veículos com pontos trocados
        child_vehicles = []
        for i, points in enumerate([all_points_v1, all_points_v2]):
            # Separar por prioridade e reorganizar
            priority_points, regular_points = split_points_by_priority(points)
            
            # Ordenar prioridades
            priority_points.sort(key=lambda p: p.priority.value)
            
            # Construir rota (sem 2-opt para permitir evolução)
            child_route = priority_points + regular_points
            
            child_vehicle = VehicleRoute(vehicle_id=i + 1, route=child_route)
            child_vehicles.append(child_vehicle)
        
        child = MultiVehicleSolution(vehicles=child_vehicles)
        calculate_multi_vehicle_fitness(child, depot_location)
        return child
    
    # Crossover normal (sem troca de veículos) - 60% das vezes (reduzido de 85%)
    child_vehicles = []
    for i in range(num_vehicles):
        route1 = parent1.vehicles[i].route
        route2 = parent2.vehicles[i].route
        
        # Separar por prioridade
        priority1, regular1 = split_points_by_priority(route1)
        priority2, regular2 = split_points_by_priority(route2)
        
        # Combinar prioridades (escolher ordem de um dos pais)
        if random.random() < 0.5:
            child_priority = priority1.copy()
        else:
            child_priority = priority2.copy()
        
        # Embaralhar prioridades de mesmo nível
        priority_dict = {}
        for point in child_priority:
            if point.priority not in priority_dict:
                priority_dict[point.priority] = []
            priority_dict[point.priority].append(point)
        
        # Reconstruir com ordem de prioridade, mas embaralhado dentro
        child_priority = []
        for priority in sorted(priority_dict.keys(), key=lambda p: p.value):
            group = priority_dict[priority]
            random.shuffle(group)
            child_priority.extend(group)
        
        # Combinar regulares (misturar ordem de ambos pais)
        if random.random() < 0.5:
            child_regular = regular1.copy()
        else:
            child_regular = regular2.copy()
        random.shuffle(child_regular)
        
        # Criar rota do veículo filho (sem 2-opt para permitir evolução)
        child_route = child_priority + child_regular
        
        child_vehicle = VehicleRoute(vehicle_id=i + 1, route=child_route)
        child_vehicles.append(child_vehicle)
    
    child = MultiVehicleSolution(vehicles=child_vehicles)
    calculate_multi_vehicle_fitness(child, depot_location)
    return child


def validate_and_repair_multi_vehicle_solution(solution: MultiVehicleSolution,
                                                 all_service_points: List[ServicePoint]) -> MultiVehicleSolution:
    """ Valida e repara solução multi-veículo para garantir que seja válida
    Garante:
    1. Todos os pontos estão presentes sem duplicação
    2. Ordem de prioridades é respeitada em cada veículo (EME → VIO → MED → POS → REG)
    3. Cada veículo tem uma rota válida
    """
    # Coletar todos os pontos da solução
    all_points_in_solution = solution.get_all_points()
    point_ids_in_solution = {p.id for p in all_points_in_solution}
    expected_point_ids = {p.id for p in all_service_points}
    
    # Verificar se há pontos faltando ou duplicados
    missing_points = expected_point_ids - point_ids_in_solution
    
    # Se há pontos faltando, redistribuir todos os pontos
    if missing_points:
        # Criar mapeamento de ID para ponto
        id_to_point = {p.id: p for p in all_service_points}
        
        # Redistribuir pontos igualmente entre veículos
        num_vehicles = len(solution.vehicles)
        points_per_vehicle = len(all_service_points) // num_vehicles
        
        # Embaralhar pontos para redistribuição aleatória
        shuffled_points = list(all_service_points)
        random.shuffle(shuffled_points)
        
        # Criar novas rotas
        for i, vehicle in enumerate(solution.vehicles):
            start_idx = i * points_per_vehicle
            end_idx = start_idx + points_per_vehicle if i < num_vehicles - 1 else len(shuffled_points)
            vehicle.route = shuffled_points[start_idx:end_idx]
    
    # Reorganizar cada veículo para respeitar prioridades
    for vehicle in solution.vehicles:
        # Remover duplicatas mantendo ordem
        seen = set()
        unique_route = []
        for point in vehicle.route:
            if point.id not in seen:
                seen.add(point.id)
                unique_route.append(point)
        
        # Separar por prioridade
        priority_points, regular_points = split_points_by_priority(unique_route)
        
        # Agrupar por nível de prioridade
        priority_groups = {
            ServicePriority.EMERGENCY_OBSTETRIC: [],
            ServicePriority.DOMESTIC_VIOLENCE: [],
            ServicePriority.HORMONAL_MEDICATION: [],
            ServicePriority.POSTPARTUM_CARE: [],
            ServicePriority.REGULAR: []
        }
        
        for point in priority_points:
            if point.priority in priority_groups:
                priority_groups[point.priority].append(point)
        
        # Reconstruir rota na ordem correta
        repaired_route = []
        priority_order = [
            ServicePriority.EMERGENCY_OBSTETRIC,
            ServicePriority.DOMESTIC_VIOLENCE,
            ServicePriority.HORMONAL_MEDICATION,
            ServicePriority.POSTPARTUM_CARE
        ]
        
        for priority in priority_order:
            repaired_route.extend(priority_groups[priority])
        
        repaired_route.extend(regular_points)
        vehicle.route = repaired_route
    
    return solution


def multi_vehicle_mutate(solution: MultiVehicleSolution,
                         depot_location: Tuple[float, float],
                         mutation_probability: float,
                         service_points: List[ServicePoint]) -> MultiVehicleSolution:
    """ Mutação de solução multi-veículo que sempre gera soluções válidas
    Permite trocas frequentes de pontos entre veículos (30% de chance)
    Caso contrário, apenas reordena pontos dentro de cada veículo """
    if random.random() >= mutation_probability:
        return solution
    
    mutated = copy.deepcopy(solution)
    
    # 30% de chance de trocar 1-2 pontos entre veículos (aumentado de 10%)
    if random.random() < 0.30 and len(mutated.vehicles) == 2:
        # Trocar 1-2 pontos entre os 2 veículos (aumentado de 1)
        num_swaps = random.randint(1, 2)
        
        for _ in range(num_swaps):
            if mutated.vehicles[0].route and mutated.vehicles[1].route:
                point_from_v1 = random.choice(mutated.vehicles[0].route)
                point_from_v2 = random.choice(mutated.vehicles[1].route)
                
                # Trocar os pontos
                mutated.vehicles[0].route.remove(point_from_v1)
                mutated.vehicles[1].route.remove(point_from_v2)
                mutated.vehicles[0].route.append(point_from_v2)
                mutated.vehicles[1].route.append(point_from_v1)
        
        # Reorganizar ambos os veículos (sem 2-opt para permitir evolução)
        for vehicle in mutated.vehicles:
            priority_points, regular_points = split_points_by_priority(vehicle.route)
            priority_points.sort(key=lambda p: p.priority.value)
            vehicle.route = priority_points + regular_points
    else:
        # Mutação normal: escolher um veículo aleatório para mutar
        vehicle = random.choice(mutated.vehicles)
        
        if len(vehicle.route) >= 2:
            priority_points, regular_points = split_points_by_priority(vehicle.route)
            
            # 60% das vezes: trocar dentro de pontos regulares (reduzido de 70%)
            if random.random() < 0.6 and len(regular_points) >= 2:
                idx1, idx2 = random.sample(range(len(regular_points)), 2)
                regular_points[idx1], regular_points[idx2] = regular_points[idx2], regular_points[idx1]
            
            # 40% das vezes: embaralhar pontos de mesma prioridade (aumentado de 30%)
            else:
                priority_dict = {}
                for point in priority_points:
                    if point.priority not in priority_dict:
                        priority_dict[point.priority] = []
                    priority_dict[point.priority].append(point)
                
                # Embaralhar um grupo de prioridade aleatório
                if priority_dict:
                    random_priority = random.choice(list(priority_dict.keys()))
                    random.shuffle(priority_dict[random_priority])
                
                # Reconstruir prioridades
                priority_points = []
                for priority in sorted(priority_dict.keys(), key=lambda p: p.value):
                    priority_points.extend(priority_dict[priority])
            
            # Não aplicar 2-opt para permitir evolução gradual
            vehicle.route = priority_points + regular_points
    
    # Sempre validar e reparar após mutação
    mutated = validate_and_repair_multi_vehicle_solution(mutated, service_points)
    
    # Recalcular fitness
    calculate_multi_vehicle_fitness(mutated, depot_location)
    return mutated


def _optimize_points_group(points: List[ServicePoint],
                           prev_location: Tuple[float, float],
                           next_location: Optional[Tuple[float, float]]) -> List[ServicePoint]:
    """
    Otimiza um grupo de pontos usando algoritmo 2-opt
    
    Args:
        points: Lista de pontos a otimizar
        prev_location: Localização do ponto anterior (ou depósito)
        next_location: Localização do próximo ponto (ou None se for o último grupo)
    
    Returns:
        Lista de pontos otimizada
    """
    if len(points) <= 2:
        return points
    
    def calc_distance(pts):
        if not pts:
            return 0
        total = calculate_distance(prev_location, pts[0].location)
        for i in range(len(pts) - 1):
            total += calculate_distance(pts[i].location, pts[i + 1].location)
        if next_location:
            total += calculate_distance(pts[-1].location, next_location)
        return total
    
    improved = True
    max_iterations = 100  # 100 iterações para otimização moderada
    iteration = 0
    optimized_points = points[:]
    
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        best_distance = calc_distance(optimized_points)
        
        for i in range(len(optimized_points) - 1):
            for j in range(i + 2, len(optimized_points) + 1):
                # Tentar reverter segmento [i:j]
                new_route = optimized_points[:i] + list(reversed(optimized_points[i:j])) + optimized_points[j:]
                new_distance = calc_distance(new_route)
                
                # Se melhorou, aplicar (sem tolerância para aceitar qualquer melhoria)
                if new_distance < best_distance:
                    optimized_points = new_route
                    best_distance = new_distance
                    improved = True
                    break
            
            if improved:
                break
    
    return optimized_points


def two_opt_optimize(route: List[ServicePoint],
                     depot_location: Tuple[float, float],
                     max_passes: int = 2) -> List[ServicePoint]:
    """
    Otimização 2-opt AGRESSIVA para eliminar cruzamentos
    Aplica 2-opt na rota COMPLETA ignorando prioridades temporariamente
    
    Estratégia:
    1. Aplica 2-opt na rota completa para eliminar TODOS os cruzamentos
    2. Reordena para respeitar prioridades (EME > VIO > MED > POS > REG)
    3. Aplica 2-opt novamente dentro de cada grupo de prioridade
    4. Repete até não haver mais melhoria
    
    Args:
        route: Rota a otimizar
        depot_location: Localização do depósito
        max_passes: Número máximo de passadas completas (default: 2)
    
    Returns:
        Rota otimizada
    """
    if len(route) <= 3:
        return route
    
    def calc_total_distance(r):
        """Calcula distância total da rota incluindo depósito"""
        if not r:
            return 0
        total = calculate_distance(depot_location, r[0].location)
        for i in range(len(r) - 1):
            total += calculate_distance(r[i].location, r[i + 1].location)
        total += calculate_distance(r[-1].location, depot_location)
        return total
    
    def apply_2opt_full(r):
        """Aplica 2-opt na rota completa sem respeitar prioridades"""
        improved = True
        max_iterations = 200  # Mais iterações para eliminar todos os cruzamentos
        iteration = 0
        optimized = r[:]
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            best_distance = calc_total_distance(optimized)
            
            for i in range(len(optimized) - 1):
                for j in range(i + 2, len(optimized) + 1):
                    # Tentar reverter segmento [i:j]
                    new_route = optimized[:i] + list(reversed(optimized[i:j])) + optimized[j:]
                    new_distance = calc_total_distance(new_route)
                    
                    if new_distance < best_distance - 0.01:
                        optimized = new_route
                        best_distance = new_distance
                        improved = True
                        break
                
                if improved:
                    break
        
        return optimized
    
    current_route = route[:]
    previous_distance = calc_total_distance(current_route)
    
    # Aplicar múltiplas passadas
    for pass_num in range(max_passes):
        # PASSO 1: Aplicar 2-opt na rota COMPLETA (ignora prioridades)
        optimized_route = apply_2opt_full(current_route)
        
        # PASSO 2: Reordenar para respeitar prioridades
        priority_points, regular_points = split_points_by_priority(optimized_route)
        
        # Agrupar por nível de prioridade
        priority_groups = {}
        for point in priority_points:
            if point.priority not in priority_groups:
                priority_groups[point.priority] = []
            priority_groups[point.priority].append(point)
        
        # Reconstruir rota respeitando ordem de prioridades
        reordered_route = []
        sorted_priorities = sorted(priority_groups.keys(), key=lambda p: p.value)
        
        for priority in sorted_priorities:
            reordered_route.extend(priority_groups[priority])
        
        reordered_route.extend(regular_points)
        
        # PASSO 3: Aplicar 2-opt dentro de cada grupo de prioridade
        final_route = []
        prev_location = depot_location
        
        for i, priority in enumerate(sorted_priorities):
            group = priority_groups[priority]
            
            # Determinar próxima localização
            if i < len(sorted_priorities) - 1:
                next_priority = sorted_priorities[i + 1]
                next_location = priority_groups[next_priority][0].location if priority_groups[next_priority] else None
            elif regular_points:
                next_location = regular_points[0].location
            else:
                next_location = depot_location
            
            # Otimizar grupo
            optimized_group = _optimize_points_group(group, prev_location, next_location)
            final_route.extend(optimized_group)
            
            if optimized_group:
                prev_location = optimized_group[-1].location
        
        # Otimizar regulares
        if len(regular_points) > 2:
            if final_route:
                prev_loc = final_route[-1].location
            else:
                prev_loc = depot_location
            
            optimized_regular = _optimize_points_group(regular_points, prev_loc, depot_location)
            final_route.extend(optimized_regular)
        else:
            final_route.extend(regular_points)
        
        # Verificar se houve melhoria
        new_distance = calc_total_distance(final_route)
        
        if new_distance < previous_distance - 0.01:
            current_route = final_route
            previous_distance = new_distance
        else:
            break
    
    return current_route


def calculate_population_diversity(population: List[MultiVehicleSolution]) -> float:
    """
    Calcula a diversidade genética da população usando distância euclidiana
    Mede quão diferentes são as rotas em termos de distância total percorrida
    """
    if len(population) < 2:
        return 0.0
    
    # Coletar fitness de todas as soluções
    fitness_values = [sol.total_fitness for sol in population]
    
    # Calcular desvio padrão normalizado como medida de diversidade
    import numpy as np
    mean_fitness = np.mean(fitness_values)
    std_fitness = np.std(fitness_values)
    
    # Normalizar pelo valor médio para ter uma medida relativa
    if mean_fitness > 0:
        diversity = std_fitness / mean_fitness
        # Limitar entre 0 e 1
        return min(diversity, 1.0)
    
    return 0.0


def sort_multi_vehicle_population(population: List[MultiVehicleSolution]) -> List[MultiVehicleSolution]:
    """ Ordena população por fitness (menor = melhor) """
    return sorted(population, key=lambda s: s.total_fitness)

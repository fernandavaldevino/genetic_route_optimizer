"""
Sistema de Otimização de Rotas com Múltiplos Veículos
Gerencia 2 veículos para atender todos os pontos em até 1 dia
- Pontos prioritários (EME, VIO, MED, POS) devem ser atendidos até 12h
- Pontos regulares (REG) podem ser atendidos após a entrega dos prioritários, mas devem ser concluídos até 18h
- Veículos partem e retornam ao mesmo depósito
"""

from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
import copy
import random
from .service_points import ServicePoint, ServicePriority, calculate_distance, calculate_travel_time

# Ponto de partida/depósito (será definido dinamicamente)
DEPOT_LOCATION: Optional[Tuple[float, float]] = None


@dataclass
class VehicleRoute:
    """ Representa a rota de um veículo """
    vehicle_id: int
    route: List[ServicePoint]
    total_distance: float = 0.0
    total_time: float = 0.0
    arrival_times: List[float] = field(default_factory=list)  # Bug #24: Usar field(default_factory)


@dataclass
class MultiVehicleSolution:
    """ Representa uma solução completa com múltiplos veículos """
    vehicles: List[VehicleRoute]
    total_fitness: float = float('inf')
    point_to_cluster: Dict[int, int] = field(default_factory=dict)  # Bug #16: Remover estado global
    
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
    Calcula tempo total e distância da rota de um veículo
    Inclui viagem do depósito ao primeiro ponto e do último ponto ao depósito
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
    """ Divide pontos em prioritários e regulares """
    priority_types = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE
    ]
    
    priority_points = [p for p in service_points if p.priority in priority_types]
    regular_points = [p for p in service_points if p.priority == ServicePriority.REGULAR]
    
    return priority_points, regular_points


def _compute_kmeans_clusters(
    points: List[ServicePoint],
    depot_location: Tuple[float, float],
    num_clusters: int = 2
) -> Tuple["np.ndarray", List[List[ServicePoint]]]:
    """
    Executa K-means clustering nos pontos fornecidos
    Inicialização inteligente:
      - Centroide 1: ponto mais distante do depósito
      - Centroide 2: ponto mais distante do centroide 1
    Balanceia clusters com diferença máxima de 2 pontos.
    Returns:
        (centroids, clusters) — centroides finais e lista de listas de pontos
    """
    import numpy as np

    if not points:
        return np.zeros((num_clusters, 2)), [[] for _ in range(num_clusters)]

    if len(points) <= num_clusters:
        result: List[List[ServicePoint]] = [[] for _ in range(num_clusters)]
        for i, point in enumerate(points):
            result[i % num_clusters].append(point)
        coords_fallback = np.array([p.location for p in points])
        centroids_fallback = np.zeros((num_clusters, 2))
        for i in range(min(len(points), num_clusters)):
            centroids_fallback[i] = coords_fallback[i]
        return centroids_fallback, result

    coords = np.array([p.location for p in points])

    # Inicialização inteligente dos centróides
    distances_from_depot = [calculate_distance(depot_location, p.location) for p in points]
    farthest_idx = int(np.argmax(distances_from_depot))
    centroid1 = coords[farthest_idx]

    distances_from_c1 = [calculate_distance(tuple(centroid1), p.location) for p in points]
    farthest_from_c1_idx = int(np.argmax(distances_from_c1))
    centroid2 = coords[farthest_from_c1_idx]

    centroids = np.array([centroid1, centroid2])

    # Iteração K-means até convergência (máximo 20 iterações)
    max_iterations = 20
    clusters: List[List[ServicePoint]] = [[] for _ in range(num_clusters)]
    for _ in range(max_iterations):
        clusters = [[] for _ in range(num_clusters)]
        cluster_indices: List[List[int]] = [[] for _ in range(num_clusters)]

        for idx, point in enumerate(points):
            distances = [calculate_distance(tuple(centroids[k]), point.location)
                         for k in range(num_clusters)]
            closest = int(np.argmin(distances))
            clusters[closest].append(point)
            cluster_indices[closest].append(idx)

        new_centroids = []
        for k in range(num_clusters):
            if cluster_indices[k]:
                cluster_coords = coords[cluster_indices[k]]
                new_centroids.append(np.mean(cluster_coords, axis=0))
            else:
                new_centroids.append(centroids[k])

        new_centroids_arr = np.array(new_centroids)
        if np.allclose(centroids, new_centroids_arr, atol=1.0):
            break
        centroids = new_centroids_arr

    # Balancear clusters: diferença máxima de 2 pontos
    while len(clusters[0]) > len(clusters[1]) + 2:
        dists = [calculate_distance(tuple(centroids[1]), p.location) for p in clusters[0]]
        idx = int(np.argmin(dists))
        clusters[1].append(clusters[0].pop(idx))

    while len(clusters[1]) > len(clusters[0]) + 2:
        dists = [calculate_distance(tuple(centroids[0]), p.location) for p in clusters[1]]
        idx = int(np.argmin(dists))
        clusters[0].append(clusters[1].pop(idx))

    return centroids, clusters


def divide_priority_points_geographically(priority_points: List[ServicePoint],
                                          depot_location: Tuple[float, float],
                                          num_vehicles: int = 2) -> List[List[ServicePoint]]:
    """ Divide pontos prioritários geograficamente entre veículos usando K-means clustering - minimiza distâncias e cruzamentos """
    if not priority_points:
        return [[] for _ in range(num_vehicles)]

    _, clusters = _compute_kmeans_clusters(priority_points, depot_location, num_vehicles)
    return clusters


def get_division_line_for_visualization(service_points: List[ServicePoint],
                                        depot_location: Tuple[float, float]) -> Optional[Dict]:
    """ Retorna dados da linha divisória baseada em K-Means Clustering - mostra linha que passa pelo Depósito e pelo ponto médio entre os 2 centróides """
    if len(service_points) <= 2:
        return None

    import numpy as np

    centroids, _ = _compute_kmeans_clusters(service_points, depot_location, 2)

    # Calcular ponto médio entre centroides
    midpoint = (centroids[0] + centroids[1]) / 2

    # Criar linha que passa pelo DEPÓSITO e pelo PONTO MÉDIO entre centroides
    depot_array = np.array(depot_location)
    direction_vector = midpoint - depot_array
    vector_length = np.linalg.norm(direction_vector)
    if vector_length > 0:
        direction_vector = direction_vector / vector_length

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
    """ Conta número de cruzamentos entre rotas de diferentes veículos, usando detecção de interseção de segmentos de linha """
    if len(vehicles) < 2:
        return 0
    
    # Verifica se dois segmentos de reta se cruzam no plano 2D
    def segments_intersect(p1, p2, p3, p4):
        """
        Verifica se segmento p1-p2 cruza com p3-p4 
        - p1, p2: Pontos extremos do primeiro segmento (tuplas (x, y))
        - p3, p4: Pontos extremos do segundo segmento (tuplas (x, y))
        """
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
                      expected_points: Optional[int] = None) -> Tuple[bool, str]:
    """ Valida se solução tem exatamente os pontos esperados sem duplicação """
    # Tornar expected_points parametrizável
    if expected_points is None:
        expected_points = len(solution.get_all_points())
    
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
                                    expected_points: Optional[int] = None,
                                    start_time: float = 450.0,          # 7:30h (7*60 + 30 = 450 min)
                                    priority_deadline: float = 720.0,   # 12h (meio-dia)
                                    speed: float = 60.0) -> float:
    """
    Calcula fitness para solução com múltiplos veículos
    
    Restrições:
    - Todos os pontos devem estar presentes sem duplicação
    - Pontos prioritários devem ser atendidos até 12h (720 min)
    - Todos os pontos devem ser atendidos em 1 dia (até 18h = 1080 min)
    - Minimizar distância total
    - Balancear carga entre veículos
    - Veículos partem e retornam ao depósito
    """
    # Usar expected_points parametrizável
    if expected_points is None:
        expected_points = len(solution.get_all_points())
    
    # VALIDAÇÃO CRÍTICA: Verificar unicidade de pontos
    is_valid, error_msg = validate_solution(solution, expected_points=expected_points)
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
        
        # Penalidades de tempo em escala de "distância equivalente"
        for point, arrival_time in zip(vehicle.route, arrival_times):
            time_of_day = arrival_time % 1440

            # Passar das 18h é inaceitável: penalidade hard (~10x rota completa)
            if time_of_day >= 1080:
                overtime_18h = time_of_day - 1080
                fitness += 5000 + (overtime_18h * 150)

            if point.priority in priority_types:
                # Pontos prioritários: apenas deadline de 12h
                # (não aplicar também time_window para evitar dupla penalização)
                if arrival_time > priority_deadline:
                    overtime = arrival_time - priority_deadline
                    fitness += overtime * 150  # 150 unidades/min — forte mas proporcional
            else:
                # Pontos regulares: penalidade por janela de tempo se definida
                if point.time_window and arrival_time > point.time_window.end_time:
                    minutes_late = arrival_time - point.time_window.end_time
                    fitness += minutes_late * 30
    
    # Fitness base: distância total sem multiplicador (referência de escala)
    fitness += total_distance
    
    # Desbalanceamento de tempo entre veículos: cada minuto de diferença ≈ 2 unidades de distância
    # Incentiva rotas equilibradas sem dominar o landscape de fitness
    if len(vehicle_times) > 1:
        max_time = max(vehicle_times)
        min_time = min(vehicle_times)
        imbalance = max_time - min_time
        fitness += imbalance * 2

    # Desbalanceamento de número de pontos: cada ponto extra ≈ 50 unidades de distância
    if len(solution.vehicles) >= 2:
        point_counts = [len(v.route) for v in solution.vehicles]
        point_imbalance = max(point_counts) - min(point_counts)
        fitness += point_imbalance * 50

    # Cruzamentos de rota: penalidade equivalente a ~10 rotas completas por cruzamento
    # Forte o suficiente para eliminar cruzamentos, mas não tão dominante que
    # o AG ignore a distância após removê-los (era 500.000 antes, razão era 500.000:1)
    if len(solution.vehicles) >= 2:
        crossings = count_route_crossings(solution.vehicles)
        fitness += crossings * 5000
    
    solution.total_fitness = fitness
    return fitness


def _build_nearest_neighbor_route(points: List[ServicePoint],
                                   start_location: Tuple[float, float],
                                   depot_location: Optional[Tuple[float, float]] = None) -> List[ServicePoint]:
    """
    Constrói rota usando vizinho mais próximo com lookahead de retorno ao depósito
    Quando restam exatamente 2 pontos, escolhe a ordem que minimiza a distância de retorno ao depósito
    Isso evita o problema clássico do nearest neighbor de deixar pontos
    distantes do depósito para o final da rota.
    """
    if not points:
        return []

    if len(points) == 1:
        return points[:]

    route: List[ServicePoint] = []
    remaining = points[:]
    current_location = start_location

    # Greedy nearest neighbor até restar 2 pontos
    while len(remaining) > 2:
        nearest = min(remaining, key=lambda p: calculate_distance(current_location, p.location))
        route.append(nearest)
        current_location = nearest.location
        remaining.remove(nearest)

    # Lookahead para os 2 últimos pontos: escolhe a ordem que minimiza custo total
    if len(remaining) == 2 and depot_location is not None:
        p_a, p_b = remaining[0], remaining[1]
        # Opção A→B
        cost_ab = (calculate_distance(current_location, p_a.location)
                   + calculate_distance(p_a.location, p_b.location)
                   + calculate_distance(p_b.location, depot_location))
        # Opção B→A
        cost_ba = (calculate_distance(current_location, p_b.location)
                   + calculate_distance(p_b.location, p_a.location)
                   + calculate_distance(p_a.location, depot_location))
        if cost_ab <= cost_ba:
            route.extend([p_a, p_b])
        else:
            route.extend([p_b, p_a])
    else:
        # Fallback: nearest neighbor puro para 1 ou 2 pontos sem depot
        while remaining:
            nearest = min(remaining, key=lambda p: calculate_distance(current_location, p.location))
            route.append(nearest)
            current_location = nearest.location
            remaining.remove(nearest)

    return route


def fix_cluster_assignment(solution: MultiVehicleSolution,
                           service_points: List[ServicePoint]) -> MultiVehicleSolution:
    """
    Corrige atribuição de pontos aos veículos baseado no mapeamento K-means
    Garante que cada ponto permaneça no cluster correto durante toda a evolução
    """
    # Usar mapeamento da solução em vez de global
    if not solution.point_to_cluster:
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
        correct_cluster = solution.point_to_cluster.get(point.id, 0)
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
    
    corrected_solution = MultiVehicleSolution(vehicles=corrected_vehicles, point_to_cluster=solution.point_to_cluster)
    return corrected_solution


def create_initial_multi_vehicle_solution(service_points: List[ServicePoint],
                                          depot_location: Tuple[float, float],
                                          num_vehicles: int = 2,
                                          apply_2opt: bool = False) -> MultiVehicleSolution:
    """
    Cria solução inicial dividindo pontos entre veículos usando K-Means Clustering
    Armazena mapeamento inicial de pontos para clusters (pode mudar durante evolução)
    
    Estratégia:
    1. Dividir pontos usando K-means clustering (divisão geográfica inteligente)
    2. Cada veículo atende um cluster de pontos próximos
    3. Cada veículo atende seus pontos prioritários primeiro, depois regulares
    4. Veículos partem e retornam ao depósito
    5. Armazena cluster inicial (pode ser ajustado pelo algoritmo genético)
    """
    # Usar mapeamento local em vez de global
    # K-means executado via função centralizada (sem duplicação)
    _, all_points_groups = _compute_kmeans_clusters(service_points, depot_location, num_vehicles)

    # Armazenar mapeamento de pontos para clusters
    point_to_cluster = {}
    for cluster_id, group in enumerate(all_points_groups):
        for point in group:
            point_to_cluster[point.id] = cluster_id
    
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
    
    solution = MultiVehicleSolution(vehicles=vehicles, point_to_cluster=point_to_cluster)
    calculate_multi_vehicle_fitness(solution, depot_location)
    
    return solution


def generate_multi_vehicle_population(service_points: List[ServicePoint],
                                      depot_location: Tuple[float, float],
                                      population_size: int,
                                      num_vehicles: int = 2) -> List[MultiVehicleSolution]:
    """
    Gera população inicial de soluções com múltiplos veículos.

    K-means executado UMA ÚNICA VEZ para determinar os clusters geográficos.
    A diversidade é gerada por embaralhamento dentro de cada cluster,
    evitando re-executar K-means population_size várias vezes.
    """
    # Usar mapeamento local em vez de global
    # K-means executado UMA VEZ — base fixa para toda a população inicial
    _, clusters = _compute_kmeans_clusters(service_points, depot_location, num_vehicles)

    # Armazenar mapeamento de pontos para clusters
    point_to_cluster = {}
    for cluster_id, group in enumerate(clusters):
        for point in group:
            point_to_cluster[point.id] = cluster_id

    population = []

    for _ in range(population_size):
        vehicles = []
        for v_idx in range(num_vehicles):
            group_points = clusters[v_idx][:]  # cópia — não mutar os clusters originais

            priority_points, regular_points = split_points_by_priority(group_points)

            # Embaralhar dentro do mesmo nível de prioridade para diversidade
            priority_dict: Dict[ServicePriority, List[ServicePoint]] = {}
            for point in priority_points:
                if point.priority not in priority_dict:
                    priority_dict[point.priority] = []
                priority_dict[point.priority].append(point)

            priority_route: List[ServicePoint] = []
            for priority in sorted(priority_dict.keys(), key=lambda p: p.value):
                group = priority_dict[priority]
                if len(group) > 1:
                    random.shuffle(group)
                priority_route.extend(group)

            # Embaralhar regulares para máxima diversidade
            if len(regular_points) > 1:
                random.shuffle(regular_points)

            route = priority_route + regular_points
            vehicles.append(VehicleRoute(vehicle_id=v_idx + 1, route=route))

        solution = MultiVehicleSolution(vehicles=vehicles, point_to_cluster=point_to_cluster)
        
        # Validar e reparar solução inicial para garantir ordem de prioridades
        solution = validate_and_repair_multi_vehicle_solution(solution, service_points)
        
        calculate_multi_vehicle_fitness(solution, depot_location)
        population.append(solution)

    return population


def multi_vehicle_crossover(parent1: MultiVehicleSolution,
                            parent2: MultiVehicleSolution,
                            depot_location: Tuple[float, float],
                            service_points: List[ServicePoint]) -> MultiVehicleSolution:
    """
    Crossover entre duas soluções multi-veículo
    Permite trocas frequentes de pontos entre veículos (40% de chance)
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
        
        # Sempre validar e reparar após crossover
        child = validate_and_repair_multi_vehicle_solution(child, service_points)
        
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
    
    # Sempre validar e reparar após crossover
    child = validate_and_repair_multi_vehicle_solution(child, service_points)
    
    calculate_multi_vehicle_fitness(child, depot_location)
    return child


def validate_and_repair_multi_vehicle_solution(solution: MultiVehicleSolution,
                                                 all_service_points: List[ServicePoint]) -> MultiVehicleSolution:
    """
    Valida e repara solução multi-veículo para garantir que seja válida
    Garante:
    1. Todos os pontos estão presentes sem duplicação
    2. Ordem de prioridades é respeitada em cada veículo (EME → VIO → MED → POS → REG)
    3. Cada veículo tem uma rota válida
    """
    # Remover duplicatas globais (entre veículos) primeiro
    global_seen = set()
    for vehicle in solution.vehicles:
        unique_route = []
        for point in vehicle.route:
            if point.id not in global_seen:
                global_seen.add(point.id)
                unique_route.append(point)
        vehicle.route = unique_route
    
    # Coletar todos os pontos da solução
    all_points_in_solution = solution.get_all_points()
    point_ids_in_solution = {p.id for p in all_points_in_solution}
    expected_point_ids = {p.id for p in all_service_points}
    
    # Verificar se há pontos faltando
    missing_ids = expected_point_ids - point_ids_in_solution
    
    # Se há pontos faltando, redistribuir
    if missing_ids:
        # Criar mapeamento de ID para ponto
        id_to_point = {p.id: p for p in all_service_points}
        missing_points = [id_to_point[pid] for pid in missing_ids]
        
        # Distribuir pontos faltantes ao veículo com menos pontos
        for mp in missing_points:
            smallest_vehicle = min(solution.vehicles, key=lambda v: len(v.route))
            smallest_vehicle.route.append(mp)
    
    # Reorganizar cada veículo para respeitar prioridades
    for vehicle in solution.vehicles:
        # Remover duplicatas locais mantendo ordem
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
    """
    Mutação de solução multi-veículo que sempre gera soluções válidas
    Permite trocas frequentes de pontos entre veículos (30% de chance)
    Caso contrário, apenas reordena pontos dentro de cada veículo
    """
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
    """ Otimiza um grupo de pontos usando algoritmo 2-opt """
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
    Otimização 2-opt que SEMPRE respeita ordem de prioridades
    
    Estratégia:
    1. Separa pontos por prioridade (EME, VIO, MED, POS, REG)
    2. Aplica 2-opt APENAS dentro de cada grupo de prioridade
    3. Mantém ordem: EME → VIO → MED → POS → REG
    4. Nunca mistura pontos de prioridades diferentes
    """
    if len(route) <= 3:
        return route
    
    # Separar por prioridade
    priority_points, regular_points = split_points_by_priority(route)
    
    # Agrupar por nível de prioridade
    priority_groups = {}
    for point in priority_points:
        if point.priority not in priority_groups:
            priority_groups[point.priority] = []
        priority_groups[point.priority].append(point)
    
    # Ordenar prioridades (EME < VIO < MED < POS)
    sorted_priorities = sorted(priority_groups.keys(), key=lambda p: p.value)
    
    # Aplicar 2-opt dentro de cada grupo de prioridade
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
        
        # Otimizar grupo (2-opt apenas dentro do grupo)
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
    
    return final_route


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

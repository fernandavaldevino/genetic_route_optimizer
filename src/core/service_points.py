"""
Sistema de Pontos de Atendimento com Prioridades e Restrições
Gerencia diferentes tipos de atendimento com suas características específicas
"""

from enum import Enum
from typing import List, Tuple, Optional
from dataclasses import dataclass
import math


class ServicePriority(Enum):
    """Níveis de prioridade para diferentes tipos de atendimento"""
    EMERGENCY_OBSTETRIC = 1      # Prioridade máxima
    DOMESTIC_VIOLENCE = 2         # Protocolos especiais
    HORMONAL_MEDICATION = 3       # Temperatura controlada
    POSTPARTUM_CARE = 4          # Janelas de tempo específicas
    REGULAR = 5                   # Atendimento regular


@dataclass
class TimeWindow:
    """Janela de tempo para atendimento"""
    start_time: float  # Tempo inicial (em minutos desde início do dia)
    end_time: float    # Tempo final (em minutos desde início do dia)
    
    def is_valid_time(self, arrival_time: float) -> bool:
        """Verifica se o tempo de chegada está dentro da janela"""
        return self.start_time <= arrival_time <= self.end_time
    
    def get_penalty(self, arrival_time: float) -> float:
        """Calcula penalidade por violação da janela de tempo"""
        if self.is_valid_time(arrival_time):
            return 0.0
        elif arrival_time < self.start_time:
            return (self.start_time - arrival_time) * 10  # Penalidade por chegar cedo
        else:
            return (arrival_time - self.end_time) * 50  # Penalidade maior por atraso


@dataclass
class ServicePoint:
    """
    Representa um ponto de atendimento com suas características específicas
    """
    id: int
    location: Tuple[float, float]  # Coordenadas (x, y)
    priority: ServicePriority
    time_window: Optional[TimeWindow] = None
    requires_temperature_control: bool = False
    requires_special_protocol: bool = False
    service_duration: float = 15.0  # Duração do atendimento em minutos
    
    def get_priority_weight(self) -> float:
        """Retorna peso baseado na prioridade (menor = mais importante)"""
        return self.priority.value
    
    def get_penalty_for_late_service(self, delay: float) -> float:
        """Calcula penalidade baseada no atraso e prioridade"""
        base_penalty = delay * self.get_priority_weight()
        
        # Penalidades específicas por tipo
        if self.priority == ServicePriority.EMERGENCY_OBSTETRIC:
            return base_penalty * 100  # Penalidade extremamente alta
        elif self.priority == ServicePriority.DOMESTIC_VIOLENCE:
            return base_penalty * 50   # Penalidade muito alta
        elif self.priority == ServicePriority.HORMONAL_MEDICATION:
            return base_penalty * 20   # Penalidade alta
        elif self.priority == ServicePriority.POSTPARTUM_CARE:
            return base_penalty * 30   # Penalidade alta
        else:
            return base_penalty


def create_service_point(
    id: int,
    location: Tuple[float, float],
    service_type: str,
    time_window: Optional[Tuple[float, float]] = None
) -> ServicePoint:
    """
    Factory function para criar pontos de atendimento baseado no tipo
    
    Args:
        id: Identificador único do ponto
        location: Coordenadas (x, y)
        service_type: Tipo de serviço ('emergency', 'violence', 'medication', 'postpartum', 'regular')
        time_window: Tupla opcional (início, fim) em minutos
    """
    
    tw = TimeWindow(time_window[0], time_window[1]) if time_window else None
    
    if service_type == 'emergency':
        return ServicePoint(
            id=id,
            location=location,
            priority=ServicePriority.EMERGENCY_OBSTETRIC,
            time_window=tw,
            requires_special_protocol=True,
            service_duration=30.0  # Atendimento mais longo
        )
    
    elif service_type == 'violence':
        return ServicePoint(
            id=id,
            location=location,
            priority=ServicePriority.DOMESTIC_VIOLENCE,
            time_window=tw,
            requires_special_protocol=True,
            service_duration=45.0  # Atendimento mais longo e cuidadoso
        )
    
    elif service_type == 'medication':
        # Horário comercial: 8h às 18h (480 a 1080 minutos)
        medication_tw = tw or TimeWindow(480, 1080)
        return ServicePoint(
            id=id,
            location=location,
            priority=ServicePriority.HORMONAL_MEDICATION,
            time_window=medication_tw,
            requires_temperature_control=True,
            service_duration=10.0  # Atendimento rápido
        )
    
    elif service_type == 'postpartum':
        return ServicePoint(
            id=id,
            location=location,
            priority=ServicePriority.POSTPARTUM_CARE,
            time_window=tw or TimeWindow(480, 720),  # Default: 8h às 12h
            service_duration=20.0
        )
    
    else:  # regular
        return ServicePoint(
            id=id,
            location=location,
            priority=ServicePriority.REGULAR,
            time_window=tw,
            service_duration=15.0
        )


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calcula distância euclidiana entre dois pontos"""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def calculate_travel_time(point1: Tuple[float, float], point2: Tuple[float, float],
                          speed: float = 40.0, scale_factor: float = 0.1) -> float:
    """
    Calcula tempo de viagem entre dois pontos
    
    Args:
        point1, point2: Coordenadas dos pontos
        speed: Velocidade média em km/h (default: 40 km/h)
        scale_factor: Fator de escala para converter coordenadas em km (default: 0.1 = 1 unidade = 100m)
    
    Returns:
        Tempo de viagem em minutos
    """
    distance_units = calculate_distance(point1, point2)
    distance_km = distance_units * scale_factor  # Converter para km
    time_hours = distance_km / speed
    return time_hours * 60  # Converter para minutos


def sort_by_priority(service_points: List[ServicePoint]) -> List[ServicePoint]:
    """
    Ordena pontos de atendimento por prioridade
    Emergências obstétricas primeiro, atendimentos regulares por último
    """
    return sorted(service_points, key=lambda sp: sp.get_priority_weight())


def validate_temperature_control_route(route: List[ServicePoint], 
                                       max_time_without_control: float = 120.0) -> Tuple[bool, str]:
    """
    Valida se medicamentos com controle de temperatura são entregues dentro do tempo limite
    
    Args:
        route: Lista de pontos de atendimento na ordem da rota
        max_time_without_control: Tempo máximo (em minutos) que medicamentos podem ficar sem controle
    
    Returns:
        Tupla (válido, mensagem)
    """
    current_time = 0.0
    last_medication_pickup = None
    
    for i, point in enumerate(route):
        if point.requires_temperature_control:
            if last_medication_pickup is not None:
                time_elapsed = current_time - last_medication_pickup
                if time_elapsed > max_time_without_control:
                    return False, f"Medicamento no ponto {point.id} excede tempo sem controle de temperatura"
            last_medication_pickup = current_time
        
        # Adicionar tempo de serviço
        current_time += point.service_duration
        
        # Adicionar tempo de viagem para o próximo ponto
        if i < len(route) - 1:
            travel_time = calculate_travel_time(point.location, route[i + 1].location)
            current_time += travel_time
    
    return True, "Rota válida para controle de temperatura"


def validate_special_protocol_sequence(route: List[ServicePoint]) -> Tuple[bool, str]:
    """
    Valida se pontos com protocolos especiais (violência doméstica) têm tempo adequado
    e não são agrupados de forma inadequada
    """
    for i, point in enumerate(route):
        if point.requires_special_protocol:
            # Verificar se há tempo suficiente alocado
            if point.service_duration < 30.0:
                return False, f"Ponto {point.id} requer mais tempo para protocolo especial"
            
            # Idealmente, não agrupar múltiplos casos especiais consecutivamente
            if i > 0 and route[i-1].requires_special_protocol:
                # Permitir, mas pode ser subótimo
                pass
    
    return True, "Protocolos especiais validados"


# Exemplo de uso
if __name__ == "__main__":
    # Criar pontos de atendimento de exemplo
    points = [
        create_service_point(1, (100, 200), 'emergency'),
        create_service_point(2, (300, 400), 'violence', time_window=(480, 600)),
        create_service_point(3, (500, 100), 'medication'),
        create_service_point(4, (200, 300), 'postpartum', time_window=(540, 660)),
        create_service_point(5, (400, 500), 'regular'),
    ]
    
    # Ordenar por prioridade
    sorted_points = sort_by_priority(points)
    
    print("Pontos ordenados por prioridade:")
    for point in sorted_points:
        print(f"ID: {point.id}, Prioridade: {point.priority.name}, "
              f"Localização: {point.location}")
    
    # Validar rota
    is_valid, message = validate_temperature_control_route(sorted_points)
    print(f"\nValidação de temperatura: {message}")
    
    is_valid, message = validate_special_protocol_sequence(sorted_points)
    print(f"Validação de protocolos: {message}")

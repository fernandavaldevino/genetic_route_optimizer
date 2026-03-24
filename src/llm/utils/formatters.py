"""
Utilitários para formatação de dados do algoritmo genético
para consumo pela LLM
"""

from typing import List, Dict, Any
from src.core.service_points import ServicePoint, ServicePriority
from src.core.genetic_algorithm import calculate_route_time_and_distance


def format_service_priority(priority: ServicePriority) -> str:
    """ Converte enum de prioridade para string legível """
    priority_map = {
        ServicePriority.EMERGENCY_OBSTETRIC: "Emergência Obstétrica",
        ServicePriority.DOMESTIC_VIOLENCE: "Violência Doméstica",
        ServicePriority.HORMONAL_MEDICATION: "Medicamento Hormonal",
        ServicePriority.POSTPARTUM_CARE: "Atendimento Pós-Parto",
        ServicePriority.REGULAR: "Atendimento Regular"
    }
    return priority_map.get(priority, str(priority))


def format_time_minutes(minutes: float) -> str:
    """  Converte minutos para formato legível (HH:MM) com indicação de dia se necessário """
    # Calcular dia (1440 minutos = 24 horas = 1 dia)
    day = int(minutes // 1440) + 1
    
    # Calcular horário do dia (0-1439 minutos)
    time_of_day = minutes % 1440
    hours = int(time_of_day // 60)
    mins = int(time_of_day % 60)
    
    # Se for dia 1, retornar apenas o horário
    if day == 1:
        return f"{hours:02d}:{mins:02d}"
    else:
        # Se for dia 2+, adicionar indicação do dia
        return f"{hours:02d}:{mins:02d} do dia {day}"


def format_duration(minutes: float) -> str:
    """ Formata duração em formato legível """
    if minutes >= 60:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        if mins > 0:
            return f"{hours}h {mins}min"
        return f"{hours}h"
    return f"{int(minutes)}min"


def route_to_dict(route: List[ServicePoint], 
                  start_time: float = 480.0,
                  speed: float = 60.0) -> Dict[str, Any]:
    """ Converte rota otimizada para dicionário estruturado """
    # Calcula métricas da rota
    total_distance, total_time, arrival_times = calculate_route_time_and_distance(
        route, start_time, speed
    )
    
    # Conta tipos de serviço (excluindo depósito - ID 0)
    service_types = {}
    for point in route:
        if point.id != 0:  # Não conta o depósito
            priority_name = point.priority.name
            service_types[priority_name] = service_types.get(priority_name, 0) + 1
    
    # Formata pontos
    points_data = []
    for i, point in enumerate(route):
        point_data = {
            'id': point.id,
            'order': i + 1,
            'location': point.location,
            'service_type': format_service_priority(point.priority),
            'priority': point.priority.value,
            'arrival_time': format_time_minutes(arrival_times[i]),
            'arrival_time_minutes': arrival_times[i],
            'service_duration': point.service_duration,
            'requires_temperature_control': point.requires_temperature_control,
            'requires_special_protocol': point.requires_special_protocol,
            'special_requirements': []
        }
        
        # Adiciona requisitos especiais
        if point.requires_temperature_control:
            point_data['special_requirements'].append('Controle de temperatura')
        if point.requires_special_protocol:
            point_data['special_requirements'].append('Protocolo especial')
        if point.time_window:
            point_data['special_requirements'].append(
                f'Janela de tempo: {format_time_minutes(point.time_window.start_time)} - '
                f'{format_time_minutes(point.time_window.end_time)}'
            )
        
        # Calcula distância e tempo até próximo ponto
        if i < len(route) - 1:
            from src.core.service_points import calculate_distance, calculate_travel_time
            next_point = route[i + 1]
            distance = calculate_distance(point.location, next_point.location)
            travel_time = calculate_travel_time(point.location, next_point.location, speed)
            
            point_data['distance_to_next'] = distance
            point_data['time_to_next'] = travel_time
        
        points_data.append(point_data)
    
    # Monta dicionário final
    route_dict = {
        'total_stops': len([p for p in route if p.id != 0]),  # Exclui depósito
        'total_distance': total_distance,
        'total_time': total_time,
        'total_time_formatted': format_duration(total_time),
        'start_time': format_time_minutes(start_time),
        'end_time': format_time_minutes(start_time + total_time),
        'service_types': service_types,
        'points': points_data
    }
    
    return route_dict


def route_to_summary(route_dict: Dict[str, Any]) -> str:
    """ Cria resumo textual da rota """
    summary = f"""
📍 RESUMO DA ROTA

Total de paradas: {route_dict['total_stops']}
Distância total: {route_dict['total_distance']:.2f} km
Tempo total: {route_dict['total_time_formatted']}
Horário: {route_dict['start_time']} - {route_dict['end_time']}

TIPOS DE ATENDIMENTO:
"""
    
    for service_type, count in route_dict['service_types'].items():
        summary += f"  • {service_type}: {count}\n"
    
    return summary

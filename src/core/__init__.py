"""
Módulo Core - Lógica principal do algoritmo genético e pontos de atendimento
"""

from .service_points import (
    ServicePoint,
    ServicePriority,
    TimeWindow,
    create_service_point,
    sort_by_priority,
    validate_temperature_control_route,
    validate_special_protocol_sequence
)

from .genetic_algorithm import (
    calculate_constrained_fitness,
    generate_priority_aware_population,
    sort_population_by_fitness,
    constrained_order_crossover,
    constrained_mutate,
    calculate_route_time_and_distance
)

__all__ = [
    'ServicePoint',
    'ServicePriority',
    'TimeWindow',
    'create_service_point',
    'sort_by_priority',
    'validate_temperature_control_route',
    'validate_special_protocol_sequence',
    'calculate_constrained_fitness',
    'generate_priority_aware_population',
    'sort_population_by_fitness',
    'constrained_order_crossover',
    'constrained_mutate',
    'calculate_route_time_and_distance'
]

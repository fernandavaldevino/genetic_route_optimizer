"""
Visualização do Algoritmo Genético com Restrições usando Pygame
Mostra rotas de atendimento com prioridades e restrições em tempo real
VERSÃO COM MÚLTIPLOS VEÍCULOS (2 veículos) + DEPÓSITO
"""

import pygame
from pygame.locals import *
import random
import sys
import copy
import math
import numpy as np
from typing import List, Tuple
from src.core.multi_vehicle import (
    generate_multi_vehicle_population,
    calculate_multi_vehicle_fitness,
    multi_vehicle_crossover,
    multi_vehicle_mutate,
    sort_multi_vehicle_population,
    MultiVehicleSolution,
    two_opt_optimize,
    count_route_crossings,
    calculate_population_diversity
)
from src.core.service_points import create_service_point, ServicePriority, ServicePoint, calculate_distance
from src.constants import (
    WIDTH, HEIGHT, NODE_RADIUS, FPS,
    INFO_PANEL_WIDTH, MAP_X_START, MAP_WIDTH, MAP_HEIGHT,
    PLOT_X_START, PLOT_Y_START, PLOT_WIDTH, PLOT_HEIGHT_2V as PLOT_HEIGHT,
    WHITE, BLACK, RED, BLUE, GREEN, ORANGE, PURPLE, YELLOW, GRAY, LIGHT_GRAY,
    DARK_GREEN, CYAN,
    PRIORITY_COLORS, VEHICLE_COLORS,
    N_POINTS, NUM_VEHICLES, POPULATION_SIZE_2V as POPULATION_SIZE,
    MUTATION_PROBABILITY_2V as MUTATION_PROBABILITY, VEHICLE_SPEED,
    MAP_COORD_MIN_X_2V, MAP_COORD_MAX_X_2V, MAP_COORD_MIN_Y, MAP_COORD_MAX_Y,
    GUARANTEED_SERVICE_TYPES, VIOLENCE_TIME_WINDOW_2V, POSTPARTUM_TIME_WINDOW_2V,
    PRIORITY_ABBREVIATIONS, MIN_DEPOT_DISTANCE,
    WORK_END_TIME, WORK_START_TIME, MINUTES_PER_DAY,
    ELITE_SIZE_2V, TOURNAMENT_SIZE_EARLY, TOURNAMENT_SIZE_MID, TOURNAMENT_SIZE_LATE,
    TOURNAMENT_EARLY_THRESHOLD, TOURNAMENT_MID_THRESHOLD,
    PRIORITY_DEADLINE_2V, TEMP_DIR, PROGRESS_FILE, SCREENSHOT_FILE,
    ELITE_SIZE_INITIAL, ELITE_SIZE_FINAL,
    MUTATION_RATE_INITIAL, MUTATION_RATE_FINAL,
    INITIAL_TEMPERATURE, FINAL_TEMPERATURE, COOLING_RATE,
    OPT2_INTERVAL_EARLY, OPT2_INTERVAL_MID, OPT2_INTERVAL_LATE,
    OPT2_EARLY_THRESHOLD, OPT2_MID_THRESHOLD,
    STAGNATION_THRESHOLD, DIVERSITY_INJECTION_MIN, DIVERSITY_INJECTION_MAX,
    GUIDED_GENERATION_THRESHOLD, GUIDED_TOP_SOLUTIONS,
    FORCED_OPT_PASSES, DIVERSITY_THRESHOLD_LOW, DIVERSITY_THRESHOLD_HIGH
)


def draw_depot(screen, depot_location, radius=15):
    """ Desenha o ponto de depósito (origem/destino) """
    pygame.draw.circle(screen, BLACK, depot_location, radius)
    pygame.draw.circle(screen, YELLOW, depot_location, radius - 3)
    pygame.draw.circle(screen, BLACK, depot_location, radius, 3)
    
    font = pygame.font.Font(None, 24)
    text = font.render("D", True, BLACK)
    text_rect = text.get_rect(center=depot_location)
    screen.blit(text, text_rect)


def draw_service_points(screen, service_points, radius):
    """ Desenha pontos de atendimento com cores baseadas na prioridade """
    for point in service_points:
        color = PRIORITY_COLORS.get(point.priority, GRAY)
        pygame.draw.circle(screen, color, point.location, radius)
        pygame.draw.circle(screen, BLACK, point.location, radius, 2)
        
        font = pygame.font.Font(None, 20)
        text = font.render(str(point.id), True, WHITE)
        text_rect = text.get_rect(center=point.location)
        screen.blit(text, text_rect)


def draw_arrow(screen, color, start, end, width=3, arrow_size=12, node_radius=12):
    """
    Desenha uma seta de start para end, parando ANTES da borda dos círculos
    
    Args:
        screen: Superfície do pygame
        color: Cor da seta
        start: Ponto inicial (x, y)
        end: Ponto final (x, y)
        width: Largura da linha
        arrow_size: Tamanho da ponta da seta
        node_radius: Raio dos círculos dos pontos (para parar antes da borda)
    """
    import math
    
    # Calcular vetor e distância
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx**2 + dy**2)
    
    if distance == 0:
        return
    
    # Normalizar vetor
    dx_norm = dx / distance
    dy_norm = dy / distance
    
    # Margem extra para evitar sobreposição (2 pixels além do raio)
    margin = 2
    
    # Ajustar pontos para parar antes da borda dos círculos
    # Start: avançar pelo raio + margem
    adjusted_start = (
        start[0] + dx_norm * (node_radius + margin),
        start[1] + dy_norm * (node_radius + margin)
    )
    
    # End: recuar pelo raio + margem + tamanho da seta
    adjusted_end = (
        end[0] - dx_norm * (node_radius + margin + arrow_size),
        end[1] - dy_norm * (node_radius + margin + arrow_size)
    )
    
    # Desenhar linha ajustada (para antes da borda)
    pygame.draw.line(screen, color, adjusted_start, adjusted_end, width)
    
    # Calcular ângulo da seta
    angle = math.atan2(dy, dx)
    
    # Ponto da ponta da seta (logo antes da borda do círculo)
    arrow_tip = (
        end[0] - dx_norm * (node_radius + margin),
        end[1] - dy_norm * (node_radius + margin)
    )
    
    # Pontos da base do triângulo da seta
    arrow_angle = math.pi / 5  # 36 graus (mais aberto)
    left_x = arrow_tip[0] - arrow_size * math.cos(angle - arrow_angle)
    left_y = arrow_tip[1] - arrow_size * math.sin(angle - arrow_angle)
    right_x = arrow_tip[0] - arrow_size * math.cos(angle + arrow_angle)
    right_y = arrow_tip[1] - arrow_size * math.sin(angle + arrow_angle)
    
    # Desenhar triângulo da seta preenchido
    pygame.draw.polygon(screen, color, [arrow_tip, (left_x, left_y), (right_x, right_y)])
    # Contorno preto para destacar
    pygame.draw.polygon(screen, BLACK, [arrow_tip, (left_x, left_y), (right_x, right_y)], 1)


def draw_vehicle_route(screen, route, vehicle_id, depot_location, draw_priority_colors=False, draw_light_gray=False):
    """ Desenha a rota de um veículo específico com setas """
    if not route:
        return
    
    # Se draw_light_gray, desenha linhas cinza clara e fina (segunda melhor rota)
    if draw_light_gray:
        line_color = (210, 210, 210)  # Cinza mais claro
        line_width = 1  # Linha fina
        
        # Linha do depósito ao primeiro ponto
        pygame.draw.line(screen, line_color, depot_location, route[0].location, line_width)
        
        # Linhas entre pontos
        for i in range(len(route) - 1):
            start_pos = route[i].location
            end_pos = route[i + 1].location
            pygame.draw.line(screen, line_color, start_pos, end_pos, line_width)
        
        # Linha do último ponto de volta ao depósito
        pygame.draw.line(screen, line_color, route[-1].location, depot_location, line_width)
        return
    
    vehicle_color = VEHICLE_COLORS.get(vehicle_id, GREEN)
    
    # Seta do depósito ao primeiro ponto
    if draw_priority_colors:
        first_color = PRIORITY_COLORS.get(route[0].priority, GRAY)
        draw_arrow(screen, first_color, depot_location, route[0].location, 2, 6)
    else:
        draw_arrow(screen, vehicle_color, depot_location, route[0].location, 3, 8)
    
    # Setas entre pontos
    for i in range(len(route) - 1):
        start_pos = route[i].location
        end_pos = route[i + 1].location
        
        if draw_priority_colors:
            line_color = PRIORITY_COLORS.get(route[i + 1].priority, GRAY)
            draw_arrow(screen, line_color, start_pos, end_pos, 2, 6)
        else:
            draw_arrow(screen, vehicle_color, start_pos, end_pos, 3, 8)
    
    # Seta do último ponto de volta ao depósito
    if draw_priority_colors:
        draw_arrow(screen, GRAY, route[-1].location, depot_location, 2, 6)
    else:
        draw_arrow(screen, vehicle_color, route[-1].location, depot_location, 3, 8)


def draw_info_panel(screen, generation, best_solution, elapsed_time=0, last_improvement_gen=0):
    """ Desenha painel de informações no lado esquerdo """
    pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, INFO_PANEL_WIDTH, HEIGHT))
    pygame.draw.line(screen, BLACK, (INFO_PANEL_WIDTH, 0), (INFO_PANEL_WIDTH, HEIGHT), 2)
    
    font_title = pygame.font.Font(None, 24)
    font_subtitle = pygame.font.Font(None, 18)
    font_text = pygame.font.Font(None, 16)
    font_small = pygame.font.Font(None, 14)
    
    x_start = 10
    y_start = 10
    line_height = 18
    
    # Título
    title = font_title.render("Otimização - 2 Veículos", True, BLACK)
    screen.blit(title, (x_start, y_start))
    y_start += 28
    
    # Informações gerais
    info_texts = [
        f"Geração: {generation}",
        f"Última otimização: {last_improvement_gen}",
        f"Fitness Total: {best_solution.total_fitness:.2f}",
    ]
    
    for text in info_texts:
        rendered = font_text.render(text, True, BLACK)
        screen.blit(rendered, (x_start, y_start))
        y_start += line_height
    
    # Tempo total decorrido
    if generation > 0:
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        
        if hours > 0:
            time_str = f"{hours}h{minutes:02d}m{seconds:02d}s"
        elif minutes > 0:
            time_str = f"{minutes}m{seconds:02d}s"
        else:
            time_str = f"{seconds}s"
        
        time_text = font_text.render(f"Duração: {time_str}", True, BLACK)
        screen.blit(time_text, (x_start, y_start))
        y_start += line_height
    
    y_start += 8
    
    # Informações dos veículos LADO A LADO COM LEGENDAS
    v_title = font_subtitle.render("Veículos:", True, BLACK)
    screen.blit(v_title, (x_start, y_start))
    y_start += line_height + 3
    
    # Cabeçalhos das colunas
    col1_x = x_start + 10
    col2_x = x_start + 180
    
    # Dados dos veículos
    for i, vehicle in enumerate(best_solution.vehicles):
        vehicle_color = VEHICLE_COLORS.get(vehicle.vehicle_id, BLACK)
        x_pos = col1_x if i == 0 else col2_x
        
        # Nome do veículo
        v_name = font_text.render(f"Veículo {vehicle.vehicle_id}:", True, vehicle_color)
        screen.blit(v_name, (x_pos, y_start))
        
        # Dados COM LEGENDAS
        data_y = y_start + line_height
        
        # Converter tempo de minutos para horas e minutos
        hours = int(vehicle.total_time // 60)
        minutes = int(vehicle.total_time % 60)
        time_str = f"{hours}h{minutes:02d}"
        
        # Converter distância para km (dividir por 0.1)
        distance_km = vehicle.total_distance * 0.1
        
        data_items = [
            ("Pontos:", f"{len(vehicle.route)}"),
            ("Dist:", f"{distance_km:.1f} km"),
            ("Tempo:", time_str)
        ]
        
        for j, (label, value) in enumerate(data_items):
            label_rendered = font_small.render(label, True, BLACK)
            screen.blit(label_rendered, (x_pos, data_y + j * 14))
            
            value_rendered = font_small.render(value, True, BLACK)
            screen.blit(value_rendered, (x_pos + label_rendered.get_width() + 3, data_y + j * 14))
    
    y_start += 70
    
    # Seção Prioridades
    legend_title = font_subtitle.render("Prioridades:", True, BLACK)
    screen.blit(legend_title, (x_start, y_start))
    y_start += line_height + 3
    
    # Encontrar IDs de cada prioridade
    priority_ids = {
        ServicePriority.EMERGENCY_OBSTETRIC: [],
        ServicePriority.DOMESTIC_VIOLENCE: [],
        ServicePriority.HORMONAL_MEDICATION: [],
        ServicePriority.POSTPARTUM_CARE: [],
        ServicePriority.REGULAR: []
    }
    
    for vehicle in best_solution.vehicles:
        for point in vehicle.route:
            priority_ids[point.priority].append(point.id)
    
    for priority in priority_ids:
        priority_ids[priority].sort()
    
    def format_id_range(ids):
        if not ids:
            return "()"
        elif len(ids) == 1:
            return f"({ids[0]})"
        elif len(ids) == 2:
            return f"({ids[0]}, {ids[1]})"
        else:
            return f"({ids[0]}...{ids[-1]})"
    
    legend_items = [
        ("Emergência Obstétrica", "EME", RED, ServicePriority.EMERGENCY_OBSTETRIC),
        ("Violência Doméstica", "VIO", ORANGE, ServicePriority.DOMESTIC_VIOLENCE),
        ("Medicamento Hormonal", "MED", BLUE, ServicePriority.HORMONAL_MEDICATION),
        ("Pós-Parto", "POS", PURPLE, ServicePriority.POSTPARTUM_CARE),
        ("Regular", "REG", GRAY, ServicePriority.REGULAR),
    ]
    
    for label, abbr, color, priority in legend_items:
        pygame.draw.circle(screen, color, (x_start + 6, y_start + 6), 5)
        pygame.draw.circle(screen, BLACK, (x_start + 6, y_start + 6), 5, 1)
        
        id_range = format_id_range(priority_ids[priority])
        text = font_small.render(f"{label} ({abbr}) - {id_range}", True, BLACK)
        screen.blit(text, (x_start + 18, y_start))
        y_start += 15
    
    y_start += 8
    
    # Ordem de Atendimento em 2 colunas (V1 e V2)
    order_title = font_subtitle.render("Ordem de Atendimento:", True, BLACK)
    screen.blit(order_title, (x_start, y_start))
    y_start += line_height + 3
    
    priority_abbr = PRIORITY_ABBREVIATIONS
    
    # Duas colunas para os veículos
    col1_x = x_start + 5
    col2_x = x_start + 175
    y_col_start = y_start
    
    for v_idx, vehicle in enumerate(best_solution.vehicles):
        vehicle_color = VEHICLE_COLORS.get(vehicle.vehicle_id, BLACK)
        x_pos = col1_x if v_idx == 0 else col2_x
        y_pos = y_col_start
        
        # Título do veículo
        v_title = font_small.render(f"Veículo {vehicle.vehicle_id}:", True, vehicle_color)
        screen.blit(v_title, (x_pos, y_pos))
        y_pos += 14
        
        # Mostrar todos os pontos
        for i in range(len(vehicle.route)):
            point = vehicle.route[i]
            arrival = vehicle.arrival_times[i] if i < len(vehicle.arrival_times) else 0
            
            time_of_day = arrival % 1440
            hours = int(time_of_day // 60)
            minutes = int(time_of_day % 60)
            
            abbr = priority_abbr.get(point.priority, "???")
            
            # Verificar se passou de 12h (720 min) para pontos prioritários
            is_priority = point.priority in [
                ServicePriority.EMERGENCY_OBSTETRIC,
                ServicePriority.DOMESTIC_VIOLENCE,
                ServicePriority.HORMONAL_MEDICATION,
                ServicePriority.POSTPARTUM_CARE
            ]
            
            # Destacar em vermelho se for prioritário E se passou de 12h (>= 720)
            time_color = RED if (is_priority and time_of_day >= 720) else BLACK
            
            text = f"{i+1}.P{point.id}-{abbr}"
            rendered = font_small.render(text, True, BLACK)
            screen.blit(rendered, (x_pos, y_pos))
            
            time_text = f"({hours:02d}:{minutes:02d})"
            time_rendered = font_small.render(time_text, True, time_color)
            screen.blit(time_rendered, (x_pos + rendered.get_width() + 2, y_pos))
            
            y_pos += 13


def draw_simple_plot(screen, x_data, y_data, best_fitness=None, last_improvement_gen=0):
    """ Desenha gráfico de evolução do fitness """
    if len(x_data) < 2:
        return
    
    margin_left = 50
    margin_bottom = 20
    margin_top = 20
    margin_right = 10
    
    plot_x = PLOT_X_START + margin_left
    plot_y = PLOT_Y_START + margin_top
    plot_w = PLOT_WIDTH - margin_left - margin_right
    plot_h = PLOT_HEIGHT - margin_top - margin_bottom
    
    # Fundo do gráfico
    pygame.draw.rect(screen, WHITE, (PLOT_X_START, PLOT_Y_START, PLOT_WIDTH, PLOT_HEIGHT))
    pygame.draw.rect(screen, BLACK, (plot_x, plot_y, plot_w, plot_h), 2)
    
    # Normalizar dados
    min_y = min(y_data)
    max_y = max(y_data)
    range_y = max_y - min_y if max_y != min_y else 1
    
    # Adicionar 15% de margem abaixo para espaço visível
    margin_y_bottom = range_y * 0.15
    # Adicionar 5% de margem acima
    margin_y_top = range_y * 0.05
    adjusted_min_y = min_y - margin_y_bottom
    adjusted_range_y = range_y + margin_y_bottom + margin_y_top
    
    max_x = len(x_data) - 1
    
    # Desenhar linha do gráfico
    points = []
    for i, (x, y) in enumerate(zip(x_data, y_data)):
        px = plot_x + int((i / max_x) * plot_w)
        # Normalizar com as margens ajustadas
        py = plot_y + int(((max_y + margin_y_top - y) / adjusted_range_y) * plot_h)
        points.append((px, py))
    
    if len(points) > 1:
        pygame.draw.lines(screen, BLUE, False, points, 2)

    # Marcar última melhoria no gráfico (recebido como parâmetro)
    if last_improvement_gen < len(points):
        px, py = points[last_improvement_gen]
        
        # Desenhar linha vertical tracejada
        dash_length = 5
        y_current = plot_y + plot_h
        while y_current > py:
            pygame.draw.line(screen, RED, (px, y_current), (px, max(y_current - dash_length, py)), 2)
            y_current -= dash_length * 2
        
        # Desenhar círculo no ponto de melhoria
        pygame.draw.circle(screen, RED, (px, py), 4)
        pygame.draw.circle(screen, WHITE, (px, py), 2)
        
        # Exibir número da geração horizontalmente
        font_gen = pygame.font.Font(None, 12)
        gen_text = font_gen.render(str(last_improvement_gen), True, RED)
        text_rect = gen_text.get_rect(center=(px, plot_y + plot_h + 10))
        screen.blit(gen_text, text_rect)
    
    # Fontes
    font_title = pygame.font.Font(None, 14)
    font_axis = pygame.font.Font(None, 11)
    
    # Título
    title = font_title.render("Evolução do Fitness", True, BLACK)
    screen.blit(title, (PLOT_X_START + 5, PLOT_Y_START + 3))
    
    # Valores do eixo Y
    y_labels = [min_y, max_y]
    for i, val in enumerate(y_labels):
        y_pos = plot_y + plot_h if i == 0 else plot_y
        label = font_axis.render(f"{val:.0f}", True, BLACK)
        screen.blit(label, (PLOT_X_START + 5, y_pos - 5))
    
    # Label do eixo Y
    y_label = font_axis.render("Fitness", True, BLACK)
    y_label_rotated = pygame.transform.rotate(y_label, 90)
    screen.blit(y_label_rotated, (PLOT_X_START + 2, plot_y + plot_h // 2 - 15))
    
    # Valores do eixo X
    x_labels = [0, max_x]
    for i, val in enumerate(x_labels):
        x_pos = plot_x if i == 0 else plot_x + plot_w
        label = font_axis.render(str(val), True, BLACK)
        label_rect = label.get_rect(center=(x_pos, plot_y + plot_h + 12))
        screen.blit(label, label_rect)
    
    # Label do eixo X
    x_label = font_axis.render("Geração", True, BLACK)
    x_label_rect = x_label.get_rect(center=(plot_x + plot_w // 2, plot_y + plot_h + 15))
    screen.blit(x_label, x_label_rect)


def draw_best_solution(screen, best_solution, best_fitness):
    """ Desenha a melhor solução abaixo do gráfico """
    font_title = pygame.font.Font(None, 18)
    font_solution = pygame.font.Font(None, 14)  # Reduzido de 16 para 14 para caber melhor
    
    y_below = PLOT_Y_START + PLOT_HEIGHT + 5
    x_start = PLOT_X_START + 5
    
    # Título
    text_title = font_title.render("Melhor Solução:", True, BLACK)
    screen.blit(text_title, (x_start, y_below))
    y_below += 18
    
    # Fitness
    text_fitness = font_solution.render(f"Fitness: {best_fitness:.2f}", True, BLACK)
    screen.blit(text_fitness, (x_start, y_below))
    y_below += 16
    
    # Desenhar 2 vetores (um para cada veículo)
    for vehicle in best_solution.vehicles:
        vehicle_color = VEHICLE_COLORS.get(vehicle.vehicle_id, BLACK)
        
        # Título do veículo com colchete de abertura
        v_text = font_solution.render(f"V{vehicle.vehicle_id}: [ ", True, vehicle_color)
        screen.blit(v_text, (x_start, y_below))
        x_pos = x_start + v_text.get_width()
        
        # IDs dos pontos coloridos por prioridade
        for i, point in enumerate(vehicle.route):
            color = PRIORITY_COLORS.get(point.priority, BLACK)
            id_text = str(point.id)
            id_rendered = font_solution.render(id_text, True, color)
            
            # Quebrar linha se necessário
            if x_pos + id_rendered.get_width() > PLOT_X_START + PLOT_WIDTH - 15:
                y_below += 14
                x_pos = x_start + 25  # Indentação para continuação
            
            screen.blit(id_rendered, (x_pos, y_below))
            x_pos += id_rendered.get_width()
            
            # Vírgula
            if i < len(vehicle.route) - 1:
                comma = font_solution.render(", ", True, BLACK)
                screen.blit(comma, (x_pos, y_below))
                x_pos += comma.get_width()
        
        # Fechar colchete
        bracket = font_solution.render(" ]", True, vehicle_color)
        screen.blit(bracket, (x_pos, y_below))
        y_below += 16  # Espaço entre vetores


def draw_final_solution_frame(screen, best_solution, best_fitness, generation, depot_location, service_points):
    """ Desenha frame final para 2 veículos """
    screen.fill(WHITE)
    
    # Fontes
    font_big = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)
    font_solution = pygame.font.Font(None, 22)
    font_tiny = pygame.font.Font(None, 18)
    
    # LADO ESQUERDO: Informações textuais
    left_x = 50
    y_pos = 50
    
    # Título principal
    title = font_big.render("OTIMIZAÇÃO CONCLUÍDA!", True, DARK_GREEN)
    screen.blit(title, (left_x, y_pos))
    y_pos += 70
    
    # Informações gerais
    info_text = font_medium.render(f"Gerações: {generation}", True, BLACK)
    screen.blit(info_text, (left_x, y_pos))
    y_pos += 40
    
    fitness_text = font_medium.render(f"Fitness: {best_fitness:.2f}", True, BLACK)
    screen.blit(fitness_text, (left_x, y_pos))
    y_pos += 60
    
    # Melhor Solução - 2 VETORES SEPARADOS (um para cada veículo)
    solution_title = font_small.render("Melhor Solução:", True, BLACK)
    screen.blit(solution_title, (left_x, y_pos))
    y_pos += 35
    
    # Desenhar 2 vetores separados
    for vehicle in best_solution.vehicles:
        vehicle_color = VEHICLE_COLORS.get(vehicle.vehicle_id, BLACK)
        x_pos = left_x
        
        # Título do veículo com colchete de abertura
        v_label = font_solution.render(f"V{vehicle.vehicle_id}: [ ", True, vehicle_color)
        screen.blit(v_label, (x_pos, y_pos))
        x_pos += v_label.get_width()
        
        # Desenhar cada ID com sua cor de prioridade
        for i, point in enumerate(vehicle.route):
            color = PRIORITY_COLORS.get(point.priority, BLACK)
            id_text = str(point.id)
            id_rendered = font_solution.render(id_text, True, color)
            
            # Quebrar linha se necessário
            if x_pos + id_rendered.get_width() > 550:
                y_pos += 26
                x_pos = left_x + 30  # Indentação
            
            screen.blit(id_rendered, (x_pos, y_pos))
            x_pos += id_rendered.get_width()
            
            # Vírgula
            if i < len(vehicle.route) - 1:
                comma = font_solution.render(", ", True, BLACK)
                screen.blit(comma, (x_pos, y_pos))
                x_pos += comma.get_width()
        
        # Colchete de fechamento
        bracket_close = font_solution.render(" ]", True, vehicle_color)
        screen.blit(bracket_close, (x_pos, y_pos))
        y_pos += 30  # Espaço entre vetores
    
    y_pos += 10
    
    # Fitness
    text_fitness = font_small.render(f"Fitness: {best_fitness:.2f}", True, BLACK)
    screen.blit(text_fitness, (left_x, y_pos))
    y_pos += 35
    
    # Calcular dias e horário da última entrega (excluindo depósito)
    max_day = 1
    last_arrival_global = 0
    passed_18h = False  # Flag para verificar se passou das 18h
    
    # Coletar todos os arrival_times de todos os veículos
    all_arrivals = []
    for vehicle in best_solution.vehicles:
        if vehicle.arrival_times and len(vehicle.arrival_times) > 0:
            all_arrivals.extend(vehicle.arrival_times)
    
    # Ordenar e pegar o último horário (20º medicamento entregue)
    if all_arrivals:
        all_arrivals.sort()
        last_arrival_global = all_arrivals[-1]  # Último medicamento entregue
        
        max_day = int(last_arrival_global // 1440) + 1
        time_of_day = last_arrival_global % 1440
        hours = int(time_of_day // 60)
        minutes = int(time_of_day % 60)
        last_time_str = f"{hours:02d}:{minutes:02d}"
        
        # Verificar se passou das 18h (1080 min)
        if time_of_day >= 1080:
            passed_18h = True
    else:
        last_time_str = "00:00"
    
    # Entrega dos medicamentos
    x_pos = left_x
    text_part1 = "Entrega dos medicamentos estimada em até "
    rendered_part1 = font_small.render(text_part1, True, BLACK)
    screen.blit(rendered_part1, (x_pos, y_pos))
    x_pos += rendered_part1.get_width()
    
    # Dias colorido (vermelho se passou das 18h)
    if passed_18h:
        # Se passou das 18h, mostrar em vermelho independente do dia
        days_text = f"{max_day} dia{'s' if max_day > 1 else ''}, às {last_time_str}."
        days_color = (200, 0, 0)  # vermelho
    elif max_day == 1:
        days_text = f"1 dia, às {last_time_str}."
        days_color = (0, 150, 0)
    elif max_day == 2:
        days_text = f"2 dias, às {last_time_str}."
        days_color = (255, 140, 0)
    else:
        days_text = f"{max_day} dias, às {last_time_str}."
        days_color = (200, 0, 0)
    
    font_days = pygame.font.Font(None, 26)
    rendered_days = font_days.render(days_text, True, days_color)
    screen.blit(rendered_days, (x_pos, y_pos - 2))
    
    y_pos += 50
    
    # Ordem de Atendimento (detalhada) em 2 colunas
    order_title = font_small.render("Ordem de Atendimento:", True, BLACK)
    screen.blit(order_title, (left_x, y_pos))
    y_pos += 30
    
    priority_abbr = PRIORITY_ABBREVIATIONS
    
    # Duas colunas (2V)
    col1_x = left_x + 10
    col2_x = left_x + 300
    y_col_start = y_pos
    
    # Adicionar títulos das colunas
    font_col_title = pygame.font.Font(None, 20)
    
    # Título Veículo 1 (verde escuro)
    v1_title = font_col_title.render("Veículo 1:", True, DARK_GREEN)
    screen.blit(v1_title, (col1_x, y_col_start))
    
    # Título Veículo 2 (ciano)
    v2_title = font_col_title.render("Veículo 2:", True, CYAN)
    screen.blit(v2_title, (col2_x, y_col_start))
    
    # Ajustar y_col_start para começar abaixo dos títulos
    y_col_start += 22
    
    # Criar listas separadas para cada veículo
    vehicle1_deliveries = []
    vehicle2_deliveries = []
    
    # Saída do depósito (comum)
    vehicle1_deliveries.append(("D", "DEP", 480, 1, True, 1))  # Veículo 1
    vehicle2_deliveries.append(("D", "DEP", 480, 1, True, 2))  # Veículo 2
    
    # Separar entregas por veículo
    for vehicle in best_solution.vehicles:
        for i, point in enumerate(vehicle.route):
            arrival = vehicle.arrival_times[i] if i < len(vehicle.arrival_times) else 0
            day = int(arrival // 1440) + 1
            abbr = priority_abbr.get(point.priority, "???")
            
            if vehicle.vehicle_id == 1:
                vehicle1_deliveries.append((f"P{point.id}", abbr, arrival, day, False, 1))
            else:
                vehicle2_deliveries.append((f"P{point.id}", abbr, arrival, day, False, 2))
    
    # Adicionar retorno ao depósito para cada veículo
    from src.core.service_points import calculate_travel_time
    
    for vehicle in best_solution.vehicles:
        if vehicle.arrival_times and len(vehicle.arrival_times) > 0 and vehicle.route:
            last_arrival = vehicle.arrival_times[-1]
            last_point = vehicle.route[-1]
            
            # Calcular tempo real de retorno ao depósito
            return_travel_time = calculate_travel_time(last_point.location, depot_location, VEHICLE_SPEED)
            service_time = last_point.service_duration
            return_arrival = last_arrival + service_time + return_travel_time
            return_day = int(return_arrival // 1440) + 1
            
            if vehicle.vehicle_id == 1:
                vehicle1_deliveries.append(("D", "DEP", return_arrival, return_day, False, 1))
            else:
                vehicle2_deliveries.append(("D", "DEP", return_arrival, return_day, False, 2))
    
    # Desenhar coluna 1 (Veículo 1) com destaque vermelho para prioritários após 12h
    # Mostrar todos os itens (incluindo retorno)
    for idx, (point_id, abbr, arrival, day, is_saida, v_id) in enumerate(vehicle1_deliveries):
        time_of_day = arrival % 1440
        hours = int(time_of_day // 60)
        minutes = int(time_of_day % 60)
        
        x_pos_col = col1_x
        y_item = y_col_start + (idx * 20)
        
        # Verificar se é medicamento prioritário que passou de 12h ou se passou das 18h
        is_priority_med = abbr in ["EME", "VIO", "MED", "POS"]
        passed_18h = (time_of_day >= 1080 and not is_saida)  # 18h = 1080 min
        use_red = ((is_priority_med and time_of_day >= 720 and not is_saida) or passed_18h)
        text_color = RED if use_red else BLACK
        
        # Renderizar número em preto
        number_text = f"{idx+1}. "
        rendered_number = font_tiny.render(number_text, True, BLACK)
        screen.blit(rendered_number, (x_pos_col, y_item))
        x_offset = rendered_number.get_width()
        
        # Texto do ponto
        if is_saida:
            rest_text = f"{point_id}-{abbr} ({hours:02d}:{minutes:02d}, D{day}) (Saída)"
        elif idx == len(vehicle1_deliveries) - 1:  # Retorno
            rest_text = f"{point_id}-{abbr} ({hours:02d}:{minutes:02d}, D{day}) (Retorno)"
        else:
            rest_text = f"{point_id}-{abbr} ({hours:02d}:{minutes:02d}, D{day})"
        
        rendered_rest = font_tiny.render(rest_text, True, text_color)
        screen.blit(rendered_rest, (x_pos_col + x_offset, y_item))
    
    # Desenhar coluna 2 (Veículo 2)
    # Mostrar todos os itens (incluindo retorno)
    for idx, (point_id, abbr, arrival, day, is_saida, v_id) in enumerate(vehicle2_deliveries):
        time_of_day = arrival % 1440
        hours = int(time_of_day // 60)
        minutes = int(time_of_day % 60)
        
        x_pos_col = col2_x
        y_item = y_col_start + (idx * 20)
        
        # Verificar se é medicamento prioritário que passou de 12h ou se passou das 18h
        is_priority_med = abbr in ["EME", "VIO", "MED", "POS"]
        passed_18h = (time_of_day >= 1080 and not is_saida)  # 18h = 1080 min
        use_red = ((is_priority_med and time_of_day >= 720 and not is_saida) or passed_18h)
        text_color = RED if use_red else BLACK
        
        # Renderizar número em preto
        number_text = f"{idx+1}. "
        rendered_number = font_tiny.render(number_text, True, BLACK)
        screen.blit(rendered_number, (x_pos_col, y_item))
        x_offset = rendered_number.get_width()
        
        # Texto do ponto
        if is_saida:
            rest_text = f"{point_id}-{abbr} ({hours:02d}:{minutes:02d}, D{day}) (Saída)"
        elif idx == len(vehicle2_deliveries) - 1:  # Retorno
            rest_text = f"{point_id}-{abbr} ({hours:02d}:{minutes:02d}, D{day}) (Retorno)"
        else:
            rest_text = f"{point_id}-{abbr} ({hours:02d}:{minutes:02d}, D{day})"
        
        rendered_rest = font_tiny.render(rest_text, True, text_color)
        screen.blit(rendered_rest, (x_pos_col + x_offset, y_item))
    
    # Instruções
    exit_text = font_tiny.render("Pressione Q ou ESC para sair  |  Pressione R para reiniciar", True, GRAY)
    screen.blit(exit_text, (left_x, HEIGHT - 50))
    
    # Lado direito: Visualização da rota (miniatura)
    # Área para desenhar a rota
    map_x_start = 600
    map_y_start = 100
    map_width = 750
    map_height = 650
    
    # Fundo branco para a área do mapa
    pygame.draw.rect(screen, WHITE, (map_x_start, map_y_start, map_width, map_height))
    pygame.draw.rect(screen, BLACK, (map_x_start, map_y_start, map_width, map_height), 2)
    
    # Calcular escala para caber no espaço
    # Encontrar limites dos pontos
    all_x = [p.location[0] for p in service_points] + [depot_location[0]]
    all_y = [p.location[1] for p in service_points] + [depot_location[1]]
    
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Adicionar margem
    margin = 30
    range_x = max_x - min_x
    range_y = max_y - min_y
    
    # Calcular escala
    scale_x = (map_width - 2 * margin) / range_x if range_x > 0 else 1
    scale_y = (map_height - 2 * margin) / range_y if range_y > 0 else 1
    scale = min(scale_x, scale_y)
    
    # Função para transformar coordenadas
    def transform(location):
        x = map_x_start + margin + (location[0] - min_x) * scale
        y = map_y_start + margin + (location[1] - min_y) * scale
        return (int(x), int(y))
    
    # Desenhar rotas (3 camadas) COM SETAS
    node_radius = 8
    
    # 1. Camada de prioridade com setas finas
    for vehicle in best_solution.vehicles:
        if not vehicle.route:
            continue
        depot_pos = transform(depot_location)
        first_pos = transform(vehicle.route[0].location)
        
        first_color = PRIORITY_COLORS.get(vehicle.route[0].priority, GRAY)
        draw_arrow(screen, first_color, depot_pos, first_pos, width=1, arrow_size=4, node_radius=node_radius)
        
        for i in range(len(vehicle.route) - 1):
            start_pos = transform(vehicle.route[i].location)
            end_pos = transform(vehicle.route[i + 1].location)
            line_color = PRIORITY_COLORS.get(vehicle.route[i + 1].priority, GRAY)
            draw_arrow(screen, line_color, start_pos, end_pos, width=1, arrow_size=4, node_radius=node_radius)
        
        last_pos = transform(vehicle.route[-1].location)
        draw_arrow(screen, GRAY, last_pos, depot_pos, width=1, arrow_size=4, node_radius=node_radius)
    
    # 2. Camada de veículo com setas grossas
    for vehicle in best_solution.vehicles:
        if not vehicle.route:
            continue
        vehicle_color = VEHICLE_COLORS.get(vehicle.vehicle_id, GREEN)
        depot_pos = transform(depot_location)
        first_pos = transform(vehicle.route[0].location)
        
        draw_arrow(screen, vehicle_color, depot_pos, first_pos, width=2, arrow_size=6, node_radius=node_radius)
        
        for i in range(len(vehicle.route) - 1):
            start_pos = transform(vehicle.route[i].location)
            end_pos = transform(vehicle.route[i + 1].location)
            draw_arrow(screen, vehicle_color, start_pos, end_pos, width=2, arrow_size=6, node_radius=node_radius)
        
        last_pos = transform(vehicle.route[-1].location)
        draw_arrow(screen, vehicle_color, last_pos, depot_pos, width=2, arrow_size=6, node_radius=node_radius)
    
    # 3. Desenhar pontos
    for point in service_points:
        pos = transform(point.location)
        color = PRIORITY_COLORS.get(point.priority, GRAY)
        pygame.draw.circle(screen, color, pos, node_radius)
        pygame.draw.circle(screen, BLACK, pos, node_radius, 1)
        
        # ID do ponto
        font_id = pygame.font.Font(None, 14)
        text = font_id.render(str(point.id), True, WHITE)
        text_rect = text.get_rect(center=pos)
        screen.blit(text, text_rect)
    
    # 4. Desenhar depósito
    depot_pos = transform(depot_location)
    pygame.draw.circle(screen, BLACK, depot_pos, 10)
    pygame.draw.circle(screen, YELLOW, depot_pos, 8)
    pygame.draw.circle(screen, BLACK, depot_pos, 10, 2)
    
    font_depot = pygame.font.Font(None, 16)
    text = font_depot.render("D", True, BLACK)
    text_rect = text.get_rect(center=depot_pos)
    screen.blit(text, text_rect)


def create_depot_and_service_points(n_points):
    """ Cria depósito e pontos de atendimento aleatórios """
    depot_x = MAP_X_START + 50
    depot_y = HEIGHT // 2
    depot_location = (depot_x, depot_y)
    
    service_points = []
    
    for i, service_type in enumerate(GUARANTEED_SERVICE_TYPES):
        while True:
            location = (
                random.randint(MAP_COORD_MIN_X_2V, MAP_COORD_MAX_X_2V),
                random.randint(MAP_COORD_MIN_Y, MAP_COORD_MAX_Y)
            )
            if calculate_distance(depot_location, location) > MIN_DEPOT_DISTANCE:
                break
        
        time_window = None
        if service_type == 'violence':
            time_window = VIOLENCE_TIME_WINDOW_2V
        elif service_type == 'postpartum':
            time_window = POSTPARTUM_TIME_WINDOW_2V
        
        point = create_service_point(i + 1, location, service_type, time_window)
        service_points.append(point)
    
    for i in range(len(GUARANTEED_SERVICE_TYPES), n_points):
        while True:
            location = (
                random.randint(MAP_COORD_MIN_X_2V, MAP_COORD_MAX_X_2V),
                random.randint(MAP_COORD_MIN_Y, MAP_COORD_MAX_Y)
            )
            if calculate_distance(depot_location, location) > MIN_DEPOT_DISTANCE:
                break
        
        point = create_service_point(i + 1, location, 'regular', None)
        service_points.append(point)
    
    return depot_location, service_points


def apply_simulated_annealing(solution: MultiVehicleSolution,
                               temperature: float,
                               depot_location: Tuple[float, float]) -> MultiVehicleSolution:
    """
    Aplica Simulated Annealing para aceitar soluções piores com probabilidade decrescente
    Ajuda a escapar de ótimos locais
    """
    import math
    
    # Criar solução vizinha (pequena perturbação)
    neighbor = copy.deepcopy(solution)
    
    # Escolher veículo aleatório
    vehicle = random.choice(neighbor.vehicles)
    
    if len(vehicle.route) >= 2:
        # 50% trocar 2 pontos, 50% reverter segmento
        if random.random() < 0.5:
            # Trocar 2 pontos
            idx1, idx2 = random.sample(range(len(vehicle.route)), 2)
            vehicle.route[idx1], vehicle.route[idx2] = vehicle.route[idx2], vehicle.route[idx1]
        else:
            # Reverter segmento aleatório
            if len(vehicle.route) >= 3:
                i = random.randint(0, len(vehicle.route) - 3)
                j = random.randint(i + 2, len(vehicle.route))
                vehicle.route[i:j] = reversed(vehicle.route[i:j])
    
    # Recalcular fitness
    from src.core.multi_vehicle import calculate_multi_vehicle_fitness
    calculate_multi_vehicle_fitness(neighbor, depot_location)
    
    # Aceitar se melhor OU com probabilidade baseada na temperatura
    delta = neighbor.total_fitness - solution.total_fitness
    
    if delta < 0:
        # Solução melhor: sempre aceitar
        return neighbor
    else:
        # Solução pior: aceitar com probabilidade exp(-delta/T)
        probability = math.exp(-delta / temperature) if temperature > 0 else 0
        if random.random() < probability:
            return neighbor
        else:
            return solution


def inject_diversity(population: List[MultiVehicleSolution],
                     service_points: List[ServicePoint],
                     depot_location: Tuple[float, float],
                     injection_rate: float,
                     elite_size: int) -> List[MultiVehicleSolution]:
    """
    Injeta diversidade na população substituindo soluções piores
    Mantém elite intacta e perturba algumas soluções elite
    """
    from src.core.multi_vehicle import (
        create_initial_multi_vehicle_solution,
        calculate_multi_vehicle_fitness,
        split_points_by_priority
    )
    
    num_to_replace = int(len(population) * injection_rate)
    
    # Manter elite intacta
    new_population = population[:elite_size]
    
    # Perturbar 30% da elite para explorar regiões próximas
    num_perturbed = max(1, elite_size // 3)
    for i in range(num_perturbed):
        perturbed = copy.deepcopy(population[i])
        
        # Aplicar perturbação forte
        for vehicle in perturbed.vehicles:
            if len(vehicle.route) >= 2:
                # Embaralhar pontos regulares
                priority_points, regular_points = split_points_by_priority(vehicle.route)
                random.shuffle(regular_points)
                vehicle.route = priority_points + regular_points
        
        calculate_multi_vehicle_fitness(perturbed, depot_location)
        new_population.append(perturbed)
    
    # Gerar novas soluções aleatórias
    num_new = num_to_replace - num_perturbed
    for _ in range(num_new):
        new_solution = create_initial_multi_vehicle_solution(
            service_points, depot_location, NUM_VEHICLES, apply_2opt=False
        )
        new_population.append(new_solution)
    
    # Completar população com soluções existentes
    remaining = POPULATION_SIZE - len(new_population)
    if remaining > 0:
        new_population.extend(population[elite_size:elite_size + remaining])
    
    return new_population[:POPULATION_SIZE]


def generate_guided_solutions(top_solutions: List[MultiVehicleSolution],
                              depot_location: Tuple[float, float],
                              num_solutions: int = 10) -> List[MultiVehicleSolution]:
    """ Gera novas soluções a partir das melhores, aplicando transformações graduais + 2-opt """
    from src.core.multi_vehicle import (
        calculate_multi_vehicle_fitness,
        two_opt_optimize,
        split_points_by_priority
    )
    
    guided_solutions = []
    
    for _ in range(num_solutions):
        # Escolher solução base aleatória das top
        base = copy.deepcopy(random.choice(top_solutions))
        
        # Aplicar transformações graduais
        for vehicle in base.vehicles:
            if len(vehicle.route) >= 2:
                priority_points, regular_points = split_points_by_priority(vehicle.route)
                
                # 70% trocar 2-3 pontos regulares
                if random.random() < 0.7 and len(regular_points) >= 2:
                    num_swaps = min(3, len(regular_points) // 2)
                    for _ in range(num_swaps):
                        idx1, idx2 = random.sample(range(len(regular_points)), 2)
                        regular_points[idx1], regular_points[idx2] = regular_points[idx2], regular_points[idx1]
                
                # Reconstruir rota
                vehicle.route = priority_points + regular_points
                
                # Aplicar 2-opt para otimizar
                vehicle.route = two_opt_optimize(vehicle.route, depot_location, max_passes=2)
        
        calculate_multi_vehicle_fitness(base, depot_location)
        guided_solutions.append(base)
    
    return guided_solutions


def calculate_diversity_adjustment(diversity: float) -> float:
    """ Calcula ajuste na taxa de mutação baseado na diversidade genética """
    if diversity < DIVERSITY_THRESHOLD_LOW:
        # Baixa diversidade: aumentar mutação 1.5x
        return 1.5
    elif diversity > DIVERSITY_THRESHOLD_HIGH:
        # Alta diversidade: diminuir mutação 0.7x
        return 0.7
    else:
        # Diversidade normal: sem ajuste
        return 1.0


def main(max_generations=10):
    import pickle
    import time
    import os
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Roteamento Multi-Veículo com Depósito - AG")
    clock = pygame.time.Clock()
    
    # Mostrar tela branca inicial para que a janela não fique preta
    screen.fill(WHITE)
    font = pygame.font.Font(None, 36)
    text = font.render("Gerando população inicial...", True, BLACK)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    
    depot_location, service_points = create_depot_and_service_points(N_POINTS)
    population = generate_multi_vehicle_population(service_points, depot_location, POPULATION_SIZE, NUM_VEHICLES)
    
    best_fitness_history = []
    generation = 0
    last_improvement_generation = 0  # Rastreia última geração com melhoria
    MAX_GENERATIONS = max_generations  # Parâmetro configurável
    finished = False  # Flag para controlar estado final
    screenshot_saved = False  # Flag para salvar screenshot apenas uma vez
    
    # Controle de tempo
    import time
    start_time = time.time()
    elapsed_time = 0
    
    # Variáveis para otimizações avançadas
    stagnation_counter = 0  # Contador de gerações sem melhoria
    temperature = INITIAL_TEMPERATURE  # Temperatura para Simulated Annealing
    best_fitness_ever = float('inf')  # Melhor fitness já encontrado
    
    # Arquivos para comunicação com Streamlit
    progress_file = os.path.join(TEMP_DIR, PROGRESS_FILE)
    screenshot_file = os.path.join(TEMP_DIR, SCREENSHOT_FILE)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and not finished:
                    # R só funciona se não terminou
                    depot_location, service_points = create_depot_and_service_points(N_POINTS)
                    population = generate_multi_vehicle_population(service_points, depot_location, POPULATION_SIZE, NUM_VEHICLES)
                    best_fitness_history = []
                    generation = 0
        
        # Critério de parada: número de gerações parametrizado
        # Modo infinito: MAX_GENERATIONS = -1 (para após 5000 gerações sem melhoria)
        if not finished:
            if MAX_GENERATIONS > 0 and generation > MAX_GENERATIONS:
                # Modo normal: parar ao atingir número de gerações
                print(f"\n{'='*60}")
                print(f"CRITÉRIO DE PARADA ATINGIDO: {MAX_GENERATIONS} gerações")
                print(f"{'='*60}")
                print(f"Melhor Fitness Final: {best_fitness:.2f}")
                for vehicle in best_solution.vehicles:
                    hours = int(vehicle.total_time // 60)
                    minutes = int(vehicle.total_time % 60)
                    distance_km = vehicle.total_distance * 0.1
                    print(f"  Veículo {vehicle.vehicle_id}: {len(vehicle.route)} pontos, "
                          f"Dist={distance_km:.1f} km, Tempo={hours}h{minutes:02d}")
                print(f"{'='*60}\n")
                finished = True
            elif MAX_GENERATIONS == -1 and stagnation_counter >= 5000:
                # Modo infinito: parar após 5000 gerações sem melhoria
                print(f"\n{'='*60}")
                print(f"CRITÉRIO DE PARADA ATINGIDO: 5000 gerações sem melhoria")
                print(f"{'='*60}")
                print(f"Melhor Fitness Final: {best_fitness:.2f}")
                for vehicle in best_solution.vehicles:
                    hours = int(vehicle.total_time // 60)
                    minutes = int(vehicle.total_time % 60)
                    distance_km = vehicle.total_distance * 0.1
                    print(f"  Veículo {vehicle.vehicle_id}: {len(vehicle.route)} pontos, "
                          f"Dist={distance_km:.1f} km, Tempo={hours}h{minutes:02d}")
                print(f"{'='*60}\n")
                finished = True
        
        # Se terminou, mostrar frame final, salvar dados e fechar após 2 segundos
        if finished:
            # Desenhar tela final
            draw_final_solution_frame(screen, best_solution, best_fitness, MAX_GENERATIONS, depot_location, service_points)
            pygame.display.flip()
            
            # Salvar screenshot e dados apenas uma vez
            if not screenshot_saved:
                # Salvar screenshot
                pygame.image.save(screen, screenshot_file)
                print(f"Screenshot salvo em: {screenshot_file}")
                
                # Salvar dados para o Streamlit
                with open(progress_file, 'wb') as f:
                    pickle.dump({
                        'generation': generation,
                        'best_fitness': best_fitness,
                        'fitness_history': best_fitness_history,
                        'best_solution': best_solution,
                        'completed': True
                    }, f)
                print(f"Dados salvos em: {progress_file}")
                
                screenshot_saved = True
                
                # Aguardar 2 segundos antes de fechar
                print("Fechando em 2 segundos...")
                time.sleep(2)
                running = False
            
            continue
        
        # Se já terminou, não processar mais gerações
        if finished:
            continue
        
        screen.fill(WHITE)
        
        # Calcular tempo decorrido
        elapsed_time = time.time() - start_time
        
        # ORDENAR POPULAÇÃO ANTES DE QUALQUER COISA
        population = sort_multi_vehicle_population(population)
        
        # EXTRAIR MELHOR SOLUÇÃO ATUAL DA POPULAÇÃO
        current_best = population[0]
        current_fitness = current_best.total_fitness
        
        # PRESERVAR MELHOR SOLUÇÃO GLOBAL (nunca perde a melhor já encontrada)
        if generation == 0:
            best_solution = copy.deepcopy(current_best)
            best_fitness = current_fitness
            best_fitness_ever = best_fitness
            print(f"\n{'='*60}")
            print(f"FITNESS INICIAL: {best_fitness:.2f}")
            print(f"{'='*60}\n")
        else:
            # Se encontrou solução melhor, atualizar
            if current_fitness < best_fitness:
                best_solution = copy.deepcopy(current_best)
                best_fitness = current_fitness
                
                # Considerar melhoria se for pelo menos 0.1% melhor que o histórico
                if best_fitness < best_fitness_history[-1] * 0.999:
                    improvement = best_fitness_history[-1] - best_fitness
                    last_improvement_generation = generation
                    stagnation_counter = 0
                    print(f"✓ Geração {generation}: MELHORIA de {improvement:.2f} (Fitness: {best_fitness:.2f})")
                
                # Atualizar melhor fitness ever
                if best_fitness < best_fitness_ever:
                    best_fitness_ever = best_fitness
            else:
                # Se não houve melhoria: incrementar estagnação
                stagnation_counter += 1
        
        # SEMPRE adicionar a MELHOR solução global ao histórico (não a atual da população)
        best_fitness_history.append(best_fitness)
        
        # ============================================================================
        # OTIMIZAÇÃO FORÇADA: Se melhor solução tem cruzamentos, aplicar 2-opt AGRESSIVO
        # ============================================================================
        num_crossings = count_route_crossings(best_solution.vehicles)
        if num_crossings > 0:
            print(f"⚠️  Geração {generation}: {num_crossings} cruzamentos detectados! Aplicando 2-opt agressivo...")
            
            # Criar CÓPIA da melhor solução para otimizar
            optimized_solution = copy.deepcopy(best_solution)
            
            # Aplicar 2-opt agressivo em TODOS os veículos
            for vehicle in optimized_solution.vehicles:
                if vehicle.route:
                    vehicle.route = two_opt_optimize(vehicle.route, depot_location, max_passes=FORCED_OPT_PASSES)
            
            # Recalcular fitness
            calculate_multi_vehicle_fitness(optimized_solution, depot_location)
            
            # Verificar se eliminou cruzamentos
            new_crossings = count_route_crossings(optimized_solution.vehicles)
            if new_crossings == 0:
                print(f"✓ Cruzamentos eliminados! Novo fitness: {optimized_solution.total_fitness:.2f}")
            else:
                print(f"⚠️  Ainda restam {new_crossings} cruzamentos após otimização")
            
            # Atualizar população com solução otimizada
            population[0] = optimized_solution
            
            # Se a solução otimizada for MELHOR que a melhor global, atualizar
            if optimized_solution.total_fitness < best_fitness:
                best_solution = copy.deepcopy(optimized_solution)
                best_fitness = optimized_solution.total_fitness
                last_improvement_generation = generation
                stagnation_counter = 0
        
        # ============================================================================
        # OTIMIZAÇÃO 2-OPT ADAPTATIVA: Aplicar periodicamente baseado na geração
        # ============================================================================
        should_apply_2opt = False
        
        if generation <= OPT2_EARLY_THRESHOLD:
            # Fase inicial (0-100): a cada 5 gerações
            should_apply_2opt = (generation % OPT2_INTERVAL_EARLY == 0)
        elif generation <= OPT2_MID_THRESHOLD:
            # Fase média (100-300): a cada 15 gerações
            should_apply_2opt = (generation % OPT2_INTERVAL_MID == 0)
        else:
            # Fase tardia (300+): a cada 30 gerações
            should_apply_2opt = (generation % OPT2_INTERVAL_LATE == 0)
        
        if should_apply_2opt and generation > 0:
            print(f"🔧 Geração {generation}: Aplicando otimização 2-opt nas top 3 soluções...")
            
            # Aplicar 2-opt nas 3 melhores soluções
            for i in range(min(3, len(population))):
                for vehicle in population[i].vehicles:
                    if vehicle.route:
                        vehicle.route = two_opt_optimize(vehicle.route, depot_location, max_passes=2)
                calculate_multi_vehicle_fitness(population[i], depot_location)
            
            # Reordenar população
            population = sort_multi_vehicle_population(population)
            
            # Se a melhor da população for MELHOR que a melhor global, atualizar
            if population[0].total_fitness < best_fitness:
                best_solution = copy.deepcopy(population[0])
                best_fitness = population[0].total_fitness
                last_improvement_generation = generation
                stagnation_counter = 0
        
        # ============================================================================
        # REINJEÇÃO DE DIVERSIDADE PROGRESSIVA: Detectar estagnação
        # ============================================================================
        if stagnation_counter >= STAGNATION_THRESHOLD:
            # Calcular taxa de injeção baseada no tempo de estagnação
            stagnation_severity = min(stagnation_counter / (STAGNATION_THRESHOLD * 3), 1.0)
            injection_rate = DIVERSITY_INJECTION_MIN + (DIVERSITY_INJECTION_MAX - DIVERSITY_INJECTION_MIN) * stagnation_severity
            
            print(f"🔄 Geração {generation}: Estagnação detectada ({stagnation_counter} gerações)!")
            print(f"   Injetando {injection_rate*100:.0f}% de diversidade na população...")
            
            # Calcular elite_size atual
            if MAX_GENERATIONS > 0:
                progress = generation / MAX_GENERATIONS
                current_elite_size = int(ELITE_SIZE_INITIAL + (ELITE_SIZE_FINAL - ELITE_SIZE_INITIAL) * progress)
            else:
                current_elite_size = (ELITE_SIZE_INITIAL + ELITE_SIZE_FINAL) // 2
            
            # Injetar diversidade
            population = inject_diversity(population, service_points, depot_location, injection_rate, current_elite_size)
            
            # Resetar contador parcialmente (não completamente para evitar loops)
            stagnation_counter = STAGNATION_THRESHOLD // 2
        
        # ============================================================================
        # GERAÇÃO GUIADA: Após muita estagnação, gerar soluções das melhores
        # ============================================================================
        if stagnation_counter >= GUIDED_GENERATION_THRESHOLD:
            print(f"🎯 Geração {generation}: Estagnação severa ({stagnation_counter} gerações)!")
            print(f"   Gerando soluções guiadas a partir das top {GUIDED_TOP_SOLUTIONS}...")
            
            # Gerar novas soluções guiadas
            top_solutions = population[:GUIDED_TOP_SOLUTIONS]
            guided_solutions = generate_guided_solutions(top_solutions, depot_location, num_solutions=20)
            
            # Substituir piores soluções por guiadas
            population = population[:POPULATION_SIZE - 20] + guided_solutions
            population = sort_multi_vehicle_population(population)
            
            # Resetar contador
            stagnation_counter = 0
            print(f"   ✓ Soluções guiadas geradas e inseridas na população")
        
        # Salvar progresso para Streamlit
        with open(progress_file, 'wb') as f:
            pickle.dump({
                'generation': generation,
                'best_fitness': best_fitness,
                'fitness_history': best_fitness_history
            }, f)
        
        draw_info_panel(screen, generation, best_solution, elapsed_time, last_improvement_generation)
        
        if len(best_fitness_history) > 1:
            draw_simple_plot(screen, list(range(len(best_fitness_history))), best_fitness_history, best_fitness, last_improvement_generation)
        
        draw_best_solution(screen, best_solution, best_fitness)
        
        # Ordem de desenho (rotas primeiro, pontos depois cobrem as linhas):
        # 1. Top 5 soluções da população (linhas cinza claro finas)
        # Mostra as soluções sendo calculadas em tempo real
        # Só desaparece na tela final (quando finished=True)
        if not finished:
            # Desenhar soluções aleatórias da população para maior diversidade visual
            # IMPORTANTE: Desenhar AMBOS os veículos de cada solução
            # Usar amostragem aleatória ao invés de sempre as mesmas top soluções
            num_to_draw = min(15, len(population))  # Aumentado para 15
            if num_to_draw > 1:
                # Pegar índices aleatórios (excluindo a melhor que é índice 0)
                import random
                random_indices = random.sample(range(1, len(population)), min(num_to_draw - 1, len(population) - 1))
                for i in random_indices:
                    solution = population[i]
                    # Desenhar TODOS os veículos da solução (não apenas um)
                    for vehicle in solution.vehicles:
                        if vehicle.route:  # Verificar se o veículo tem rota
                            draw_vehicle_route(screen, vehicle.route, vehicle.vehicle_id, depot_location, draw_light_gray=True)
        
        # 2. Camada de prioridade: linhas finas coloridas com setas
        for vehicle in best_solution.vehicles:
            draw_vehicle_route(screen, vehicle.route, vehicle.vehicle_id, depot_location, draw_priority_colors=True)
        
        # 3. Camada de veículo: linhas grossas verde/ciano com setas
        for vehicle in best_solution.vehicles:
            draw_vehicle_route(screen, vehicle.route, vehicle.vehicle_id, depot_location, draw_priority_colors=False)
        
        # 4. Pontos de atendimento (cobrem as linhas que entram nos círculos)
        draw_service_points(screen, service_points, NODE_RADIUS)
        
        # 5. Depósito por último
        draw_depot(screen, depot_location)
        
        # Imprimir os dados da melhor solução a cada geração para monitoramento
        print(f"Geração {generation}: Fitness = {best_fitness:.2f}")
        for vehicle in best_solution.vehicles:
            hours = int(vehicle.total_time // 60)
            minutes = int(vehicle.total_time % 60)
            distance_km = vehicle.total_distance * 0.1
            print(f"  Veículo {vehicle.vehicle_id}: {len(vehicle.route)} pontos, "
                    f"Dist={distance_km:.1f} km, Tempo={hours}h{minutes:02d}")
    
        # ============================================================================
        # CALCULAR DIVERSIDADE GENÉTICA E AJUSTAR MUTAÇÃO
        # ============================================================================
        diversity = calculate_population_diversity(population)
        diversity_adjustment = calculate_diversity_adjustment(diversity)
        
        # ============================================================================
        # ELITISMO DINÂMICO: aumenta ao longo das gerações (5 -> 10)
        # ============================================================================
        if MAX_GENERATIONS > 0:
            progress = generation / MAX_GENERATIONS
            elite_size = int(ELITE_SIZE_INITIAL + (ELITE_SIZE_FINAL - ELITE_SIZE_INITIAL) * progress)
        else:
            # Modo infinito: usar elitismo médio
            elite_size = (ELITE_SIZE_INITIAL + ELITE_SIZE_FINAL) // 2
        
        # ============================================================================
        # MUTAÇÃO DINÂMICA COM AJUSTE DE DIVERSIDADE: (70% -> 20%) * ajuste
        # ============================================================================
        if MAX_GENERATIONS > 0:
            base_mutation_rate = MUTATION_RATE_INITIAL - (MUTATION_RATE_INITIAL - MUTATION_RATE_FINAL) * progress
        else:
            # Modo infinito: usar taxa média
            base_mutation_rate = (MUTATION_RATE_INITIAL + MUTATION_RATE_FINAL) / 2
        
        # Aplicar ajuste baseado em diversidade
        mutation_rate = base_mutation_rate * diversity_adjustment
        mutation_rate = max(0.1, min(0.9, mutation_rate))  # Limitar entre 10% e 90%
        
        # ============================================================================
        # SIMULATED ANNEALING: Atualizar temperatura
        # ============================================================================
        if MAX_GENERATIONS > 0:
            # Temperatura diminui linearmente
            temperature = INITIAL_TEMPERATURE - (INITIAL_TEMPERATURE - FINAL_TEMPERATURE) * progress
        else:
            # Modo infinito: resfriamento exponencial
            temperature = max(FINAL_TEMPERATURE, temperature * COOLING_RATE)
        
        # ============================================================================
        # CRIAR NOVA POPULAÇÃO COM ELITISMO GARANTIDO
        # ============================================================================
        new_population = []
        
        # PASSO 1: SEMPRE copiar a melhor solução global primeiro (elitismo garantido)
        new_population.append(copy.deepcopy(best_solution))
        
        # PASSO 2: Copiar elite adicional da população ordenada (se elite_size > 1)
        for i in range(1, elite_size):
            new_population.append(copy.deepcopy(population[i]))
        
        # PASSO 3: Aplicar Simulated Annealing em cópias da elite (não substitui a elite)
        num_annealing = max(1, elite_size // 5)
        for i in range(num_annealing):
            annealed = apply_simulated_annealing(copy.deepcopy(population[i]), temperature, depot_location)
            new_population.append(annealed)
        
        # PASSO 3: Gerar resto da população por crossover e mutação
        while len(new_population) < POPULATION_SIZE:
            # Torneio adaptativo: menor no início, MAIOR no final
            # Início (3): Torneio pequeno → Aceita soluções variadas → Explora espaço
            # Final (7): Torneio grande → SEMPRE escolhe os melhores → Muta ótimos para achar ainda melhores
            if MAX_GENERATIONS > 0:
                if generation < MAX_GENERATIONS * TOURNAMENT_EARLY_THRESHOLD:
                    tournament_size = TOURNAMENT_SIZE_LATE  # Início: 3 (explora mais)
                elif generation < MAX_GENERATIONS * TOURNAMENT_MID_THRESHOLD:
                    tournament_size = TOURNAMENT_SIZE_MID  # Meio: 5 (equilíbrio)
                else:
                    tournament_size = TOURNAMENT_SIZE_EARLY  # Final: 7 (refina ótimos)
            else:
                # Modo infinito: usar tamanho médio
                tournament_size = TOURNAMENT_SIZE_MID
            
            tournament = random.sample(population, min(tournament_size, len(population)))
            tournament = sort_multi_vehicle_population(tournament)
            
            parent1 = tournament[0]
            parent2 = tournament[1] if len(tournament) > 1 else tournament[0]
            
            child = multi_vehicle_crossover(parent1, parent2, depot_location, service_points)
            
            # Aplicar mutação com taxa DINÂMICA
            child = multi_vehicle_mutate(child, depot_location, mutation_rate, service_points)
            
            new_population.append(child)
        
        population = new_population
        
        # Só incrementar geração se não terminou
        if not finished:
            generation += 1
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    print("="*60)
    print("SISTEMA DE ROTEAMENTO COM 2 VEÍCULOS + DEPÓSITO")
    print("="*60)
    print("\nControles:")
    print("  Q ou ESC - Sair")
    print("  R - Reiniciar com novos pontos")
    print("\nObjetivo:")
    print("  - Veículos partem e retornam ao depósito (D)")
    print("  - Pontos prioritários (EME, VIO, MED, POS) até 12h")
    print("  - Pontos regulares (REG) após 12h")
    print("  - Todos os 20 pontos em 1 dia")
    print("\nVisualização:")
    print("  - Linhas finas coloridas: prioridade de cada entrega")
    print("  - Linhas grossas verde/ciano: veículo responsável")
    print("  - Círculo 'D' amarelo: depósito (origem/destino)")
    print("\n" + "="*60)
    print("Iniciando visualização...\n")
    
    main()

"""
Visualização do Algoritmo Genético com Restrições usando Pygame
Mostra rotas de atendimento com prioridades e restrições em tempo real
VERSÃO COM MÚLTIPLOS VEÍCULOS (2 veículos) + DEPÓSITO
"""

import pygame
from pygame.locals import *
import random
import sys
import numpy as np
from src.core.multi_vehicle import (
    generate_multi_vehicle_population,
    calculate_multi_vehicle_fitness,
    multi_vehicle_crossover,
    multi_vehicle_mutate,
    sort_multi_vehicle_population,
    MultiVehicleSolution
)
from src.core.service_points import create_service_point, ServicePriority, calculate_distance

# Constantes
WIDTH, HEIGHT = 1400, 800
NODE_RADIUS = 12
FPS = 10

# Áreas da tela
INFO_PANEL_WIDTH = 350
MAP_X_START = INFO_PANEL_WIDTH + 20
MAP_WIDTH = WIDTH - MAP_X_START - 20
MAP_HEIGHT = HEIGHT - 20

PLOT_X_START = 10
PLOT_Y_START = 500  # Movido mais para baixo
PLOT_WIDTH = INFO_PANEL_WIDTH - 20
PLOT_HEIGHT = 150  # Reduzido para dar espaço

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (220, 220, 220)
DARK_GREEN = (0, 150, 0)
CYAN = (0, 200, 200)

# Cores por prioridade
PRIORITY_COLORS = {
    ServicePriority.EMERGENCY_OBSTETRIC: RED,
    ServicePriority.DOMESTIC_VIOLENCE: ORANGE,
    ServicePriority.HORMONAL_MEDICATION: BLUE,
    ServicePriority.POSTPARTUM_CARE: PURPLE,
    ServicePriority.REGULAR: GRAY
}

# Cores por veículo
VEHICLE_COLORS = {
    1: DARK_GREEN,  # Veículo 1: Verde escuro
    2: CYAN         # Veículo 2: Ciano
}

# Parâmetros do AG
N_POINTS = 20
NUM_VEHICLES = 2
POPULATION_SIZE = 150       # Aumentado de 100 para 150 para mais diversidade
MUTATION_PROBABILITY = 0.5  # Ajustado de 0.6 para 0.5 (equilíbrio entre exploração e convergência)
VEHICLE_SPEED = 60.0        # Velocidade dos veículos em km/h


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


def draw_info_panel(screen, generation, best_solution):
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
        f"Fitness Total: {best_solution.total_fitness:.2f}",
    ]
    
    for text in info_texts:
        rendered = font_text.render(text, True, BLACK)
        screen.blit(rendered, (x_start, y_start))
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
    
    priority_abbr = {
        ServicePriority.EMERGENCY_OBSTETRIC: "EME",
        ServicePriority.DOMESTIC_VIOLENCE: "VIO",
        ServicePriority.HORMONAL_MEDICATION: "MED",
        ServicePriority.POSTPARTUM_CARE: "POS",
        ServicePriority.REGULAR: "REG"
    }
    
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


def draw_simple_plot(screen, x_data, y_data, best_fitness=None):
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
    
    priority_abbr = {
        ServicePriority.EMERGENCY_OBSTETRIC: "EME",
        ServicePriority.DOMESTIC_VIOLENCE: "VIO",
        ServicePriority.HORMONAL_MEDICATION: "MED",
        ServicePriority.POSTPARTUM_CARE: "POS",
        ServicePriority.REGULAR: "REG"
    }
    
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
    
    # Desenhar rotas (3 camadas)
    node_radius = 8
    
    # 1. Camada de prioridade
    for vehicle in best_solution.vehicles:
        if not vehicle.route:
            continue
        depot_pos = transform(depot_location)
        first_pos = transform(vehicle.route[0].location)
        
        first_color = PRIORITY_COLORS.get(vehicle.route[0].priority, GRAY)
        pygame.draw.line(screen, first_color, depot_pos, first_pos, 1)
        
        for i in range(len(vehicle.route) - 1):
            start_pos = transform(vehicle.route[i].location)
            end_pos = transform(vehicle.route[i + 1].location)
            line_color = PRIORITY_COLORS.get(vehicle.route[i + 1].priority, GRAY)
            pygame.draw.line(screen, line_color, start_pos, end_pos, 1)
        
        last_pos = transform(vehicle.route[-1].location)
        pygame.draw.line(screen, GRAY, last_pos, depot_pos, 1)
    
    # 2. Camada de veículo
    for vehicle in best_solution.vehicles:
        if not vehicle.route:
            continue
        vehicle_color = VEHICLE_COLORS.get(vehicle.vehicle_id, GREEN)
        depot_pos = transform(depot_location)
        first_pos = transform(vehicle.route[0].location)
        
        pygame.draw.line(screen, vehicle_color, depot_pos, first_pos, 2)
        
        for i in range(len(vehicle.route) - 1):
            start_pos = transform(vehicle.route[i].location)
            end_pos = transform(vehicle.route[i + 1].location)
            pygame.draw.line(screen, vehicle_color, start_pos, end_pos, 2)
        
        last_pos = transform(vehicle.route[-1].location)
        pygame.draw.line(screen, vehicle_color, last_pos, depot_pos, 2)
    
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
    
    types_guaranteed = [
        'emergency', 'emergency',
        'violence', 'violence',
        'medication', 'medication',
        'postpartum', 'postpartum'
    ]
    
    for i, service_type in enumerate(types_guaranteed):
        while True:
            location = (
                random.randint(MAP_X_START + NODE_RADIUS + 80, WIDTH - NODE_RADIUS - 20),
                random.randint(NODE_RADIUS + 20, HEIGHT - NODE_RADIUS - 20)
            )
            if calculate_distance(depot_location, location) > 100:
                break
        
        time_window = None
        if service_type == 'violence':
            time_window = (480, 600)
        elif service_type == 'postpartum':
            time_window = (540, 660)
        
        point = create_service_point(i + 1, location, service_type, time_window)
        service_points.append(point)
    
    for i in range(len(types_guaranteed), n_points):
        while True:
            location = (
                random.randint(MAP_X_START + NODE_RADIUS + 80, WIDTH - NODE_RADIUS - 20),
                random.randint(NODE_RADIUS + 20, HEIGHT - NODE_RADIUS - 20)
            )
            if calculate_distance(depot_location, location) > 100:
                break
        
        point = create_service_point(i + 1, location, 'regular', None)
        service_points.append(point)
    
    return depot_location, service_points


def main(max_generations=10):
    import pickle
    import time
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Roteamento Multi-Veículo com Depósito - AG")
    clock = pygame.time.Clock()
    
    depot_location, service_points = create_depot_and_service_points(N_POINTS)
    population = generate_multi_vehicle_population(service_points, depot_location, POPULATION_SIZE, NUM_VEHICLES)
    
    best_fitness_history = []
    generation = 0
    MAX_GENERATIONS = max_generations  # Parâmetro configurável
    finished = False  # Flag para controlar estado final
    screenshot_saved = False  # Flag para salvar screenshot apenas uma vez
    
    # Arquivos para comunicação com Streamlit
    temp_dir = '/tmp'
    progress_file = f'{temp_dir}/progress.pkl'
    screenshot_file = f'{temp_dir}/pygame_final.png'
    
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
        if generation >= MAX_GENERATIONS and not finished:
            # Imprimir no console (apenas uma vez)
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
        
        # Se terminou, mostrar frame final, salvar dados e fechar após 2 segundos
        if finished:
            # Desenhar tela final
            draw_final_solution_frame(screen, best_solution, best_fitness, generation, depot_location, service_points)
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
        
        screen.fill(WHITE)
        
        population = sort_multi_vehicle_population(population)
        
        best_solution = population[0]
        best_fitness = best_solution.total_fitness
        
        # Debug: mostrar melhoria
        if generation == 0:
            print(f"\n{'='*60}")
            print(f"FITNESS INICIAL: {best_fitness:.2f}")
            print(f"{'='*60}\n")
        elif generation > 0 and best_fitness < best_fitness_history[-1]:
            improvement = best_fitness_history[-1] - best_fitness
            print(f"✓ Geração {generation}: MELHORIA de {improvement:.2f} (Fitness: {best_fitness:.2f})")
        
        best_fitness_history.append(best_fitness)
        
        # Salvar progresso para Streamlit
        with open(progress_file, 'wb') as f:
            pickle.dump({
                'generation': generation,
                'best_fitness': best_fitness,
                'fitness_history': best_fitness_history
            }, f)
        
        draw_info_panel(screen, generation, best_solution)
        
        if len(best_fitness_history) > 1:
            draw_simple_plot(screen, list(range(len(best_fitness_history))), best_fitness_history, best_fitness)
        
        draw_best_solution(screen, best_solution, best_fitness)
        
        # Ordem de desenho (rotas primeiro, pontos depois cobrem as linhas):
        # 1. Segunda melhor solução (linhas cinza claro finas) - Sempre durante otimização
        # Só desaparece na tela final (quando finished=True)
        if len(population) > 1 and not finished:
            second_best = population[1]
            for vehicle in second_best.vehicles:
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
    
        # Criar nova população com Elitismo forte e Torneio adaptativo
        elite_size = 10  # 10 para preservar mais soluções boas
        new_population = population[:elite_size]
        
        while len(new_population) < POPULATION_SIZE:
            # Torneio adaptativo: maior no início, menor no final
            if generation < MAX_GENERATIONS * 0.3:
                tournament_size = 7  # Início: pressão seletiva alta
            elif generation < MAX_GENERATIONS * 0.7:
                tournament_size = 5  # Meio: pressão moderada
            else:
                tournament_size = 3  # Final: mais diversidade
            
            tournament = random.sample(population, min(tournament_size, len(population)))
            tournament = sort_multi_vehicle_population(tournament)
            
            parent1 = tournament[0]
            parent2 = tournament[1] if len(tournament) > 1 else tournament[0]
            
            child = multi_vehicle_crossover(parent1, parent2, depot_location)
            
            # Aplicar mutação com probabilidade configurada
            child = multi_vehicle_mutate(child, depot_location, MUTATION_PROBABILITY)
            
            new_population.append(child)
        
        population = new_population
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

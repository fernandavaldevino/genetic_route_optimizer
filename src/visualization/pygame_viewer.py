"""
Visualização do Algoritmo Genético com Restrições usando Pygame
Mostra rotas de atendimento com prioridades e restrições em tempo real
"""

import pygame
from pygame.locals import *
import random
import sys
import numpy as np
from src.core.genetic_algorithm import (
    calculate_constrained_fitness,
    generate_priority_aware_population,
    sort_population_by_fitness,
    constrained_order_crossover,
    constrained_mutate,
    calculate_route_time_and_distance
)
from src.core.service_points import create_service_point, ServicePriority
from src.constants import (
    WIDTH, HEIGHT, NODE_RADIUS, FPS,
    INFO_PANEL_WIDTH, MAP_X_START, MAP_WIDTH, MAP_HEIGHT,
    PLOT_X_START, PLOT_Y_START, PLOT_WIDTH, PLOT_HEIGHT,
    WHITE, BLACK, RED, BLUE, GREEN, ORANGE, PURPLE, YELLOW, GRAY, LIGHT_GRAY,
    PRIORITY_COLORS,
    N_POINTS, POPULATION_SIZE, MUTATION_PROBABILITY, MAX_GENERATIONS, VEHICLE_SPEED,
    MAP_COORD_MIN_X, MAP_COORD_MAX_X, MAP_COORD_MIN_Y, MAP_COORD_MAX_Y,
    GUARANTEED_SERVICE_TYPES, VIOLENCE_TIME_WINDOW, POSTPARTUM_TIME_WINDOW,
    PRIORITY_ABBREVIATIONS, MINUTES_PER_DAY, WORK_START_TIME, WORK_END_TIME
)

def draw_service_points(screen, service_points, radius, start_points_by_day=None):
    """
    Desenha pontos de atendimento com cores baseadas na prioridade
    
    Args:
        screen: Superfície do Pygame
        service_points: Lista de todos os pontos
        radius: Raio dos círculos
        start_points_by_day: Dict {dia: point_id} para destacar pontos iniciais de cada dia
    """
    for point in service_points:
        # Depósito (ID=0) é desenhado em amarelo
        if point.id == 0:
            color = YELLOW
        else:
            color = PRIORITY_COLORS.get(point.priority, GRAY)
        
        pygame.draw.circle(screen, color, point.location, radius)
        pygame.draw.circle(screen, BLACK, point.location, radius, 2)
        
        # Destacar pontos iniciais de cada dia (exceto depósito)
        if start_points_by_day and point.id != 0:
            if 1 in start_points_by_day and point.id == start_points_by_day[1]:
                # Dia 1: círculo preto mais grosso
                pygame.draw.circle(screen, BLACK, point.location, radius + 3, 5)
            elif 2 in start_points_by_day and point.id == start_points_by_day[2]:
                # Dia 2: círculo verde escuro mais grosso
                pygame.draw.circle(screen, (0, 100, 0), point.location, radius + 3, 5)
            elif point.id in start_points_by_day.values():
                # Outros dias: círculo azul escuro
                pygame.draw.circle(screen, (0, 0, 139), point.location, radius + 3, 5)
        
        # Desenhar ID do ponto ou "D" para depósito
        font = pygame.font.Font(None, 20)
        if point.id == 0:
            text = font.render("D", True, BLACK)  # "D" em preto para depósito
        else:
            text = font.render(str(point.id), True, WHITE)
        text_rect = text.get_rect(center=point.location)
        screen.blit(text, text_rect)


def draw_route(screen, route, color=None, width=2, use_priority_colors=True):
    """
    Desenha a rota conectando os pontos
    
    Args:
        screen: Superfície do Pygame
        route: Lista de pontos da rota
        color: Cor única para toda a rota (se None e use_priority_colors=False, usa verde)
        width: Largura da linha
        use_priority_colors: Se True, usa cores baseadas na prioridade do ponto de destino (default: True)
    """
    if len(route) < 2:
        return
    
    for i in range(len(route) - 1):  # Não fechar o loop
        start_pos = route[i].location
        end_pos = route[i + 1].location
        
        if use_priority_colors:
            # Usar cor baseada na prioridade do ponto de destino
            dest_point = route[i + 1]
            # Se destino for depósito, usar verde
            if dest_point.id == 0:
                line_color = GREEN
            else:
                line_color = PRIORITY_COLORS.get(dest_point.priority, GRAY)
        else:
            # Usar cor única
            line_color = color if color else GREEN
        
        pygame.draw.line(screen, line_color, start_pos, end_pos, width)


def calculate_days_message(arrival_times):
    """ Calcula o dia e horário da última entrega """
    if arrival_times and len(arrival_times) > 0:
        # Calcular o dia da última entrega - arrival_time (antes do retorno ao depósito)
        last_service_arrival = arrival_times[-1]
        max_day = int(last_service_arrival // MINUTES_PER_DAY) + 1
        
        # Calcular horário da última entrega
        time_of_day = last_service_arrival % MINUTES_PER_DAY
        hours = int(time_of_day // 60)
        minutes = int(time_of_day % 60)
        time_str = f"{hours:02d}:{minutes:02d}"
        
        if max_day == 1:
            return "1 dia", (0, 150, 0), time_str           # Verde
        elif max_day == 2:
            return "2 dias", (204, 85, 0), time_str         # Laranja escuro
        else:
            return f"{max_day} dias", (200, 0, 0), time_str  # Vermelho
    else:
        return "calculando...", BLACK, "00:00"


def draw_info_panel(screen, generation, best_fitness, best_route, arrival_times):
    """ Desenha painel de informações no lado esquerdo """
    # Fundo do painel
    pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, INFO_PANEL_WIDTH, HEIGHT))
    pygame.draw.line(screen, BLACK, (INFO_PANEL_WIDTH, 0), (INFO_PANEL_WIDTH, HEIGHT), 2)
    
    font_title = pygame.font.Font(None, 26)
    font_text = pygame.font.Font(None, 18)
    
    x_start = 10
    y_start = 10
    line_height = 22
    
    # Título
    title = font_title.render("Otimização de Rotas com Restrições", True, BLACK)
    screen.blit(title, (x_start, y_start))
    y_start += 35
    
    # # Calcular mensagem de dias (sem horário)
    # days_text, days_color, _ = calculate_days_message(arrival_times)
    
    # Informações gerais
    info_texts = [
        f"Geração: {generation}",
        f"Fitness: {best_fitness:.2f}",
    ]
    
    for text in info_texts:
        rendered = font_text.render(text, True, BLACK)
        screen.blit(rendered, (x_start, y_start))
        y_start += line_height
    
    y_start += 10
    
    # Ordem de Prioridades para Atendimento
    legend_title = font_text.render("Ordem de Prioridades para Atendimento:", True, BLACK)
    screen.blit(legend_title, (x_start, y_start))
    y_start += line_height + 5
    
    # Encontrar IDs de cada prioridade na rota
    priority_ids = {
        ServicePriority.EMERGENCY_OBSTETRIC: [],
        ServicePriority.DOMESTIC_VIOLENCE: [],
        ServicePriority.HORMONAL_MEDICATION: [],
        ServicePriority.POSTPARTUM_CARE: [],
        ServicePriority.REGULAR: []
    }
    
    for point in best_route:
        priority_ids[point.priority].append(point.id)
    
    # Ordenar IDs
    for priority in priority_ids:
        priority_ids[priority].sort()
    
    # Formatar ranges de IDs
    def format_id_range(ids, use_dots=False):
        if not ids:
            return "()"
        elif len(ids) == 1:
            return f"({ids[0]})"
        else:
            # Filtrar o 0 (depósito) se estiver presente
            filtered_ids = [id for id in ids if id != 0]
            if not filtered_ids:
                return "()"
            elif len(filtered_ids) == 1:
                return f"({filtered_ids[0]})"
            else:
                if use_dots:
                    return f"({filtered_ids[0]} ... {filtered_ids[-1]})"
                else:
                    return f"({filtered_ids[0]}, {filtered_ids[-1]})"
    
    legend_items = [
        ("Emergência Obstétrica (EME)", RED, ServicePriority.EMERGENCY_OBSTETRIC, False),
        ("Violência Doméstica (VIO)", ORANGE, ServicePriority.DOMESTIC_VIOLENCE, False),
        ("Medicamento Hormonal (MED)", BLUE, ServicePriority.HORMONAL_MEDICATION, False),
        ("Pós-Parto (POS)", PURPLE, ServicePriority.POSTPARTUM_CARE, False),
        ("Regular (REG)", GRAY, ServicePriority.REGULAR, True),  # Usar dots para Regular
    ]
    
    for label, color, priority, use_dots in legend_items:
        # Desenhar círculo de cor
        pygame.draw.circle(screen, color, (x_start + 8, y_start + 8), 7)
        pygame.draw.circle(screen, BLACK, (x_start + 8, y_start + 8), 7, 1)
        
        # Texto da prioridade
        id_range = format_id_range(priority_ids[priority], use_dots)
        text = font_text.render(f"{label} - {id_range}", True, BLACK)
        screen.blit(text, (x_start + 22, y_start))
        y_start += line_height
    
    y_start += 10
    
    # Ordem de atendimento em 2 colunas
    order_title = font_text.render("Ordem de Atendimento:", True, BLACK)
    screen.blit(order_title, (x_start, y_start))
    y_start += line_height + 5
    
    # Usar abreviações de prioridade das constantes
    priority_abbr = PRIORITY_ABBREVIATIONS
    
    # Calcular retorno ao depósito
    depot = best_route[0]
    last_point = best_route[-1]
    from src.core.service_points import calculate_travel_time
    return_travel_time = calculate_travel_time(last_point.location, depot.location, VEHICLE_SPEED)
    return_arrival = arrival_times[-1] + last_point.service_duration + return_travel_time
    
    # Verificar se retorno passa das 18h
    return_time_of_day = return_arrival % MINUTES_PER_DAY
    if return_time_of_day >= WORK_END_TIME:  # 18h
        return_day = int(return_arrival // MINUTES_PER_DAY)
        return_arrival = (return_day + 1) * MINUTES_PER_DAY + WORK_START_TIME  # Próximo dia às 8h
    
    # Configuração das colunas
    col1_x = x_start + 5
    col2_x = x_start + 185
    y_col_start = y_start
    
    # Total de itens: saída do depósito + pontos de atendimento + retorno ao depósito
    total_items = len(best_route) + 1  # +1 para o retorno
    
    # Calcular quantos itens por coluna (coluna esquerda tem 1 a mais se ímpar)
    items_col1 = (total_items + 1) // 2     # Arredonda para cima
    items_col2 = total_items - items_col1
    
    # Desenhar em 2 colunas balanceadas
    for i in range(total_items):
        if i < len(best_route):
            # Pontos da rota (incluindo saída do depósito)
            point = best_route[i]
            arrival = arrival_times[i]
        else:
            # Retorno ao depósito
            point = depot
            arrival = return_arrival
        
        # Calcular dia e hora do dia
        day = int(arrival // MINUTES_PER_DAY) + 1  # Dia 1, 2, 3, etc.
        time_of_day = arrival % MINUTES_PER_DAY
        hours = int(time_of_day // 60)
        minutes = int(time_of_day % 60)
        
        abbr = priority_abbr.get(point.priority, "???")
        
        # Determinar coluna e posição Y
        if i < items_col1:
            # Coluna 1
            x_pos = col1_x
            y_pos = y_col_start + (i * 17)
        else:
            # Coluna 2
            x_pos = col2_x
            y_pos = y_col_start + ((i - items_col1) * 17)
        
        # Renderizar texto em partes para colorir o indicador de dia
        # Parte 1: número, ID e horário (preto)
        if point.id == 0:
            # Depósito
            text_part1 = f"{i+1}. D-DEP ({hours:02d}:{minutes:02d}, "
        else:
            # Ponto normal
            text_part1 = f"{i+1}. P{point.id}-{abbr} ({hours:02d}:{minutes:02d}, "
        
        rendered_part1 = font_text.render(text_part1, True, BLACK)
        screen.blit(rendered_part1, (x_pos, y_pos))
        x_offset = rendered_part1.get_width()
        
        # Parte 2: indicador de dia (colorido)
        day_text = f"D{day}"
        
        # Verificar se é medicamento prioritário (EME, VIO, MED, POS)
        is_priority_med = point.priority in [
            ServicePriority.EMERGENCY_OBSTETRIC,
            ServicePriority.DOMESTIC_VIOLENCE,
            ServicePriority.HORMONAL_MEDICATION,
            ServicePriority.POSTPARTUM_CARE
        ]
        
        # Cores por dia
        if day == 1:
            day_color = BLACK  # Dia 1: preto (normal)
        elif day >= 2 and is_priority_med:
            # Medicamento prioritário no Dia 2+: VERMELHO
            day_color = (200, 0, 0)
        elif day == 2:
            day_color = (0, 100, 0)  # Dia 2 regular: verde escuro
        else:
            day_color = (0, 0, 139)  # Dia 3+ regular: azul escuro
        
        rendered_day = font_text.render(day_text, True, day_color)
        screen.blit(rendered_day, (x_pos + x_offset, y_pos))
        x_offset += rendered_day.get_width()
        
        # Parte 3: parêntese de fechamento
        text_part3 = ")"
        rendered_part3 = font_text.render(text_part3, True, BLACK)
        screen.blit(rendered_part3, (x_pos + x_offset, y_pos))
        
        # Se for depósito, adicionar identificador (Saída/Retorno)
        if point.id == 0:
            if i == 0:
                # Saída do depósito - mesma linha
                x_offset += rendered_part3.get_width()
                text_saida = " (Saída)"
                rendered_saida = font_text.render(text_saida, True, BLACK)
                screen.blit(rendered_saida, (x_pos + x_offset, y_pos))
            elif i >= len(best_route):
                # Retorno ao depósito - nova linha abaixo
                text_retorno = "(Retorno)"
                rendered_retorno = font_text.render(text_retorno, True, BLACK)
                # Posicionar abaixo, com indentação
                screen.blit(rendered_retorno, (x_pos + 20, y_pos + 12))


def draw_simple_plot(screen, x_data, y_data, best_route=None, best_fitness=None, arrival_times=None):
    """ Desenha gráfico com eixos e valores """
    if len(x_data) < 2:
        return
    
    margin_left = 60
    margin_bottom = 25
    margin_top = 25
    margin_right = 10
    
    plot_x = PLOT_X_START + margin_left
    plot_y = PLOT_Y_START + margin_top
    plot_w = PLOT_WIDTH - margin_left - margin_right
    plot_h = PLOT_HEIGHT - margin_top - margin_bottom - 5
    
    # Fundo do gráfico
    pygame.draw.rect(screen, WHITE, (PLOT_X_START, PLOT_Y_START, PLOT_WIDTH, PLOT_HEIGHT))
    pygame.draw.rect(screen, BLACK, (plot_x, plot_y, plot_w, plot_h), 2)
    
    # Normalizar dados
    min_y = min(y_data)
    max_y = max(y_data)
    range_y = max_y - min_y if max_y != min_y else 1
    max_x = len(x_data) - 1
    
    # Desenhar linha do gráfico
    points = []
    margin_top_graph = 5
    margin_bottom_graph = 15
    for i, (x, y) in enumerate(zip(x_data, y_data)):
        px = plot_x + int((i / max_x) * plot_w)
        py = plot_y + margin_top_graph + int(((y - min_y) / range_y) * (plot_h - margin_top_graph - margin_bottom_graph))
        py = plot_y + plot_h - py + plot_y  # Inverter Y para gráfico
        points.append((px, py))
    
    if len(points) > 1:
        pygame.draw.lines(screen, BLUE, False, points, 2)
    
    # Fontes
    font_title = pygame.font.Font(None, 16)
    font_axis = pygame.font.Font(None, 12)
    
    # Título
    title = font_title.render("Evolução do Fitness", True, BLACK)
    screen.blit(title, (PLOT_X_START + 5, PLOT_Y_START + 5))
    
    # Valores do eixo Y (fitness)
    y_labels = [min_y, (min_y + max_y) / 2, max_y]
    for i, val in enumerate(y_labels):
        y_pos = plot_y + plot_h - int((i / 2) * plot_h)
        label = font_axis.render(f"{val:.0f}", True, BLACK)
        screen.blit(label, (PLOT_X_START + 25, y_pos - 6))
    
    # Label do eixo Y
    y_label = font_axis.render("Fitness", True, BLACK)
    y_label_rotated = pygame.transform.rotate(y_label, 90)
    y_label_rect = y_label_rotated.get_rect(center=(PLOT_X_START + 12, plot_y + plot_h // 2))
    screen.blit(y_label_rotated, y_label_rect)
    
    # Valores do eixo X (gerações)
    x_labels = [0, max_x // 2, max_x]
    for i, val in enumerate(x_labels):
        x_pos = plot_x + int((i / 2) * plot_w)
        label = font_axis.render(str(val), True, BLACK)
        label_rect = label.get_rect(center=(x_pos, plot_y + plot_h + 15))
        screen.blit(label, label_rect)
    
    # Label do eixo X
    x_label = font_axis.render("Geração", True, BLACK)
    x_label_rect = x_label.get_rect(center=(plot_x + plot_w // 2, plot_y + plot_h + 20))
    screen.blit(x_label, x_label_rect)
    
    # Melhor solução abaixo do gráfico
    if best_route and best_fitness is not None:
        font_title = pygame.font.Font(None, 16)
        font_solution = pygame.font.Font(None, 15)
        font_fitness = pygame.font.Font(None, 16)
        y_below = PLOT_Y_START + PLOT_HEIGHT + 5
        
        # Título
        text_title = font_title.render("Melhor Solução:", True, BLACK)
        screen.blit(text_title, (PLOT_X_START + 5, y_below))
        y_below += 18
        
        # Desenhar vetor com cores por prioridade (excluindo depósito)
        x_pos = PLOT_X_START + 5
        y_pos = y_below
        
        # Desenhar colchete de abertura
        bracket_open = font_solution.render("[ ", True, BLACK)
        screen.blit(bracket_open, (x_pos, y_pos))
        x_pos += bracket_open.get_width()
        
        # Filtrar pontos sem o depósito
        route_without_depot = [p for p in best_route if p.id != 0]
        
        # Desenhar cada ID com sua cor de prioridade
        for i, point in enumerate(route_without_depot):
            # Cor baseada na prioridade
            color = PRIORITY_COLORS.get(point.priority, BLACK)
            
            # Texto do ID
            id_text = str(point.id)
            id_rendered = font_solution.render(id_text, True, color)
            
            # Verificar se precisa quebrar linha (largura máxima ~320px)
            if x_pos + id_rendered.get_width() > PLOT_X_START + PLOT_WIDTH - 15:
                y_pos += 16
                x_pos = PLOT_X_START + 10  # Indentação para linhas continuadas
            
            screen.blit(id_rendered, (x_pos, y_pos))
            x_pos += id_rendered.get_width()
            
            # Adicionar vírgula e espaço (exceto no último)
            if i < len(route_without_depot) - 1:
                comma = font_solution.render(", ", True, BLACK)
                screen.blit(comma, (x_pos, y_pos))
                x_pos += comma.get_width()
        
        # Desenhar colchete de fechamento
        bracket_close = font_solution.render(" ]", True, BLACK)
        screen.blit(bracket_close, (x_pos, y_pos))
        
        # Fitness
        y_below = y_pos + 20
        text_fitness = font_fitness.render(f"Fitness: {best_fitness:.2f}", True, BLACK)
        screen.blit(text_fitness, (PLOT_X_START + 5, y_below))
        
        # Texto de dias necessários
        y_below += 25
        
        # Linha 1: "Entrega dos medicamentos estimada em até"
        font_delivery = pygame.font.Font(None, 18)
        text_delivery = "Entrega dos medicamentos estimada em até"
        rendered_delivery = font_delivery.render(text_delivery, True, BLACK)
        # Centralizar na largura do painel
        x_centered = PLOT_X_START + (PLOT_WIDTH - rendered_delivery.get_width()) // 2
        screen.blit(rendered_delivery, (x_centered, y_below))
        
        # Linha 2: número de dias + horário
        y_below += 22
        font_days = pygame.font.Font(None, 28)
        days_text, days_color, time_str = calculate_days_message(arrival_times)
        
        # Combinar dias e horário
        full_text = f"{days_text}, às {time_str}."
        rendered_days = font_days.render(full_text, True, days_color)
        # Centralizar
        x_centered_days = PLOT_X_START + (PLOT_WIDTH - rendered_days.get_width()) // 2
        screen.blit(rendered_days, (x_centered_days, y_below))


def draw_completion_screen(screen, generation, best_fitness, best_route, arrival_times, service_points):
    """ Desenha tela de conclusão da otimização mostrando vetor único com cores """
    screen.fill(WHITE)
    
    # Fontes
    font_title = pygame.font.Font(None, 48)
    font_subtitle = pygame.font.Font(None, 32)
    font_text = pygame.font.Font(None, 24)
    font_solution = pygame.font.Font(None, 22)
    font_small = pygame.font.Font(None, 18)
    
    # Calcular informações da rota
    total_distance, total_time, _ = calculate_route_time_and_distance(best_route)
    
    # Calcular número máximo de dias
    max_day = 1
    if arrival_times and len(arrival_times) > 0:
        last_arrival = arrival_times[-1]
        max_day = int(last_arrival // MINUTES_PER_DAY) + 1
    
    # Lado esquerdo - Informações textuais
    left_x = 50
    y_pos = 50
    
    # Título principal
    title = font_title.render("OTIMIZAÇÃO CONCLUÍDA!", True, (0, 150, 0))
    screen.blit(title, (left_x, y_pos))
    y_pos += 70
    
    # Informações gerais
    info_texts = [
        (f"Gerações: {generation}", BLACK),
        (f"Fitness: {best_fitness:.2f}", BLACK),
    ]
    
    for text, color in info_texts:
        rendered = font_subtitle.render(text, True, color)
        screen.blit(rendered, (left_x, y_pos))
        y_pos += 40
    
    y_pos += 20
    
    # Melhor Solução - Vetor único com cores (excluindo depósito)
    solution_title = font_subtitle.render("Melhor Solução:", True, BLACK)
    screen.blit(solution_title, (left_x, y_pos))
    y_pos += 45
    
    # Desenhar vetor com IDs coloridos por prioridade (excluindo depósito)
    x_pos = left_x
    y_vec = y_pos
    
    # Colchete de abertura com espaço
    bracket_open = font_solution.render("[ ", True, BLACK)
    screen.blit(bracket_open, (x_pos, y_vec))
    x_pos += bracket_open.get_width()
    
    # Filtrar pontos sem o depósito
    route_without_depot = [p for p in best_route if p.id != 0]
    
    # Desenhar cada ID com sua cor de prioridade
    for i, point in enumerate(route_without_depot):
        # Cor baseada na prioridade
        color = PRIORITY_COLORS.get(point.priority, BLACK)
        
        # Texto do ID
        id_text = str(point.id)
        id_rendered = font_solution.render(id_text, True, color)
        
        # Verificar se precisa quebrar linha
        if x_pos + id_rendered.get_width() > WIDTH - 100:
            y_vec += 28
            x_pos = left_x + 15  # Indentação
        
        screen.blit(id_rendered, (x_pos, y_vec))
        x_pos += id_rendered.get_width()
        
        # Adicionar vírgula e espaço (exceto no último)
        if i < len(route_without_depot) - 1:
            comma = font_solution.render(", ", True, BLACK)
            screen.blit(comma, (x_pos, y_vec))
            x_pos += comma.get_width()
    
    # Colchete de fechamento com espaço
    bracket_close = font_solution.render(" ]", True, BLACK)
    screen.blit(bracket_close, (x_pos, y_vec))
    
    y_pos = y_vec + 45
    
    # Fitness
    text_fitness = font_text.render(f"Fitness: {best_fitness:.2f}", True, BLACK)
    screen.blit(text_fitness, (left_x, y_pos))
    y_pos += 35
    
    # Entrega dos medicamentos estimada em X dias, às hh:mm
    x_pos = left_x
    text_part1 = "Entrega dos medicamentos estimada em até "
    rendered_part1 = font_text.render(text_part1, True, BLACK)
    screen.blit(rendered_part1, (x_pos, y_pos))
    x_pos += rendered_part1.get_width()
    
    # Calcular horário da última entrega
    if arrival_times and len(arrival_times) > 0:
        last_service_arrival = arrival_times[-1]  # Última entrega antes do retorno
        time_of_day = last_service_arrival % MINUTES_PER_DAY
        hours = int(time_of_day // 60)
        minutes = int(time_of_day % 60)
        time_str = f"{hours:02d}:{minutes:02d}"
    else:
        time_str = "00:00"
    
    # Número de dias colorido + horário
    if max_day == 1:
        days_text = f"1 dia, às {time_str}."
        days_color = (0, 150, 0)
    elif max_day == 2:
        days_text = f"2 dias, às {time_str}."
        days_color = (255, 140, 0)  # Laranja
    else:
        days_text = f"{max_day} dias, às {time_str}."
        days_color = (200, 0, 0)
    
    font_days = pygame.font.Font(None, 26)
    rendered_days = font_days.render(days_text, True, days_color)
    screen.blit(rendered_days, (x_pos, y_pos - 2))
    
    y_pos += 50
    
    # Ordem de Atendimento (detalhada)
    order_title = font_text.render("Ordem de Atendimento:", True, BLACK)
    screen.blit(order_title, (left_x, y_pos))
    y_pos += 30
    
    # Usar abreviações de prioridade das constantes
    priority_abbr = PRIORITY_ABBREVIATIONS
    
    # Mostrar ordem de atendimento em 2 colunas
    col1_x = left_x + 10
    col2_x = left_x + 300
    y_col_start = y_pos
    
    # Calcular retorno ao depósito
    depot = best_route[0]  # Depósito é sempre o primeiro
    last_point = best_route[-1]
    
    # Calcular tempo de retorno ao depósito
    from src.core.service_points import calculate_travel_time
    return_travel_time = calculate_travel_time(last_point.location, depot.location, VEHICLE_SPEED)
    return_arrival = arrival_times[-1] + last_point.service_duration + return_travel_time
    
    # Verificar se retorno passa das 18h
    return_time_of_day = return_arrival % MINUTES_PER_DAY
    if return_time_of_day >= WORK_END_TIME:  # 18h
        return_day = int(return_arrival // MINUTES_PER_DAY)
        return_arrival = (return_day + 1) * MINUTES_PER_DAY + WORK_START_TIME  # Próximo dia às 8h
    
    # Número total de itens (rota + retorno)
    total_items = len(best_route) + 1
    
    for i in range(min(total_items, 22)):  # Até 22 para incluir retorno
        if i < len(best_route):
            # Pontos da rota
            point = best_route[i]
            arrival = arrival_times[i]
        else:
            # Retorno ao depósito
            point = depot
            arrival = return_arrival
        
        # Calcular dia e hora
        day = int(arrival // MINUTES_PER_DAY) + 1
        time_of_day = arrival % MINUTES_PER_DAY
        hours = int(time_of_day // 60)
        minutes = int(time_of_day % 60)
        
        # Determinar coluna
        if i < 11:
            x_pos_col = col1_x
            y_item = y_col_start + (i * 20)
        else:
            x_pos_col = col2_x
            y_item = y_col_start + ((i - 11) * 20)
        
        # Verificar se é medicamento prioritário no Dia 2+
        is_priority_med = point.priority in [
            ServicePriority.EMERGENCY_OBSTETRIC,
            ServicePriority.DOMESTIC_VIOLENCE,
            ServicePriority.HORMONAL_MEDICATION,
            ServicePriority.POSTPARTUM_CARE
        ]
        use_red = (day >= 2 and is_priority_med and point.id != 0)
        
        # Renderizar número em preto
        number_text = f"{i+1}. "
        rendered_number = font_small.render(number_text, True, BLACK)
        screen.blit(rendered_number, (x_pos_col, y_item))
        x_offset = rendered_number.get_width()
        
        # Formatar resto do texto
        if point.id == 0:
            abbr = "DEP"
            rest_text = f"D-{abbr} ("
        else:
            abbr = priority_abbr.get(point.priority, "???")
            rest_text = f"P{point.id}-{abbr} ("
        
        # Renderizar resto em vermelho se necessário
        text_color = (200, 0, 0) if use_red else BLACK
        rendered_rest = font_small.render(rest_text, True, text_color)
        screen.blit(rendered_rest, (x_pos_col + x_offset, y_item))
        x_offset += rendered_rest.get_width()
        
        # Renderizar horário (mesma cor)
        time_text = f"{hours:02d}:{minutes:02d}, "
        rendered_time = font_small.render(time_text, True, text_color)
        screen.blit(rendered_time, (x_pos_col + x_offset, y_item))
        x_offset += rendered_time.get_width()
        
        # Renderizar dia colorido
        day_text = f"D{day}"
        if day == 1:
            day_color = BLACK
        elif day == 2:
            day_color = (0, 100, 0)  # Verde escuro
        else:
            day_color = (0, 0, 139)  # Azul escuro
        
        rendered_day = font_small.render(day_text, True, day_color)
        screen.blit(rendered_day, (x_pos_col + x_offset, y_item))
        x_offset += rendered_day.get_width()
        
        # Renderizar parêntese de fechamento
        close_paren = font_small.render(")", True, BLACK)
        screen.blit(close_paren, (x_pos_col + x_offset, y_item))
        x_offset += close_paren.get_width()
        
        # Se for depósito, adicionar identificador (Saída/Retorno) após o horário
        if point.id == 0:
            if i == 0:
                # Saída do depósito
                text_saida = " (Saída)"
                rendered_saida = font_small.render(text_saida, True, BLACK)
                screen.blit(rendered_saida, (x_pos_col + x_offset, y_item))
            elif i >= len(best_route):
                # Retorno ao depósito
                text_retorno = " (Retorno)"
                rendered_retorno = font_small.render(text_retorno, True, BLACK)
                screen.blit(rendered_retorno, (x_pos_col + x_offset, y_item))
    
    # Instruções para sair e reiniciar
    exit_text = font_small.render("Pressione Q ou ESC para sair  |  Pressione R para reiniciar", True, GRAY)
    screen.blit(exit_text, (left_x, HEIGHT - 50))
    
    # Lado direito - Visualização do mapa
    map_x_start = 650
    map_y_start = 50
    map_width = WIDTH - map_x_start - 50
    map_height = HEIGHT - 100
    
    # Desenhar borda do mapa
    pygame.draw.rect(screen, BLACK, (map_x_start, map_y_start, map_width, map_height), 3)
    
    # Escalar pontos para caber no mapa do lado direito
    all_x = [p.location[0] for p in service_points]
    all_y = [p.location[1] for p in service_points]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    margin = 30
    scale_x = (map_width - 2 * margin) / (max_x - min_x) if max_x != min_x else 1
    scale_y = (map_height - 2 * margin) / (max_y - min_y) if max_y != min_y else 1
    scale = min(scale_x, scale_y)
    
    def transform_point(location):
        x = map_x_start + margin + (location[0] - min_x) * scale
        y = map_y_start + margin + (location[1] - min_y) * scale
        return (int(x), int(y))
    
    # Desenhar linhas da rota coloridas por prioridade
    for i in range(len(best_route) - 1):
        start_pos = transform_point(best_route[i].location)
        end_pos = transform_point(best_route[i+1].location)
        
        # Cor baseada na prioridade do ponto de destino
        dest_point = best_route[i + 1]
        dest_arrival = arrival_times[i + 1]
        dest_day = int(dest_arrival // MINUTES_PER_DAY) + 1
        
        # Verificar se é medicamento prioritário no Dia 2+
        is_priority_med = dest_point.priority in [
            ServicePriority.EMERGENCY_OBSTETRIC,
            ServicePriority.DOMESTIC_VIOLENCE,
            ServicePriority.HORMONAL_MEDICATION,
            ServicePriority.POSTPARTUM_CARE
        ]
        
        if dest_point.id == 0:
            line_color = GREEN  # Verde para depósito
        elif dest_day >= 2 and is_priority_med:
            line_color = (200, 0, 0)  # Vermelho para medicamento prioritário no Dia 2+
        else:
            line_color = PRIORITY_COLORS.get(dest_point.priority, GRAY)
        
        pygame.draw.line(screen, line_color, start_pos, end_pos, 3)
    
    # Desenhar linha de retorno ao depósito em cinza
    if len(best_route) > 0:
        last_point_pos = transform_point(best_route[-1].location)
        depot_pos = transform_point(best_route[0].location)
        pygame.draw.line(screen, GRAY, last_point_pos, depot_pos, 3)
    
    # Desenhar pontos
    for point in best_route:
        # Depósito (ID 0) é desenhado em amarelo
        if point.id == 0:
            color = YELLOW
        else:
            color = PRIORITY_COLORS.get(point.priority, GRAY)
        
        pos = transform_point(point.location)
        pygame.draw.circle(screen, color, pos, 10)
        pygame.draw.circle(screen, BLACK, pos, 10, 2)
        
        # Desenhar ID ou "D" para depósito
        font_id = pygame.font.Font(None, 16)
        if point.id == 0:
            text = font_id.render("D", True, BLACK)  # "D" em preto para depósito
        else:
            text = font_id.render(str(point.id), True, WHITE)
        text_rect = text.get_rect(center=pos)
        screen.blit(text, text_rect)


def create_random_service_points(n_points):
    """ Cria pontos de atendimento aleatórios com diferentes tipos, incluindo depósito """
    service_points = []
    
    # Criar DEPÓSITO (ponto D/0) - ponto de partida em amarelo
    depot_location = (
        random.randint(MAP_COORD_MIN_X, MAP_COORD_MAX_X),
        random.randint(MAP_COORD_MIN_Y, MAP_COORD_MAX_Y)
    )
    depot = create_service_point(0, depot_location, 'regular', None)
    depot.service_duration = 0.0  # Depósito não tem tempo de serviço
    service_points.append(depot)
    
    # Garantir 2 atendimentos de cada tipo prioritário
    for i, service_type in enumerate(GUARANTEED_SERVICE_TYPES):
        location = (
            random.randint(MAP_COORD_MIN_X, MAP_COORD_MAX_X),
            random.randint(MAP_COORD_MIN_Y, MAP_COORD_MAX_Y)
        )
        
        # Definir janelas de tempo específicas (4h para 1 veículo)
        time_window = None
        if service_type == 'violence':
            time_window = VIOLENCE_TIME_WINDOW
        elif service_type == 'postpartum':
            time_window = POSTPARTUM_TIME_WINDOW
        
        point = create_service_point(i + 1, location, service_type, time_window)
        service_points.append(point)
    
    # Adicionar apenas pontos REGULARES no restante para garantir que as prioridades sejam sempre respeitadas
    for i in range(len(GUARANTEED_SERVICE_TYPES), n_points):
        location = (
            random.randint(MAP_COORD_MIN_X, MAP_COORD_MAX_X),
            random.randint(MAP_COORD_MIN_Y, MAP_COORD_MAX_Y)
        )
        
        service_type = 'regular'  # Apenas regulares
        
        point = create_service_point(i + 1, location, service_type, None)
        service_points.append(point)
    
    return service_points


def main():
    # Inicializar Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Roteamento com Restricoes - AG")
    clock = pygame.time.Clock()
    
    # Criar pontos de atendimento
    service_points = create_random_service_points(N_POINTS)
    
    # Criar população inicial
    population = generate_priority_aware_population(service_points, POPULATION_SIZE)
    
    best_fitness_history = []
    generation = 0
    optimization_complete = False
    
    # Loop principal
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Reiniciar com novos pontos
                    service_points = create_random_service_points(N_POINTS)
                    population = generate_priority_aware_population(service_points, POPULATION_SIZE)
                    best_fitness_history = []
                    generation = 0
                    optimization_complete = False
        
        # Verificar se atingiu o critério de parada
        if generation >= MAX_GENERATIONS and not optimization_complete:
            optimization_complete = True
            print(f"\n{'='*60}")
            print(f"OTIMIZAÇÃO CONCLUÍDA EM {generation} GERAÇÕES!")
            print(f"Fitness final: {best_fitness:.2f}")
            print(f"{'='*60}\n")
        
        # Se otimização completa, mostrar tela de conclusão
        if optimization_complete:
            draw_completion_screen(screen, generation, best_fitness, best_route, arrival_times, service_points)
            pygame.display.flip()
            clock.tick(FPS)
            
            # Processar eventos na tela de conclusão
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        # Reiniciar: criar novos pontos e resetar otimização
                        service_points = create_random_service_points(N_POINTS)
                        population = generate_priority_aware_population(service_points, POPULATION_SIZE)
                        best_fitness_history = []
                        generation = 0
                        optimization_complete = False
            continue
        
        # Limpar tela
        screen.fill(WHITE)
        
        # Calcular fitness (1 veículo: deadline = fim do Dia 1)
        fitness_values = [calculate_constrained_fitness(route, speed=VEHICLE_SPEED, priority_deadline=MINUTES_PER_DAY) for route in population]
        
        # Ordenar população
        population, fitness_values = sort_population_by_fitness(population, fitness_values)
        
        best_fitness = fitness_values[0]
        best_route = population[0]
        
        best_fitness_history.append(best_fitness)
        
        # Calcular tempos de chegada
        _, _, arrival_times = calculate_route_time_and_distance(best_route)
        
        # Desenhar painel de informações (esquerda)
        draw_info_panel(screen, generation, best_fitness, best_route, arrival_times)
        
        # Desenhar gráfico de evolução (parte inferior esquerda)
        if len(best_fitness_history) > 1:
            draw_simple_plot(
                screen,
                list(range(len(best_fitness_history))),
                best_fitness_history,
                best_route,
                best_fitness,
                arrival_times
            )
        
        # Desenhar segunda melhor rota primeiro (mais clara, sem cores de prioridade)
        if len(population) > 1:
            draw_route(screen, population[1], color=(200, 200, 200), width=1, use_priority_colors=False)
        
        # Desenhar melhor rota com cores de prioridade
        draw_route(screen, best_route, width=4, use_priority_colors=True)
        
        # Desenhar linha de retorno ao depósito em cinza
        if len(best_route) > 1:
            last_point = best_route[-1]
            depot = best_route[0]
            pygame.draw.line(screen, GRAY, last_point.location, depot.location, 4)
        
        # Identificar pontos iniciais de cada dia
        start_points_by_day = {}
        if best_route and arrival_times:
            current_day = 1
            start_points_by_day[current_day] = best_route[0].id
            
            for i in range(1, len(best_route)):
                day = int(arrival_times[i] // MINUTES_PER_DAY) + 1
                if day > current_day:
                    start_points_by_day[day] = best_route[i].id
                    current_day = day
        
        # Desenhar pontos de atendimento POR ÚLTIMO para ficarem sobre as linhas
        draw_service_points(screen, service_points, NODE_RADIUS, start_points_by_day=start_points_by_day)
        
        # Imprimir informações no console a cada geração
        print(f"Geração {generation}: Fitness = {best_fitness:.2f}")
        
        # Verificar se todos os pontos estão na rota (apenas a cada 50 gerações para não poluir)
        if generation % 50 == 0:
            route_ids = set(p.id for p in best_route)
            all_ids = set(p.id for p in service_points)
            if route_ids != all_ids:
                print(f"  AVISO: Pontos faltando na rota! Esperados: {all_ids}, Na rota: {route_ids}")
        
        # Criar nova população
        new_population = [population[0]]  # Elitismo
        
        while len(new_population) < POPULATION_SIZE:
            # Seleção por torneio
            tournament_size = 5
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament = [(population[i], fitness_values[i]) for i in tournament_indices]
            tournament.sort(key=lambda x: x[1])
            
            parent1 = tournament[0][0]
            parent2 = tournament[1][0]
            
            # Crossover
            child = constrained_order_crossover(parent1, parent2)
            
            # Mutação
            child = constrained_mutate(child, MUTATION_PROBABILITY)
            
            new_population.append(child)
        
        population = new_population
        generation += 1
        
        # Atualizar display
        pygame.display.flip()
        clock.tick(FPS)
    
    # Finalizar
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    print("="*60)
    print("SISTEMA DE ROTEAMENTO COM RESTRICOES")
    print("="*60)
    print("\nControles:")
    print("  Q ou ESC - Sair")
    print("  R - Reiniciar com novos pontos")
    print("\nLegenda de Cores:")
    print("  Vermelho - Emergencia Obstetrica (prioridade maxima)")
    print("  Laranja - Violencia Domestica (protocolo especial)")
    print("  Azul - Medicamento Hormonal (temperatura controlada)")
    print("  Roxo - Pos-Parto (janela de tempo especifica)")
    print("  Cinza - Atendimento Regular")
    print("\n" + "="*60)
    print("Iniciando visualizacao...\n")
    
    main()

#!/usr/bin/env python3
"""
Interface Gráfica com Streamlit para o Sistema de Otimização de Rotas

Autor: Fernanda Valdevino - Projeto Fase 2
"""

# Suprimir mensagem de boas-vindas do pygame
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import streamlit as st
import sys
import os
import random
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import multiprocessing
import pickle
import time
from PIL import Image

# Adicionar src ao path (ajustar para a nova estrutura de pastas)
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.core.genetic_algorithm import (
    calculate_constrained_fitness,
    generate_priority_aware_population,
    sort_population_by_fitness,
    constrained_order_crossover,
    constrained_mutate,
    calculate_route_time_and_distance
)
from src.core.service_points import create_service_point, ServicePriority
from src.llm.utils.streamlit_integration import LLMIntegration
from src.constants import (
    N_POINTS, POPULATION_SIZE, MUTATION_PROBABILITY,
    PRIORITY_COLORS_HEX as PRIORITY_COLORS,
    PRIORITY_COLORS_STREAMLIT, PRIORITY_ABBREVIATIONS, PRIORITY_NAMES,
    COORD_MIN_X, COORD_MAX_X, COORD_MIN_Y, COORD_MAX_Y,
    GUARANTEED_SERVICE_TYPES, VIOLENCE_TIME_WINDOW, POSTPARTUM_TIME_WINDOW,
    VEHICLE_COLORS_HEX, MINUTES_PER_DAY, DISTANCE_TO_KM_FACTOR, SPEED_KM_PER_MIN,
    TEMP_DIR, SERVICE_POINTS_FILE, PROGRESS_FILE, SCREENSHOT_FILE, DEPOT_FILE
)

# Configuração da página
st.set_page_config(
    page_title="Otimizador de Rotas - AG",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

def create_random_service_points(n_points):
    """ Cria pontos de atendimento aleatórios com diferentes tipos """
    service_points = []
    
    depot_location = (
        random.randint(COORD_MIN_X, COORD_MAX_X),
        random.randint(COORD_MIN_Y, COORD_MAX_Y)
    )
    depot = create_service_point(0, depot_location, 'regular', None)
    depot.service_duration = 0.0
    service_points.append(depot)
    
    for i, service_type in enumerate(GUARANTEED_SERVICE_TYPES):
        location = (
            random.randint(COORD_MIN_X, COORD_MAX_X),
            random.randint(COORD_MIN_Y, COORD_MAX_Y)
        )
        
        time_window = None
        if service_type == 'violence':
            time_window = VIOLENCE_TIME_WINDOW
        elif service_type == 'postpartum':
            time_window = POSTPARTUM_TIME_WINDOW
        
        point = create_service_point(i + 1, location, service_type, time_window)
        service_points.append(point)
    
    for i in range(len(GUARANTEED_SERVICE_TYPES), n_points):
        location = (
            random.randint(COORD_MIN_X, COORD_MAX_X),
            random.randint(COORD_MIN_Y, COORD_MAX_Y)
        )
        point = create_service_point(i + 1, location, 'regular', None)
        service_points.append(point)
    
    return service_points

def format_time(minutes):
    """ Formata minutos em HH:MM """
    hours = int(minutes // 60) % 24
    mins = int(minutes % 60)
    return f"{hours:02d}:{mins:02d}"

def get_day_from_minutes(minutes):
    """ Retorna o dia a partir dos minutos """
    return int(minutes // MINUTES_PER_DAY) + 1

def run_pygame_2_vehicles(service_points_file, progress_file, screenshot_file, depot_location, max_generations):
    """ Executa visualização com 2 veículos - chama main_2v.py integrado """
    import subprocess
    import sys
    
    # Caminho para o main_2v.py do projeto (agora na pasta app)
    main_2v_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'main_2v.py')
    
    # Executar o main_2v.py passando max_generations como argumento
    print(f"\n{'='*60}")
    print("EXECUTANDO OTIMIZAÇÃO COM 2 VEÍCULOS")
    print(f"{'='*60}\n")
    
    result = subprocess.run(
        [sys.executable, main_2v_path, str(max_generations)],
        cwd=os.path.dirname(__file__),
        capture_output=False
    )
    
    print(f"\n{'='*60}")
    print("OTIMIZAÇÃO COM 2 VEÍCULOS FINALIZADA")
    print(f"{'='*60}\n")
    
    # NÃO sobrescrever os dados - o pygame_viewer_2v.py já salvou tudo corretamente
    # Os dados estão em progress_file e screenshot_file


def run_pygame_with_full_visualization(service_points_file, progress_file, screenshot_file, max_generations):
    """ Executa visualização completa do Pygame (1 veículo) """
    import sys
    import os
    
    # Configurar sys.path para o processo filho
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    src_path = os.path.join(project_root, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Importar módulo completo do pygame_viewer
    from src.visualization import pygame_viewer
    from src.core.genetic_algorithm import (
        calculate_constrained_fitness,
        generate_priority_aware_population,
        sort_population_by_fitness,
        constrained_order_crossover,
        constrained_mutate,
        calculate_route_time_and_distance
    )
    import pygame
    import pickle
    import random
    import time
    
    # Constantes necessárias
    POPULATION_SIZE = 100
    MUTATION_PROBABILITY = 0.5
    
    # Carregar pontos
    with open(service_points_file, 'rb') as f:
        service_points = pickle.load(f)
    
    # Carregar velocidade
    speed_file = os.path.join('/tmp', 'vehicle_speed.pkl')
    if os.path.exists(speed_file):
        with open(speed_file, 'rb') as f:
            vehicle_speed = pickle.load(f)
    else:
        vehicle_speed = 60  # Valor padrão
    
    # Prints informativos iniciais
    print("="*60)
    print("SISTEMA DE ROTEAMENTO COM 1 VEÍCULO")
    print("="*60)
    print(f"\nGerações: {max_generations}")
    print("\nControles:")
    print("  Q ou ESC - Sair")
    print("  R - Reiniciar com novos pontos")
    print("\nObjetivo:")
    print("  - Veículo parte e retorna ao depósito (D)")
    print("  - Pontos prioritários (EME, VIO, MED, POS) até o 1º dia")
    print("  - Pontos regulares (REG) após prioridades")
    print("  - Todos os 20 pontos")
    print("\nVisualização:")
    print("  - Linhas finas coloridas: prioridade de cada entrega")
    print("  - Linha grossa: rota do veículo")
    print("  - Círculo 'D' amarelo: depósito (origem/destino)")
    print("\n" + "="*60)
    print("Iniciando visualização...\n")
    
    # Executar visualização completa (código do pygame_viewer.py adaptado)
    pygame.init()
    WIDTH, HEIGHT = 1400, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Roteamento com Restricoes - AG")
    clock = pygame.time.Clock()
    FPS = 10
    
    print("Gerando população: 0% com 2-opt (máxima diversidade inicial)\n")
    
    # Criar população inicial
    population = generate_priority_aware_population(service_points, POPULATION_SIZE)
    
    best_fitness_history = []
    generation = 0
    optimization_complete = False
    last_improvement_generation = 0
    start_time = pygame.time.get_ticks() / 1000.0
    first_fitness_printed = False
    
    # Loop principal
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False
        
        # Verificar se atingiu o critério de parada
        if generation > max_generations and not optimization_complete:
            optimization_complete = True
            
            # Print final
            print()
            print("="*60)
            print(f"CRITÉRIO DE PARADA ATINGIDO: {max_generations} gerações")
            print("="*60)
            
            # Calcular métricas finais
            total_distance, total_time, _ = calculate_route_time_and_distance(best_route, speed=vehicle_speed)
            distance_km = total_distance * 0.1
            hours = int(total_time // 60)
            minutes = int(total_time % 60)
            num_points = len([p for p in best_route if p.id != 0])
            
            print(f"Melhor Fitness Final: {best_fitness:.2f}")
            print(f"  Veículo: {num_points} pontos, Dist={distance_km:.1f} km, Tempo={hours}h{minutes:02d}")
            print("="*60)
            print()
            
            # Salvar screenshot final
            pygame.image.save(screen, screenshot_file)
            print(f"Screenshot salvo em: {screenshot_file}")
            print(f"Dados salvos em: {progress_file}")
        
        # Se otimização completa, mostrar tela de conclusão
        if optimization_complete:
            # Desenhar tela de conclusão
            from src.visualization.pygame_viewer import draw_completion_screen
            draw_completion_screen(screen, max_generations, best_fitness, best_route, arrival_times, service_points)
            pygame.display.flip()
            
            # Salvar screenshot final
            pygame.image.save(screen, screenshot_file)
            
            # Aguardar um pouco antes de fechar
            print("Fechando em 2 segundos...")
            print()
            time.sleep(2)
            running = False
            continue
        
        # Limpar tela
        screen.fill((255, 255, 255))
        
        # Calcular fitness
        fitness_values = [calculate_constrained_fitness(route, speed=vehicle_speed) for route in population]
        
        # Ordenar população
        population, fitness_values = sort_population_by_fitness(population, fitness_values)
        
        best_fitness = fitness_values[0]
        best_route = population[0]
        
        # Detectar melhoria (considerar melhoria se for pelo menos 0.1% melhor)
        if generation == 0:
            best_fitness_history.append(best_fitness)
            last_improvement_generation = 0
        elif best_fitness < best_fitness_history[-1] * 0.999:
            best_fitness_history.append(best_fitness)
            last_improvement_generation = generation
        else:
            best_fitness_history.append(best_fitness)
        
        # Calcular tempos de chegada
        _, _, arrival_times = calculate_route_time_and_distance(best_route, speed=vehicle_speed)
        
        # Calcular tempo decorrido
        elapsed_time = pygame.time.get_ticks() / 1000.0 - start_time
        
        # Print do fitness inicial (apenas uma vez)
        if not first_fitness_printed:
            print("="*60)
            print(f"FITNESS INICIAL: {best_fitness:.2f}")
            print("="*60)
            print()
            first_fitness_printed = True
        
        # Print a cada geração
        if generation == 0 or generation % 1 == 0:
            # Calcular distância e tempo
            total_distance, total_time, _ = calculate_route_time_and_distance(best_route, speed=vehicle_speed)
            distance_km = total_distance * 0.1
            hours = int(total_time // 60)
            minutes = int(total_time % 60)
            num_points = len([p for p in best_route if p.id != 0])
            
            print(f"Geração {generation}: Fitness = {best_fitness:.2f}")
            print(f"  Veículo: {num_points} pontos, Dist={distance_km:.1f} km, Tempo={hours}h{minutes:02d}")
            print()
        
        # Desenhar visualização completa
        from src.visualization.pygame_viewer import (
            draw_info_panel, draw_simple_plot, draw_route,
            draw_service_points, NODE_RADIUS
        )
        
        # Desenhar painel de informações
        draw_info_panel(screen, generation, best_fitness, best_route, arrival_times, elapsed_time, last_improvement_generation)
        
        # Desenhar gráfico de evolução
        if len(best_fitness_history) > 1:
            draw_simple_plot(
                screen,
                list(range(len(best_fitness_history))),
                best_fitness_history,
                best_route,
                best_fitness,
                arrival_times,
                last_improvement_generation
            )
        
        # Desenhar segunda melhor rota
        if len(population) > 1:
            draw_route(screen, population[1], color=(200, 200, 200), width=1, use_priority_colors=False)
        
        # Desenhar melhor rota
        draw_route(screen, best_route, width=4, use_priority_colors=True)
        
        # Desenhar linha de retorno
        if len(best_route) > 1:
            last_point = best_route[-1]
            depot = best_route[0]
            pygame.draw.line(screen, (128, 128, 128), last_point.location, depot.location, 4)
        
        # Identificar pontos iniciais de cada dia
        start_points_by_day = {}
        if best_route and arrival_times:
            current_day = 1
            start_points_by_day[current_day] = best_route[0].id
            
            for i in range(1, len(best_route)):
                day = int(arrival_times[i] // 1440) + 1
                if day > current_day:
                    start_points_by_day[day] = best_route[i].id
                    current_day = day
        
        # Desenhar pontos
        draw_service_points(screen, service_points, NODE_RADIUS, start_points_by_day=start_points_by_day)
        
        # Salvar progresso para Streamlit
        with open(progress_file, 'wb') as f:
            pickle.dump({
                'generation': generation,
                'best_fitness': best_fitness,
                'fitness_history': best_fitness_history
            }, f)
        
        # Criar nova população
        new_population = [population[0]]
        
        while len(new_population) < POPULATION_SIZE:
            tournament_size = 5
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament = [(population[i], fitness_values[i]) for i in tournament_indices]
            tournament.sort(key=lambda x: x[1])
            
            parent1 = tournament[0][0]
            parent2 = tournament[1][0]
            
            child = constrained_order_crossover(parent1, parent2)
            child = constrained_mutate(child, MUTATION_PROBABILITY)
            
            new_population.append(child)
        
        population = new_population
        generation += 1
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Salvar resultados finais
    with open(progress_file, 'wb') as f:
        pickle.dump({
            'generation': generation,
            'best_fitness': best_fitness,
            'fitness_history': best_fitness_history,
            'best_route': best_route,
            'arrival_times': arrival_times,
            'completed': True
        }, f)
    
    pygame.quit()

def display_results(best_route, best_fitness, arrival_times, route_json=None):
    """ Exibe os resultados da otimização """
    
    from src.core.service_points import calculate_distance
    
    # Agrupar pontos por dia usando detecção de mudança de horário
    points_by_day = {}
    current_day = 1
    previous_time_mins = None
    
    for i, point in enumerate(best_route):
        if point.id == 0:
            continue
        
        # Converter arrival_time para horário do dia (0-1439)
        time_mins = arrival_times[i] % 1440
        
        # Detectar mudança de dia (horário volta para trás)
        if previous_time_mins is not None and time_mins < previous_time_mins:
            current_day += 1
        
        if current_day not in points_by_day:
            points_by_day[current_day] = []
        points_by_day[current_day].append((point, time_mins))
        
        previous_time_mins = time_mins
    
    max_day = max(points_by_day.keys()) if points_by_day else 1
    
    # Calcular distância por dia e distância total
    distance_by_day = {}
    depot = best_route[0]
    sorted_days = sorted(points_by_day.keys())
    total_distance_km = 0.0
    
    # Calcular distâncias
    for day_idx, day in enumerate(sorted_days):
        day_distance = 0
        day_points = points_by_day[day]
        
        if day_points:
            # Primeiro dia: sai do depósito
            if day_idx == 0:
                day_distance += calculate_distance(depot.location, day_points[0][0].location)
            else:
                # Dias seguintes: continua do último ponto do dia anterior
                prev_day = sorted_days[day_idx - 1]
                last_point_prev_day = points_by_day[prev_day][-1][0]
                day_distance += calculate_distance(last_point_prev_day.location, day_points[0][0].location)
            
            # Distâncias entre pontos do dia
            for j in range(len(day_points) - 1):
                day_distance += calculate_distance(day_points[j][0].location, day_points[j+1][0].location)
            
            # Último dia: volta ao depósito
            if day_idx == len(sorted_days) - 1:
                day_distance += calculate_distance(day_points[-1][0].location, depot.location)
        
        distance_by_day[day] = day_distance * 0.1
        total_distance_km += distance_by_day[day]
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Fitness Total", f"{best_fitness:.2f}")
    
    with col2:
        total_points = len([p for p in best_route if p.id != 0])
        st.metric("Total de Pontos", total_points)
    
    with col3:
        st.metric("Distância Total", f"{total_distance_km:.1f} km")
    
    with col4:
        # Calcular tempo total: somar tempo de trabalho de cada dia
        total_time_minutes = 0
        for day in sorted(points_by_day.keys()):
            day_points = points_by_day[day]
            if day_points:
                first_arrival = day_points[0][1]  # Já em minutos do dia (0-1439)
                last_arrival = day_points[-1][1]
                last_duration = day_points[-1][0].service_duration
                # Tempo de trabalho do dia
                day_time = (last_arrival - first_arrival) + last_duration
                total_time_minutes += day_time
        
        total_time_hours = total_time_minutes / 60.0
        st.metric("Tempo Total", f"{total_time_hours:.1f}h")
    
    st.divider()
    
    # Informações dos Dias
    st.subheader("🚗 Informações dos Dias")
    
    cols = st.columns(max_day)
    
    for day_idx, day in enumerate(sorted(points_by_day.keys())):
        with cols[day_idx]:
            st.markdown(f"### :green[Dia {day}]")
            st.metric("Pontos Atendidos", len(points_by_day[day]))
            st.metric("Distância", f"{distance_by_day[day]:.1f} km")
            
            day_points = points_by_day[day]
            if day_points:
                first_arrival = day_points[0][1]  # Já em minutos do dia (0-1439)
                last_arrival = day_points[-1][1]
                last_duration = day_points[-1][0].service_duration
                # Tempo de trabalho do dia
                day_time = (last_arrival - first_arrival) + last_duration
                
                hours = int(day_time // 60)
                minutes = int(day_time % 60)
                st.metric("Tempo Total", f"{hours}h{minutes:02d}")
    
    st.divider()
    
    # Ordem de Prioridades para Atendimento
    st.subheader("🎯 Ordem de Prioridades para Atendimento")
    
    priority_abbr = PRIORITY_ABBREVIATIONS
    priority_names = PRIORITY_NAMES
    
    # Agrupar IDs por prioridade
    priority_ids = {
        ServicePriority.EMERGENCY_OBSTETRIC: [],
        ServicePriority.DOMESTIC_VIOLENCE: [],
        ServicePriority.HORMONAL_MEDICATION: [],
        ServicePriority.POSTPARTUM_CARE: [],
        ServicePriority.REGULAR: []
    }
    
    for point in best_route:
        if point.id != 0:  # Excluir depósito
            priority_ids[point.priority].append(point.id)
    
    # Exibir em colunas
    col1, col2 = st.columns(2)
    
    priorities_list = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE,
        ServicePriority.REGULAR
    ]
    
    for i, priority in enumerate(priorities_list):
        col = col1 if i < 3 else col2
        with col:
            ids = priority_ids[priority]
            if ids:
                ids_str = f"({', '.join(map(str, sorted(ids)))})"
            else:
                ids_str = "()"
            
            # Usar cores nomeadas do Streamlit ao invés de hexadecimal
            color_map = {
                ServicePriority.EMERGENCY_OBSTETRIC: "red",
                ServicePriority.DOMESTIC_VIOLENCE: "orange",
                ServicePriority.HORMONAL_MEDICATION: "blue",
                ServicePriority.POSTPARTUM_CARE: "violet",
                ServicePriority.REGULAR: "gray"
            }
            color_name = color_map[priority]
            st.markdown(f":{color_name}[●] **{priority_names[priority]} ({priority_abbr[priority]})** - {ids_str}")
    
    st.divider()
    
    st.subheader("📋 Melhor Solução Encontrada")
    
    # Mapeamento de cores HTML
    PRIORITY_COLORS_HTML = {
        ServicePriority.EMERGENCY_OBSTETRIC: "#FF0000",  # Vermelho
        ServicePriority.DOMESTIC_VIOLENCE: "#FFA500",    # Laranja
        ServicePriority.HORMONAL_MEDICATION: "#0000FF",  # Azul
        ServicePriority.POSTPARTUM_CARE: "#800080",      # Roxo
        ServicePriority.REGULAR: "#808080"               # Cinza
    }
    
    # Criar HTML com IDs coloridos por prioridade - apenas vetor I
    route_without_depot = [p for p in best_route if p.id != 0]
    
    # Construir vetor com cores por prioridade
    def build_colored_vector(route):
        parts = ["[ "]
        for i, point in enumerate(route):
            color = PRIORITY_COLORS_HTML.get(point.priority, "#000000")
            parts.append(f"<span style='color: {color}; font-weight: bold;'>{point.id}</span>")
            if i < len(route) - 1:
                parts.append(", ")
        parts.append(" ]")
        return "".join(parts)
    
    v_html = build_colored_vector(route_without_depot)
    
    solution_html = f"""
    <div style='font-family: monospace; font-size: 16px; padding: 15px; background-color: #0e1117; border-radius: 5px; border: 1px solid rgb(49, 51, 63);'>
        <span style='color: rgb(250, 250, 250); font-weight: bold;'>I</span>
        <span style='color: rgb(250, 250, 250);'>= [ </span>
        {v_html}
        <span style='color: rgb(250, 250, 250);'> ]</span>
    </div>
    """
    
    st.markdown(solution_html, unsafe_allow_html=True)

def display_results_multi_vehicle(best_solution, best_fitness):
    """ Exibe os resultados da otimização com múltiplos veículos """
    
    # Verificar se best_solution é None (projeto 2V standalone)
    if best_solution is None:
        st.success("✅ Projeto 2 Veículos Executado!")
        st.info("🎮 O projeto com 2 veículos foi executado em uma janela separada do Pygame.")
        st.markdown("""
        ### 📋 Informações:
        - O projeto de 2 veículos roda de forma independente
        - Todas as informações foram exibidas na janela do Pygame
        - A visualização incluiu:
          - Rotas dos 2 veículos (verde e ciano)
          - Depósito (ponto amarelo D)
          - Ordem de atendimento
          - Gráfico de evolução
          - Melhor solução encontrada
        """)
        return
    
    # Cores por veículo
    VEHICLE_COLORS_HEX = {
        1: "#009600",  # Verde escuro
        2: "#00C8C8"   # Ciano
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_points = sum(len(v.route) for v in best_solution.vehicles)
        st.metric("Total de Pontos", total_points)
    
    with col2:
        total_distance = sum(v.total_distance for v in best_solution.vehicles)
        # Converter para km (multiplicar por 0.1)
        total_distance_km = total_distance * 0.1
        st.metric("Distância Total", f"{total_distance_km:.1f} km")
    
    with col3:
        # Calcular tempo total corretamente (apenas tempo de trabalho, sem o descanso) e carregar dados do JSON salvo que já tem o tempo correto
        try:
            from telegram_bot.route_integration import RouteDataIntegration
            integration = RouteDataIntegration()
            route_json = integration.load_latest_route()
            
            if route_json and route_json.get('vehicles'):
                # Somar tempo estimado de todos os veículos do JSON
                total_time_minutes = 0
                for vehicle_data in route_json['vehicles']:
                    estimated_time_str = vehicle_data.get('estimated_time', '0h 0min')
                    # Parse "7h 26min" -> minutos
                    parts = estimated_time_str.replace('h', '').replace('min', '').split()
                    if len(parts) >= 2:
                        total_time_minutes += int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 1:
                        total_time_minutes += int(parts[0]) * 60
                total_time_hours = total_time_minutes / 60.0
            else:
                # Fallback: usar total_time do algoritmo (pode estar incorreto)
                total_time_minutes = sum(v.total_time for v in best_solution.vehicles)
                total_time_hours = total_time_minutes / 60.0
        except:
            # Fallback: usar total_time do algoritmo
            total_time_minutes = sum(v.total_time for v in best_solution.vehicles)
            total_time_hours = total_time_minutes / 60.0
        
        st.metric("Tempo Total", f"{total_time_hours:.1f}h")
    
    st.divider()
    
    # Informações dos veículos
    st.subheader("🚗 Informações dos Veículos")
    
    cols = st.columns(len(best_solution.vehicles))
    
    for i, vehicle in enumerate(best_solution.vehicles):
        with cols[i]:
            st.markdown(f"### :green[Veículo {vehicle.vehicle_id}]")
            st.metric("Pontos Atendidos", len(vehicle.route))
            
            # Converter distância para km (multiplicar por 0.1)
            distance_km = vehicle.total_distance * 0.1
            st.metric("Distância", f"{distance_km:.1f} km")
            
            # Usar tempo do JSON ao invés de vehicle.total_time
            try:
                from telegram_bot.route_integration import RouteDataIntegration
                integration = RouteDataIntegration()
                route_json = integration.load_latest_route()
                
                if route_json and route_json.get('vehicles'):
                    # Encontrar dados deste veículo no JSON
                    vehicle_data = None
                    for v_data in route_json['vehicles']:
                        if v_data.get('id') == vehicle.vehicle_id:
                            vehicle_data = v_data
                            break
                    
                    if vehicle_data:
                        estimated_time_str = vehicle_data.get('estimated_time', '0h 0min')
                        # Parse "7h 26min" -> horas e minutos
                        parts = estimated_time_str.replace('h', '').replace('min', '').split()
                        if len(parts) >= 2:
                            hours = int(parts[0])
                            minutes = int(parts[1])
                        elif len(parts) == 1:
                            hours = int(parts[0])
                            minutes = 0
                        else:
                            # Fallback
                            hours = int(vehicle.total_time // 60)
                            minutes = int(vehicle.total_time % 60)
                    else:
                        # Fallback
                        hours = int(vehicle.total_time // 60)
                        minutes = int(vehicle.total_time % 60)
                else:
                    # Fallback
                    hours = int(vehicle.total_time // 60)
                    minutes = int(vehicle.total_time % 60)
            except:
                # Fallback: usar vehicle.total_time
                hours = int(vehicle.total_time // 60)
                minutes = int(vehicle.total_time % 60)
            
            st.metric("Tempo Total", f"{hours}h{minutes:02d}")
    
    st.divider()
    
    # Ordem de Prioridades para Atendimento
    st.subheader("🎯 Ordem de Prioridades para Atendimento")
    
    priority_abbr = PRIORITY_ABBREVIATIONS
    priority_names = PRIORITY_NAMES
    
    # Agrupar IDs por prioridade
    priority_ids = {
        ServicePriority.EMERGENCY_OBSTETRIC: [],
        ServicePriority.DOMESTIC_VIOLENCE: [],
        ServicePriority.HORMONAL_MEDICATION: [],
        ServicePriority.POSTPARTUM_CARE: [],
        ServicePriority.REGULAR: []
    }
    
    for vehicle in best_solution.vehicles:
        for point in vehicle.route:
            if point.id != 0:  # Excluir depósito (ID 0)
                # Verificar se a prioridade existe no dicionário
                if point.priority in priority_ids:
                    priority_ids[point.priority].append(point.id)
    
    # Exibir em colunas
    col1, col2 = st.columns(2)
    
    priorities_list = [
        ServicePriority.EMERGENCY_OBSTETRIC,
        ServicePriority.DOMESTIC_VIOLENCE,
        ServicePriority.HORMONAL_MEDICATION,
        ServicePriority.POSTPARTUM_CARE,
        ServicePriority.REGULAR
    ]
    
    # Mapeamento de cores Streamlit
    STREAMLIT_COLORS = {
        ServicePriority.EMERGENCY_OBSTETRIC: "red",
        ServicePriority.DOMESTIC_VIOLENCE: "orange",
        ServicePriority.HORMONAL_MEDICATION: "blue",
        ServicePriority.POSTPARTUM_CARE: "violet",
        ServicePriority.REGULAR: "gray"
    }
    
    for i, priority in enumerate(priorities_list):
        col = col1 if i < 3 else col2
        with col:
            ids = priority_ids[priority]
            if ids:
                ids_str = f"({', '.join(map(str, sorted(ids)))})"
            else:
                ids_str = "()"
            
            color = STREAMLIT_COLORS[priority]
            st.markdown(f":{color}[●] **{priority_names[priority]} ({priority_abbr[priority]})** - {ids_str}")
    
    st.divider()
    
    # Melhor Solução Encontrada - 2 VETORES SEPARADOS COM CORES
    st.subheader("📋 Melhor Solução Encontrada")
    
    # Mapeamento de cores HTML
    PRIORITY_COLORS_HTML = {
        ServicePriority.EMERGENCY_OBSTETRIC: "#FF0000",  # Vermelho
        ServicePriority.DOMESTIC_VIOLENCE: "#FFA500",    # Laranja
        ServicePriority.HORMONAL_MEDICATION: "#0000FF",  # Azul
        ServicePriority.POSTPARTUM_CARE: "#800080",      # Roxo
        ServicePriority.REGULAR: "#808080"               # Cinza
    }
    
    # Cores dos vetores dos veículos
    VEHICLE_COLORS = {
        1: "#009600",  # Verde escuro
        2: "#00C8C8"   # Ciano
    }
    
    for vehicle in best_solution.vehicles:
        vehicle_color = VEHICLE_COLORS.get(vehicle.vehicle_id, "#FFFFFF")
        
        # Criar HTML com IDs coloridos por prioridade
        html_parts = [f"<div style='font-family: monospace; font-size: 16px; padding: 10px; background-color: #0e1117; border-radius: 5px;'><span style='color: {vehicle_color}; font-weight: bold;'>V{vehicle.vehicle_id}</span> <span style='color: rgb(250, 250, 250);'>= [ "]
        
        for i, point in enumerate(vehicle.route):
            color = PRIORITY_COLORS_HTML.get(point.priority, "#000000")
            html_parts.append(f"<span style='color: {color}; font-weight: bold;'>{point.id}</span>")
            
            if i < len(vehicle.route) - 1:
                html_parts.append(", ")
        
        html_parts.append(" ]</span></div>")
        
        st.markdown("".join(html_parts), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Representação I = [[V1], [V2]]
    st.markdown("**Representação da Solução:**")
    
    # Mapeamento de cores HTML por prioridade
    PRIORITY_COLORS_HTML = {
        ServicePriority.EMERGENCY_OBSTETRIC: "#FF0000",  # Vermelho
        ServicePriority.DOMESTIC_VIOLENCE: "#FFA500",    # Laranja
        ServicePriority.HORMONAL_MEDICATION: "#0000FF",  # Azul
        ServicePriority.POSTPARTUM_CARE: "#800080",      # Roxo
        ServicePriority.REGULAR: "#808080"               # Cinza
    }
    
    # Cores dos vetores dos veículos
    VEHICLE_COLORS = {
        1: "#009600",  # Verde escuro
        2: "#00C8C8"   # Ciano
    }
    
    # Construir vetores V1 e V2 com cores por prioridade
    def build_colored_vector(vehicle):
        parts = ["[ "]
        for i, point in enumerate(vehicle.route):
            color = PRIORITY_COLORS_HTML.get(point.priority, "#000000")
            parts.append(f"<span style='color: {color}; font-weight: bold;'>{point.id}</span>")
            if i < len(vehicle.route) - 1:
                parts.append(", ")
        parts.append(" ]")
        return "".join(parts)
    
    v1_html = build_colored_vector(best_solution.vehicles[0])
    v2_html = build_colored_vector(best_solution.vehicles[1])
    
    solution_html = f"""
    <div style='font-family: monospace; font-size: 16px; padding: 15px; background-color: #0e1117; border-radius: 5px; border: 1px solid rgb(49, 51, 63);'>
        <span style='color: rgb(250, 250, 250); font-weight: bold;'>I</span>
        <span style='color: rgb(250, 250, 250);'>= [ </span>
        {v1_html}
        <span style='color: rgb(250, 250, 250);'> , </span>
        {v2_html}
        <span style='color: rgb(250, 250, 250);'> ]</span>
    </div>
    """
    
    st.markdown(solution_html, unsafe_allow_html=True)


def main():
    """ Função principal da aplicação Streamlit """
    
    st.title("🚗 Sistema de Otimização de Rotas com Restrições")
    st.markdown("**Algoritmo Genético para Roteamento de Atendimentos em Saúde da Mulher**")
    
    # Adicionar divisor após o título
    st.divider()
    
    # Placeholder para sidebar (será preenchido depois)
    sidebar_placeholder = st.sidebar.empty()
    
    if 'optimization_done' not in st.session_state:
        st.session_state.optimization_done = False
    
    if 'num_vehicles' not in st.session_state:
        st.session_state.num_vehicles = 1  # Default: 1 veículo
    
    if 'max_generations' not in st.session_state:
        st.session_state.max_generations = 500  # Default: 500
    
    if 'vehicle_speed' not in st.session_state:
        st.session_state.vehicle_speed = 80  # Default: 80 km/h
    
    if not st.session_state.optimization_done:
        # Verificar se deve auto-iniciar (após Reiniciar)
        auto_start = st.session_state.get('auto_start', False)
        
        if not auto_start:
            st.markdown("### 🚀 Configuração da Otimização")
            
            # CSS para aumentar fontes e ajustar layout
            st.markdown("""
            <style>
            div[role="radiogroup"] label {
                font-size: 1.5rem !important;
                font-weight: 600 !important;
            }
            div[role="radiogroup"] label p {
                font-size: 1.5rem !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Layout em 3 colunas (veículos, gerações, vazia)
            col_vehicles, col_generations, col_empty = st.columns(3)
            
            with col_vehicles:
                # Seletor de número de veículos
                st.markdown("<h3 style='font-size: 1.3rem; margin-bottom: 15px;'>Número de veículos:</h3>", unsafe_allow_html=True)
                num_vehicles = st.radio(
                    "Número de veículos",
                    options=[1, 2],
                    format_func=lambda x: f"🚗 {x} veículo" if x == 1 else f"🚗🚗 {x} veículos",
                    horizontal=True,
                    help="1 veículo: Otimização tradicional | 2 veículos: Otimização multi-veículo com depósito",
                    key='num_vehicles_radio',
                    label_visibility="collapsed",
                    index=0  # Default: 1 veículo (índice 0 na lista [1, 2])
                )
                st.session_state.num_vehicles = num_vehicles
                
                # Texto de restrição de medicamentos prioritários (abaixo dos veículos)
                st.markdown("<br>", unsafe_allow_html=True)
                if num_vehicles == 1:
                    restriction_html = """
                    <div style='margin-top: 10px; margin-bottom: 20px; white-space: nowrap;'>
                        <span style='font-size: 18px; font-weight: 600;'>Medicamentos prioritários entregues <span style='font-size: 22px; font-weight: 700; color: #FF8C00; background-color: rgba(255, 140, 0, 0.1); padding: 4px 8px; border-radius: 4px;'>até o 1º dia</span></span>
                    </div>
                    """
                else:  # 2 veículos
                    restriction_html = """
                    <div style='margin-top: 10px; margin-bottom: 20px; white-space: nowrap;'>
                        <span style='font-size: 18px; font-weight: 600;'>Medicamentos prioritários entregues <span style='font-size: 22px; font-weight: 700; color: #FF8C00; background-color: rgba(255, 140, 0, 0.1); padding: 4px 8px; border-radius: 4px;'>até 12:00</span></span>
                    </div>
                    """
                st.markdown(restriction_html, unsafe_allow_html=True)
            
            with col_generations:
                # Seletor de número de gerações
                st.markdown("<h3 style='font-size: 1.3rem; margin-bottom: 15px;'>Número de gerações:</h3>", unsafe_allow_html=True)
                
                # Opções incluindo "Infinito" (representado por -1)
                generation_options = [100, 200, 500, 1000, 2000, 5000, 10000, 15000, 20000, "Infinito"]
                generation_display = {
                    100: "100",
                    200: "200",
                    500: "500",
                    1000: "1.000",
                    2000: "2.000",
                    5000: "5.000",
                    10000: "10.000",
                    15000: "15.000",
                    20000: "20.000",
                    "Infinito": "∞ Infinito (para após 5000 gerações sem melhoria)"
                }
                
                selected_option = st.selectbox(
                    "Número de gerações",
                    options=generation_options,
                    format_func=lambda x: generation_display[x],
                    index=2,  # 500 como padrão (índice 2 na lista [100, 200, 500, ...])
                    help="Número máximo de gerações do algoritmo genético. 'Infinito' para até 5000 gerações sem melhoria.",
                    key='max_generations_select',
                    label_visibility="collapsed"
                )
                
                # Converter "Infinito" para -1 internamente
                max_generations = -1 if selected_option == "Infinito" else selected_option
                st.session_state.max_generations = max_generations
            
            with col_empty:
                # Campo de entrada de velocidade média
                st.markdown("<h3 style='font-size: 1.3rem; margin-bottom: 15px;'>Velocidade Média (km/h):</h3>", unsafe_allow_html=True)
                vehicle_speed = st.number_input(
                    "Velocidade Média (km/h)",
                    min_value=10,
                    max_value=200,
                    value=80,  # Valor padrão: 80 km/h
                    step=10,  # Incrementos de 10 em 10 km/h
                    help="Velocidade média dos veículos (10-200 km/h). Afeta tempo de viagem e número de dias necessários.",
                    key='vehicle_speed_input',
                    label_visibility="collapsed"
                )
                st.session_state.vehicle_speed = vehicle_speed
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 1.2rem; margin-bottom: 20px;'>Clique no botão abaixo para iniciar o processo de otimização de rotas.</p>", unsafe_allow_html=True)
            
            # Estilo customizado para o botão Encerrar (mesmo estilo do primary, mas com fundo preto)
            st.markdown("""
            <style>
            div.stButton > button[kind="secondary"] {
                background-color: #0e1117 !important;
                border: 1px solid rgb(49, 51, 63) !important;
                border-radius: 0.5rem !important;
                color: rgb(250, 250, 250) !important;
                font-weight: 400 !important;
                padding: 0.25rem 0.75rem !important;
                transition: all 0.2s ease !important;
            }
            div.stButton > button[kind="secondary"]:hover {
                border-color: rgb(255, 75, 75) !important;
                color: rgb(255, 75, 75) !important;
            }
            div.stButton > button[kind="secondary"]:active {
                background-color: #000000 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Botões alinhados horizontalmente: Iniciar à esquerda, espaço no meio, Encerrar à direita
            col_start, col_empty, col_close = st.columns([1, 2, 1])
            
            with col_start:
                start_button = st.button("▶️ Iniciar otimização", type="primary", key="start_optimization_btn")
            
            with col_close:
                close_button = st.button("❌ Encerrar", type="secondary", key="close_initial_btn")
            
            # Processar ação do botão Encerrar
            if close_button:
                # Limpar arquivos temporários
                temp_dir = '/tmp'
                for filename in ['service_points.pkl', 'progress.pkl', 'pygame_final.png', 'depot_location.pkl', 'vehicle_speed.pkl']:
                    filepath = os.path.join(temp_dir, filename)
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except:
                            pass
                
                # Executar make clean em background
                import subprocess
                import threading
                
                def run_clean():
                    try:
                        # Executar make clean no diretório raiz do projeto
                        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                        result = subprocess.run(['make', 'clean'],
                                              check=False,
                                              cwd=project_root,
                                              capture_output=True,
                                              text=True)
                        print(f"Make clean executado: {result.returncode}")
                        if result.stdout:
                            print(f"Output: {result.stdout}")
                        if result.stderr:
                            print(f"Errors: {result.stderr}")
                    except Exception as e:
                        print(f"Erro ao executar make clean: {e}")
                    # Encerrar o servidor após limpeza
                    import signal
                    time.sleep(1)
                    os.kill(os.getpid(), signal.SIGTERM)
                
                # Mensagem de encerramento
                st.markdown("### 👋 Aplicação Encerrada")
                st.markdown("✅ Limpeza concluída!")
                st.markdown("Você pode fechar esta aba do navegador.")
                st.info("O servidor será encerrado em alguns segundos...")
                
                # Executar limpeza e encerramento em thread separada
                cleanup_thread = threading.Thread(target=run_clean)
                cleanup_thread.daemon = True
                cleanup_thread.start()
                
                # Parar execução do Streamlit
                st.stop()
    
    # Preencher sidebar com informações (agora que num_vehicles está definido)
    with sidebar_placeholder.container():
        st.header("ℹ️ Informações do Sistema")
        
        st.markdown("### 🧬 Parâmetros do Algoritmo Genético")
        
        # Obter número de gerações atual
        max_generations = st.session_state.get('max_generations', 10)
        
        # Formatar exibição de gerações
        if max_generations == -1:
            generations_display = "∞ (para após 5000 sem melhoria)"
        else:
            generations_display = f"{max_generations:,}".replace(',', '.')
        
        st.markdown(f"""
        - **Pontos de Atendimento:** 20
        - **Tamanho da População:** 100
        - **Gerações Máximas:** {generations_display}
        - **Probabilidade de Mutação:** 50%
        - **Seleção:** Torneio (tamanho 5)
        - **Elitismo:** Ativo
        """)
        
        st.divider()
        
        st.markdown("### 🎨 Legenda de Cores")
        st.markdown("""
        - 🔴 **Vermelho:** Emergência Obstétrica (EME) - (1,2)
        - 🟠 **Laranja:** Violência Doméstica (VIO) - (3,4)
        - 🔵 **Azul:** Medicamento Hormonal (MED) - (5,6)
        - 🟣 **Roxo:** Pós-Parto (POS) - (7,8)
        - ⚫ **Cinza:** Atendimento Regular (REG) - (9...20)
        - 🟡 **Amarelo:** Depósito (D)
        """)
        
        st.divider()
        
        st.markdown("### ⏰ Restrições")
        
        # Obter número de veículos atual
        num_vehicles = st.session_state.get('num_vehicles', 1)
        
        # Texto de restrição de medicamentos prioritários e janelas de tempo dependem do número de veículos
        if num_vehicles == 1:
            priority_restriction = "Devem ser entregues no :orange[**1º dia**]"
            vio_window = ":orange[**8h às 12h**]"
            pos_window = ":orange[**9h às 13h**]"
        else:  # 2 veículos
            priority_restriction = "Devem ser entregues até :orange[**12:00h**]"
            vio_window = ":orange[**8h às 10h**]"
            pos_window = ":orange[**9h às 11h**]"
        
        st.markdown(f"""
        - **Horário Comercial:** 8h às 18h
        - **Medicamentos prioritários:** {priority_restriction}
        - **Emergência Obstétrica:** Prioridade máxima
        - **Violência Doméstica:** {vio_window}
        - **Pós-Parto:** {pos_window}
        - **Medicamentos Hormonais:** Controle de temperatura
        """)
    
    if not st.session_state.optimization_done:
        # Verificar se o botão foi clicado (se não estiver em auto_start)
        should_start = auto_start or (not auto_start and 'start_button' in locals() and start_button)
        
        if should_start:
            # Limpar flag de auto_start
            if 'auto_start' in st.session_state:
                del st.session_state['auto_start']
            
            # Obter número de veículos, gerações e velocidade selecionados
            num_vehicles = st.session_state.num_vehicles
            MAX_GENERATIONS = st.session_state.max_generations
            vehicle_speed = st.session_state.get('vehicle_speed', 60)
            
            # Arquivos temporários
            service_points_file = os.path.join(TEMP_DIR, SERVICE_POINTS_FILE)
            progress_file = os.path.join(TEMP_DIR, PROGRESS_FILE)
            screenshot_file = os.path.join(TEMP_DIR, SCREENSHOT_FILE)
            depot_file = os.path.join(TEMP_DIR, DEPOT_FILE)
            speed_file = os.path.join(TEMP_DIR, 'vehicle_speed.pkl')
            
            # Limpar arquivos antigos
            for filepath in [progress_file, screenshot_file, depot_file, speed_file]:
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except:
                        pass
            
            # Salvar velocidade para o Pygame
            with open(speed_file, 'wb') as f:
                pickle.dump(vehicle_speed, f)
            
            # Criar pontos de serviço baseado no número de veículos
            if num_vehicles == 1:
                # Para 1 veículo: incluir depósito como ID 0
                service_points = create_random_service_points(N_POINTS)
                with open(service_points_file, 'wb') as f:
                    pickle.dump(service_points, f)
            else:
                # Para 2 veículos: criar pontos SEM depósito (IDs 1-20)
                service_points = []
                types_guaranteed = [
                    'emergency', 'emergency',
                    'violence', 'violence',
                    'medication', 'medication',
                    'postpartum', 'postpartum'
                ]
                
                for i, service_type in enumerate(types_guaranteed):
                    location = (
                        random.randint(COORD_MIN_X, COORD_MAX_X),
                        random.randint(COORD_MIN_Y, COORD_MAX_Y)
                    )
                    
                    time_window = None
                    if service_type == 'violence':
                        time_window = VIOLENCE_TIME_WINDOW
                    elif service_type == 'postpartum':
                        time_window = POSTPARTUM_TIME_WINDOW
                    
                    point = create_service_point(i + 1, location, service_type, time_window)
                    service_points.append(point)
                
                for i in range(len(types_guaranteed), N_POINTS):
                    location = (
                        random.randint(COORD_MIN_X, COORD_MAX_X),
                        random.randint(COORD_MIN_Y, COORD_MAX_Y)
                    )
                    point = create_service_point(i + 1, location, 'regular', None)
                    service_points.append(point)
                
                # Criar depósito separado
                depot_location = (
                    random.randint(COORD_MIN_X, COORD_MAX_X),
                    random.randint(COORD_MIN_Y, COORD_MAX_Y)
                )
                
                with open(service_points_file, 'wb') as f:
                    pickle.dump(service_points, f)
                with open(depot_file, 'wb') as f:
                    pickle.dump(depot_location, f)
            
            st.markdown("### 🔄 Otimização em Andamento...")
            vehicle_text = "1 veículo" if num_vehicles == 1 else "2 veículos"
            st.info(f"🎮 Uma janela do Pygame está sendo aberta com a visualização completa ({vehicle_text})!")
            
            # Iniciar Pygame em processo separado (escolher função baseado no número de veículos)
            if num_vehicles == 1:
                pygame_process = multiprocessing.Process(
                    target=run_pygame_with_full_visualization,
                    args=(service_points_file, progress_file, screenshot_file, max_generations)
                )
            else:  # 2 veículos
                with open(depot_file, 'rb') as f:
                    depot_location = pickle.load(f)
                pygame_process = multiprocessing.Process(
                    target=run_pygame_2_vehicles,
                    args=(service_points_file, progress_file, screenshot_file, depot_location, max_generations)
                )
            
            pygame_process.start()
            
            # Monitorar progresso
            st.markdown("---")
            st.markdown("### 📊 Progresso da Otimização")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            while pygame_process.is_alive():
                try:
                    if os.path.exists(progress_file):
                        with open(progress_file, 'rb') as f:
                            progress_data = pickle.load(f)
                        
                        generation = progress_data.get('generation', 0)
                        best_fitness = progress_data.get('best_fitness', 0)
                        
                        # Modo infinito: mostrar progresso indeterminado
                        if MAX_GENERATIONS == -1:
                            # Barra de progresso pulsante (0.5 fixo)
                            progress_bar.progress(0.5)
                            status_text.text(f"Geração {generation} (∞) - Fitness: {best_fitness:.2f}")
                        else:
                            # Modo normal: progresso baseado em gerações
                            progress = generation / MAX_GENERATIONS
                            progress_bar.progress(min(progress, 1.0))
                            status_text.text(f"Geração {generation}/{MAX_GENERATIONS} - Fitness: {best_fitness:.2f}")
                except:
                    pass
                
                time.sleep(0.5)
            
            # Aguardar processo terminar completamente
            pygame_process.join()
            
            # Aguardar um pouco para garantir que o arquivo foi salvo
            time.sleep(1)
            
            # Verificar se os resultados finais existem
            if os.path.exists(progress_file):
                # Carregar resultados finais
                with open(progress_file, 'rb') as f:
                    final_data = pickle.load(f)
                
                # Verificar se a otimização foi concluída
                if final_data.get('completed', False):
                    # Verificar se é solução de 1 ou 2 veículos
                    if 'best_solution' in final_data:
                        # 2 veículos
                        st.session_state.best_solution = final_data['best_solution']
                        st.session_state.best_fitness = final_data['best_fitness']
                        st.session_state.is_multi_vehicle = True
                    else:
                        # 1 veículo
                        st.session_state.best_route = final_data['best_route']
                        st.session_state.best_fitness = final_data['best_fitness']
                        st.session_state.arrival_times = final_data['arrival_times']
                        st.session_state.is_multi_vehicle = False
                    
                    st.session_state.fitness_history = final_data['fitness_history']
                    st.session_state.screenshot_file = screenshot_file
                    st.session_state.optimization_done = True
                    
                    # Salvar dados para o bot do Telegram
                    try:
                        from telegram_bot.route_integration import RouteDataIntegration
                        integration = RouteDataIntegration()
                        
                        # Carregar pontos de serviço
                        with open(service_points_file, 'rb') as f:
                            service_points = pickle.load(f)
                        
                        if st.session_state.is_multi_vehicle:
                            # Multi-veículo: converter dados
                            best_solution = st.session_state.best_solution
                            route_data = {
                                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'fitness': st.session_state.best_fitness,
                                'num_vehicles': 2,
                                'vehicles': []
                            }
                            
                            for vehicle in best_solution.vehicles:
                                # Calcular horário de retorno ao depósito
                                # Última parada + duração + tempo de viagem de volta
                                if vehicle.arrival_times and vehicle.route:
                                    from src.core.service_points import calculate_distance
                                    
                                    # Carregar depot_location
                                    depot_file = os.path.join(TEMP_DIR, DEPOT_FILE)
                                    if os.path.exists(depot_file):
                                        with open(depot_file, 'rb') as f:
                                            depot_location = pickle.load(f)
                                    else:
                                        depot_location = (0, 0)
                                    
                                    # Última parada (em minutos absolutos)
                                    last_arrival = vehicle.arrival_times[-1]
                                    last_point = vehicle.route[-1]
                                    
                                    # Calcular tempo de retorno ao depósito
                                    return_distance = calculate_distance(last_point.location, depot_location)
                                    speed_km_per_min = vehicle_speed / 60.0
                                    return_travel_time = (return_distance * 0.1) / speed_km_per_min
                                    
                                    # Horário de retorno = última parada + duração + viagem de volta
                                    return_time = last_arrival + last_point.service_duration + return_travel_time
                                else:
                                    return_time = 480
                                
                                vehicle_data = {
                                    'id': vehicle.vehicle_id,
                                    'driver': f'Motorista {vehicle.vehicle_id}',
                                    'total_stops': len(vehicle.route),
                                    'total_distance': round(vehicle.total_distance * 0.1, 2),
                                    'estimated_time': f"{int(vehicle.total_time // 60)}h {int(vehicle.total_time % 60)}min",
                                    'start_time': '08:00',
                                    'end_time': format_time(return_time),
                                    'stops': []
                                }
                                
                                # Usar arrival_times reais ao invés de recalcular
                                for idx, point in enumerate(vehicle.route):
                                    arrival_time = vehicle.arrival_times[idx] if idx < len(vehicle.arrival_times) else 480
                                    stop = {
                                        'id': idx + 1,
                                        'type': PRIORITY_ABBREVIATIONS.get(point.priority, 'REG'),
                                        'priority': list(ServicePriority).index(point.priority) + 1,
                                        'address': f"Ponto {point.id}",
                                        'time': format_time(arrival_time),
                                        'duration': f"{int(point.service_duration)} min",
                                        'instructions': f"Atendimento {PRIORITY_NAMES.get(point.priority, 'Regular')}",
                                        'special_notes': f"Ponto ID {point.id}"
                                    }
                                    vehicle_data['stops'].append(stop)
                                
                                # CORREÇÃO: Calcular tempo total corretamente (apenas tempo de trabalho, sem o descanso)
                                # Usar o mesmo algoritmo do route_integration.py
                                stops = vehicle_data['stops']
                                days = []
                                current_day_stops = []
                                previous_time_mins = None
                                
                                for stop in stops:
                                    time_str = stop['time']
                                    hours, mins = map(int, time_str.split(':'))
                                    stop_time_mins = hours * 60 + mins
                                    
                                    # Detectar mudança de dia (horário volta para trás)
                                    if previous_time_mins is not None and stop_time_mins < previous_time_mins:
                                        if current_day_stops:
                                            days.append(current_day_stops)
                                        current_day_stops = [stop]
                                    else:
                                        current_day_stops.append(stop)
                                    
                                    duration_mins = int(stop['duration'].split()[0])
                                    previous_time_mins = stop_time_mins + duration_mins
                                
                                # Adicionar último dia
                                if current_day_stops:
                                    days.append(current_day_stops)
                                
                                # Calcular tempo de trabalho de cada dia (SEM contar descanso)
                                total_time_minutes = 0
                                for day_stops in days:
                                    first_time = day_stops[0]['time']
                                    first_h, first_m = map(int, first_time.split(':'))
                                    first_mins = first_h * 60 + first_m
                                    
                                    last_time = day_stops[-1]['time']
                                    last_h, last_m = map(int, last_time.split(':'))
                                    last_mins = last_h * 60 + last_m
                                    last_duration = int(day_stops[-1]['duration'].split()[0])
                                    
                                    # Tempo de trabalho do dia
                                    day_time = (last_mins + last_duration) - first_mins
                                    total_time_minutes += day_time
                                
                                # Atualizar estimated_time com o valor correto
                                vehicle_data['estimated_time'] = f"{total_time_minutes // 60}h {total_time_minutes % 60}min"
                                
                                route_data['vehicles'].append(vehicle_data)
                        else:
                            # 1 veículo: converter dados
                            best_route = st.session_state.best_route
                            arrival_times = st.session_state.arrival_times
                            total_distance, total_time, _ = calculate_route_time_and_distance(best_route, speed=vehicle_speed)
                            
                            route_data = {
                                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'fitness': st.session_state.best_fitness,
                                'num_vehicles': 1,
                                'vehicles': [{
                                    'id': 1,
                                    'driver': 'Motorista 1',
                                    'total_stops': len([p for p in best_route if p.id != 0]),
                                    'total_distance': round(total_distance * 0.1, 2),
                                    'estimated_time': f"{int(total_time // 60)}h {int(total_time % 60)}min",
                                    'start_time': '08:00',
                                    'end_time': format_time(480 + total_time),
                                    'stops': []
                                }]
                            }
                            
                            # Criar lista de paradas sem o depósito, mantendo a ordem correta
                            for idx, point in enumerate(best_route):
                                if point.id == 0:  # Pular depósito
                                    continue
                                
                                stop = {
                                    'id': len(route_data['vehicles'][0]['stops']) + 1,
                                    'type': PRIORITY_ABBREVIATIONS.get(point.priority, 'REG'),
                                    'priority': list(ServicePriority).index(point.priority) + 1,
                                    'address': f"Ponto {point.id}",
                                    'time': format_time(arrival_times[idx]),
                                    'duration': f"{int(point.service_duration)} min",
                                    'instructions': f"Atendimento {PRIORITY_NAMES.get(point.priority, 'Regular')}",
                                    'special_notes': f"Ponto ID {point.id}"
                                }
                                route_data['vehicles'][0]['stops'].append(stop)
                            
                            # Calcular tempo total corretamente (apenas tempo de trabalho, sem o descanso)
                            # Usar o mesmo algoritmo do route_integration.py
                            stops = route_data['vehicles'][0]['stops']
                            days = []
                            current_day_stops = []
                            previous_time_mins = None
                            
                            for stop in stops:
                                time_str = stop['time']
                                hours, mins = map(int, time_str.split(':'))
                                stop_time_mins = hours * 60 + mins
                                
                                # Detectar mudança de dia (horário volta para trás)
                                if previous_time_mins is not None and stop_time_mins < previous_time_mins:
                                    if current_day_stops:
                                        days.append(current_day_stops)
                                    current_day_stops = [stop]
                                else:
                                    current_day_stops.append(stop)
                                
                                duration_mins = int(stop['duration'].split()[0])
                                previous_time_mins = stop_time_mins + duration_mins
                            
                            # Adicionar último dia
                            if current_day_stops:
                                days.append(current_day_stops)
                            
                            # Calcular tempo de trabalho de cada dia (SEM contar descanso)
                            total_time_minutes = 0
                            for day_stops in days:
                                first_time = day_stops[0]['time']
                                first_h, first_m = map(int, first_time.split(':'))
                                first_mins = first_h * 60 + first_m
                                
                                last_time = day_stops[-1]['time']
                                last_h, last_m = map(int, last_time.split(':'))
                                last_mins = last_h * 60 + last_m
                                last_duration = int(day_stops[-1]['duration'].split()[0])
                                
                                # Tempo de trabalho do dia
                                day_time = (last_mins + last_duration) - first_mins
                                total_time_minutes += day_time
                            
                            # Atualizar estimated_time com o valor correto
                            route_data['vehicles'][0]['estimated_time'] = f"{total_time_minutes // 60}h {total_time_minutes % 60}min"
                        
                        # Salvar dados
                        integration.save_route(route_data)
                        print("✅ Dados salvos para o bot do Telegram!")
                        
                        # Iniciar bot do Telegram automaticamente
                        try:
                            import subprocess
                            import threading
                            
                            def start_telegram_bot():
                                """ Inicia o bot do Telegram em background """
                                try:
                                    bot_path = os.path.join(project_root, 'telegram_bot', 'bot.py')
                                    if os.path.exists(bot_path):
                                        # Verificar se o bot já está rodando (opcional com psutil)
                                        bot_running = False
                                        try:
                                            import psutil
                                            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                                                try:
                                                    cmdline = proc.info.get('cmdline', [])
                                                    if cmdline and 'bot.py' in ' '.join(cmdline):
                                                        bot_running = True
                                                        print("ℹ️ Bot do Telegram já está rodando")
                                                        break
                                                except:
                                                    continue
                                        except ImportError:
                                            # psutil não disponível, tentar iniciar mesmo assim
                                            print("ℹ️ psutil não disponível, iniciando bot sem verificação de duplicação")
                                        
                                        if not bot_running:
                                            # Iniciar bot em processo separado
                                            subprocess.Popen(
                                                [sys.executable, bot_path],
                                                cwd=os.path.dirname(bot_path),
                                                stdout=subprocess.DEVNULL,
                                                stderr=subprocess.DEVNULL,
                                                start_new_session=True
                                            )
                                            print("🤖 Bot do Telegram iniciado automaticamente!")
                                    else:
                                        print(f"⚠️ Arquivo do bot não encontrado: {bot_path}")
                                except Exception as e:
                                    print(f"⚠️ Erro ao iniciar bot do Telegram: {e}")
                            
                            # Iniciar bot em thread separada para não bloquear
                            bot_thread = threading.Thread(target=start_telegram_bot)
                            bot_thread.daemon = True
                            bot_thread.start()
                        except Exception as e:
                            print(f"⚠️ Erro ao tentar iniciar bot: {e}")
                    except Exception as e:
                        print(f"⚠️ Erro ao salvar dados para o bot: {e}")
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.rerun()
                else:
                    # Verificar se há mensagem especial (para 2 veículos)
                    if 'message' in final_data:
                        st.warning("⚠️ Funcionalidade de 2 veículos")
                        st.info(final_data['message'])
                        st.markdown("### Como usar:")
                        st.code("cd 'Projeto - Fase 2 - 2V/genetic_algorithm_routes_optimization'\npython main.py", language="bash")
                    else:
                        st.error("❌ Otimização não foi concluída corretamente.")
            else:
                st.error("❌ Arquivo de resultados não encontrado.")
    
    else:
        st.success("✅ Otimização Concluída!")
        
        # Mostrar screenshot final do Pygame
        if 'screenshot_file' in st.session_state and os.path.exists(st.session_state.screenshot_file):
            st.markdown("### 🖼️ Resultado Final da Visualização Pygame")
            screenshot = Image.open(st.session_state.screenshot_file)
            st.image(screenshot, caption="Tela Final do Pygame")
            st.divider()
        
        # Mostrar gráfico de evolução
        if 'fitness_history' in st.session_state:
            st.markdown("### 📊 Evolução do Fitness ao Longo das Gerações")
            df = pd.DataFrame({
                'Geração': list(range(1, len(st.session_state.fitness_history) + 1)),
                'Fitness': st.session_state.fitness_history
            })
            st.line_chart(df.set_index('Geração'), width='stretch')
            
            # Verificar se há dados no histórico antes de acessar
            if st.session_state.fitness_history and len(st.session_state.fitness_history) > 0:
                col1, col2, col3, col4 = st.columns(4)
                # Calcular última geração com otimização (melhoria > 0.1%)
                last_improvement_gen = 0
                best_fitness_so_far = float('inf')
                
                for i in range(len(st.session_state.fitness_history)):
                    # Considerar melhoria se for pelo menos 0.1% melhor
                    if st.session_state.fitness_history[i] < best_fitness_so_far * 0.999:
                        last_improvement_gen = i
                        best_fitness_so_far = st.session_state.fitness_history[i]
                
                with col1:
                    st.metric("Fitness Inicial", f"{st.session_state.fitness_history[0]:.2f}")
                with col2:
                    st.metric("Fitness Final", f"{st.session_state.fitness_history[-1]:.2f}")
                with col3:
                    improvement = st.session_state.fitness_history[0] - st.session_state.fitness_history[-1]
                    st.metric("Melhoria Total", f"{improvement:.2f}", delta=f"-{improvement:.2f}", delta_color="inverse")
                with col4:
                    improvement_pct = (improvement / st.session_state.fitness_history[0]) * 100
                    st.metric("Melhoria %", f"{improvement_pct:.1f}%")
                
                # Nova linha com última geração com otimização
                st.markdown("---")
                col_opt1, col_opt2, col_opt3 = st.columns(3)
                with col_opt1:
                    st.metric("Última Geração com Otimização", f"{last_improvement_gen}")
                with col_opt2:
                    total_generations = len(st.session_state.fitness_history) - 1
                    st.metric("Total de Gerações", f"{total_generations}")
                with col_opt3:
                    if total_generations > 0:
                        stagnation = total_generations - last_improvement_gen
                        st.metric("Gerações sem Melhoria", f"{stagnation}")
            
            st.divider()
        
        # Exibir resultados (verificar se é multi-veículo ou não)
        if st.session_state.get('is_multi_vehicle', False):
            display_results_multi_vehicle(
                st.session_state.best_solution,
                st.session_state.best_fitness
            )
        else:
            display_results(
                st.session_state.best_route,
                st.session_state.best_fitness,
                st.session_state.arrival_times
            )
        
        st.divider()
        
        # ===== SEÇÃO LLM: GERAÇÃO DE CONTEÚDO INTELIGENTE =====
        st.markdown("### 🤖 Assistente Inteligente com IA")
        st.markdown("Gere documentos e obtenha informações sobre a rota otimizada usando Inteligência Artificial.")
        
        # Inicializar LLM Integration
        if 'llm_integration' not in st.session_state:
            st.session_state.llm_integration = LLMIntegration()
            st.session_state.llm_initialized = st.session_state.llm_integration.initialize()
        
        # Verificar se LLM está disponível
        if st.session_state.llm_initialized:
            # CSS para adicionar espaçamento de 1cm entre as abas
            st.markdown("""
            <style>
            button[data-baseweb="tab"] {
                margin-right: 1cm !important;
            }
            button[data-baseweb="tab"]:last-child {
                margin-right: 0 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Tabs para diferentes funcionalidades
            tab1, tab2, tab_telegram, tab3 = st.tabs(["📋 Manual de Instruções", "🗺️ Roteiro Detalhado", "📱 Telegram QRCode", "⁉️ Perguntas & Respostas"])
            
            # Preparar dados da rota
            if st.session_state.get('is_multi_vehicle', False):
                # Multi-veículo
                from src.llm.utils.streamlit_integration import prepare_route_data_multi_vehicle
                vehicles_data = prepare_route_data_multi_vehicle(st.session_state.best_solution)
                
                # Para Q&A: combinar todos os veículos em uma única rota
                all_points = []
                all_arrival_times = []
                for vehicle in st.session_state.best_solution.vehicles:
                    all_points.extend(vehicle.route)
                    vehicle_speed = st.session_state.get('vehicle_speed', 60)
                    _, _, v_arrival_times = calculate_route_time_and_distance(vehicle.route, speed=vehicle_speed)
                    all_arrival_times.extend(v_arrival_times)
                
                route = all_points
                arrival_times = all_arrival_times
                total_distance = sum(v.total_distance for v in st.session_state.best_solution.vehicles) * 0.1
                total_time = sum(v.total_time for v in st.session_state.best_solution.vehicles)
            else:
                # Veículo único
                route = st.session_state.best_route
                arrival_times = st.session_state.arrival_times
                vehicle_speed = st.session_state.get('vehicle_speed', 60)
                total_distance, total_time, _ = calculate_route_time_and_distance(route, speed=vehicle_speed)
                total_distance = total_distance * 0.1
                vehicles_data = None
            
            # TAB 1: Manual de Instruções
            with tab1:
                st.markdown("#### 📖 Manual de Instruções e Checklist")
                st.markdown("Baixe o manual completo com instruções detalhadas e o checklist pré-itinerário em PDF.")
                
                col1, col2, col3 = st.columns(3)
                
                # Botão Manual de Instruções
                with col1:
                    try:
                        from src.llm.utils.pdf_generator import generate_manual_pdf, generate_multi_vehicle_manuals_zip
                        
                        if st.button("📝 Gerar Manual de Instruções", key="gen_manual_btn", type="secondary", use_container_width=True):
                            with st.spinner("Gerando manual de instruções e preparando download..."):
                                # Verificar se é multi-veículo
                                if st.session_state.get('is_multi_vehicle', False) and vehicles_data:
                                    # Gerar ZIP com múltiplos PDFs (um por veículo)
                                    zip_bytes = generate_multi_vehicle_manuals_zip(vehicles_data, st.session_state.llm_integration)
                                    st.session_state.manual_zip_ready = zip_bytes
                                    st.session_state.manual_pdf_ready = None  # Limpar PDF único
                                else:
                                    # Gerar PDF único
                                    manual = st.session_state.llm_integration.generate_manual(
                                        route=route,
                                        arrival_times=arrival_times,
                                        total_distance=total_distance,
                                        total_time=total_time,
                                        is_multi_vehicle=False,
                                        vehicles_data=None
                                    )
                                    pdf_bytes = generate_manual_pdf(manual)
                                    st.session_state.manual_pdf_ready = pdf_bytes
                                    st.session_state.manual_zip_ready = None  # Limpar ZIP
                        
                        # Mostrar botão de download apropriado
                        if 'manual_zip_ready' in st.session_state and st.session_state.manual_zip_ready:
                            # Download ZIP com múltiplos PDFs
                            st.download_button(
                                label="💾 Download Manuais (ZIP)",
                                data=st.session_state.manual_zip_ready,
                                file_name="manuais_veiculos.zip",
                                mime="application/zip",
                                type="primary",
                                use_container_width=True,
                                key="download_manual_zip"
                            )
                        elif 'manual_pdf_ready' in st.session_state and st.session_state.manual_pdf_ready:
                            # Download PDF único
                            st.download_button(
                                label="💾 Download Manual PDF",
                                data=st.session_state.manual_pdf_ready,
                                file_name="manual_instrucoes.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True,
                                key="download_manual_final"
                            )
                    except ImportError:
                        st.button("📥 Baixar Manual de Instruções", key="gen_manual_fallback", type="secondary", use_container_width=True, disabled=True)
                        st.warning("⚠️ Biblioteca fpdf2 não instalada")
                
                # Botão Checklist
                with col2:
                    try:
                        from src.llm.utils.pdf_generator import generate_checklist_pdf
                        
                        if st.button("📝 Gerar Checklist Pré-Itinerário", key="gen_checklist_btn", type="secondary", use_container_width=True):
                            with st.spinner("Gerando checklist e preparando download..."):
                                checklist = st.session_state.llm_integration.generate_checklist(route)
                                pdf_bytes = generate_checklist_pdf(checklist)
                                st.session_state.checklist_pdf_ready = pdf_bytes
                        
                        # Mostrar botão de download se o PDF foi gerado
                        if 'checklist_pdf_ready' in st.session_state:
                            st.download_button(
                                label="💾 Download Checklist PDF",
                                data=st.session_state.checklist_pdf_ready,
                                file_name="checklist_pre_itinerario.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True,
                                key="download_checklist_final"
                            )
                    except ImportError:
                        st.button("📥 Baixar Checklist Pré-Itinerário", key="gen_checklist_fallback", type="secondary", use_container_width=True, disabled=True)
                        st.warning("⚠️ Biblioteca fpdf2 não instalada")
                
                # Coluna 3 vazia
                with col3:
                    pass
            
            # TAB 2: Roteiro Detalhado
            with tab2:
                st.markdown("#### 🗺️ Roteiro Detalhado e Resumo de Prioridades")
                st.markdown("Baixe o roteiro passo a passo e o resumo de prioridades em PDF.")
                
                col1, col2, col3 = st.columns(3)
                
                # Botão Roteiro
                with col1:
                    try:
                        from src.llm.utils.pdf_generator import generate_itinerary_pdf
                        
                        if st.button("📝 Gerar Roteiro Detalhado", key="gen_itinerary_btn", type="secondary", use_container_width=True):
                            with st.spinner("Gerando roteiro detalhado e preparando download..."):
                                # Verificar se é multi-veículo
                                if st.session_state.get('is_multi_vehicle', False) and vehicles_data:
                                    # Gerar ZIP com múltiplos PDFs (um por veículo)
                                    zip_bytes = st.session_state.llm_integration.generate_multi_vehicle_itineraries_zip(vehicles_data)
                                    st.session_state.itinerary_zip_ready = zip_bytes
                                    st.session_state.itinerary_pdf_ready = None  # Limpar PDF único
                                else:
                                    # Gerar PDF único
                                    itinerary = st.session_state.llm_integration.generate_itinerary(
                                        route=route,
                                        arrival_times=arrival_times,
                                        total_distance=total_distance,
                                        total_time=total_time
                                    )
                                    pdf_bytes = generate_itinerary_pdf(itinerary)
                                    st.session_state.itinerary_pdf_ready = pdf_bytes
                                    st.session_state.itinerary_zip_ready = None  # Limpar ZIP
                        
                        # Mostrar botão de download apropriado
                        if 'itinerary_zip_ready' in st.session_state and st.session_state.itinerary_zip_ready:
                            # Download ZIP com múltiplos PDFs
                            st.download_button(
                                label="💾 Download Roteiros (ZIP)",
                                data=st.session_state.itinerary_zip_ready,
                                file_name="roteiros_veiculos.zip",
                                mime="application/zip",
                                type="primary",
                                use_container_width=True,
                                key="download_itinerary_zip"
                            )
                        elif 'itinerary_pdf_ready' in st.session_state and st.session_state.itinerary_pdf_ready:
                            # Download PDF único
                            st.download_button(
                                label="💾 Download Roteiro PDF",
                                data=st.session_state.itinerary_pdf_ready,
                                file_name="roteiro_detalhado.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True,
                                key="download_itinerary_final"
                            )
                    except ImportError:
                        st.button("📥 Baixar Roteiro Detalhado", key="gen_itinerary_fallback", type="secondary", use_container_width=True, disabled=True)
                        st.warning("⚠️ Biblioteca fpdf2 não instalada")
                
                # Botão Prioridades
                with col2:
                    try:
                        from src.llm.utils.pdf_generator import generate_itinerary_pdf
                        
                        if st.button("📝 Gerar Resumo de Prioridades", key="gen_priorities_btn", type="secondary", use_container_width=True):
                            with st.spinner("Analisando prioridades e preparando download..."):
                                # Verificar se é multi-veículo
                                if st.session_state.get('is_multi_vehicle', False) and vehicles_data:
                                    # Gerar ZIP com múltiplos PDFs (um por veículo)
                                    zip_bytes = st.session_state.llm_integration.generate_multi_vehicle_priorities_zip(vehicles_data)
                                    st.session_state.priorities_zip_ready = zip_bytes
                                    st.session_state.priorities_pdf_ready = None  # Limpar PDF único
                                else:
                                    # Gerar PDF único
                                    priorities = st.session_state.llm_integration.generate_priority_summary(route, include_emojis=False)
                                    pdf_bytes = generate_itinerary_pdf(priorities, title="Resumo de Prioridades")
                                    st.session_state.priorities_pdf_ready = pdf_bytes
                                    st.session_state.priorities_zip_ready = None  # Limpar ZIP
                        
                        # Mostrar botão de download apropriado
                        if 'priorities_zip_ready' in st.session_state and st.session_state.priorities_zip_ready:
                            # Download ZIP com múltiplos PDFs
                            st.download_button(
                                label="💾 Download Prioridades (ZIP)",
                                data=st.session_state.priorities_zip_ready,
                                file_name="prioridades_veiculos.zip",
                                mime="application/zip",
                                type="primary",
                                use_container_width=True,
                                key="download_priorities_zip"
                            )
                        elif 'priorities_pdf_ready' in st.session_state and st.session_state.priorities_pdf_ready:
                            # Download PDF único
                            st.download_button(
                                label="💾 Download Prioridades PDF",
                                data=st.session_state.priorities_pdf_ready,
                                file_name="resumo_prioridades.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True,
                                key="download_priorities_final"
                            )
                    except ImportError:
                        st.button("📥 Baixar Resumo de Prioridades", key="gen_priorities_fallback", type="secondary", use_container_width=True, disabled=True)
                        st.warning("⚠️ Biblioteca fpdf2 não instalada")
                
                # Coluna 3 vazia
                with col3:
                    pass
            
            # Tab Telegram: QR Code
            with tab_telegram:
                try:
                    from src.utils.telegram_qrcode import render_telegram_qrcode_tab
                    render_telegram_qrcode_tab(st)
                except ImportError as e:
                    st.warning("⚠️ Módulo de QR Code do Telegram não disponível")
                    st.info(f"Erro: {e}")
                    st.markdown("""
                    **Para habilitar o QR Code do Telegram:**
                    
                    1. Instale a biblioteca qrcode:
                       ```bash
                       pip install qrcode[pil]
                       ```
                    
                    2. Configure o bot no arquivo `.env`:
                       ```
                       TELEGRAM_BOT_TOKEN=seu_token_aqui
                       TELEGRAM_BOT_USERNAME=seu_bot_username
                       ```
                    
                    3. Execute o bot: `python telegram_bot/bot.py`
                    
                    **Documentação completa:** `telegram_bot/README.md`
                    """)
            
            # TAB 3: Perguntas & Respostas
            with tab3:
                st.markdown("#### 💬 Faça Perguntas sobre a Rota")
                st.markdown("Pergunte qualquer coisa sobre a rota otimizada em linguagem natural.")
                
                # Sugestões de perguntas
                suggestions = st.session_state.llm_integration.get_suggested_questions(route)
                if suggestions:
                    st.markdown("**💡 Sugestões de perguntas:**")
                    cols = st.columns(2)
                    for idx, suggestion in enumerate(suggestions):
                        col = cols[idx % 2]
                        with col:
                            if st.button(f"❓ {suggestion}", key=f"suggest_{idx}", use_container_width=True):
                                # Processar pergunta diretamente ao clicar no botão
                                with st.spinner("Processando pergunta..."):
                                    answer = st.session_state.llm_integration.answer_question(
                                        question=suggestion,
                                        route=route,
                                        arrival_times=arrival_times,
                                        total_distance=total_distance,
                                        total_time=total_time
                                    )
                                    # Adicionar ao histórico
                                    if 'qa_history' not in st.session_state:
                                        st.session_state.qa_history = []
                                    st.session_state.qa_history.append({
                                        'question': suggestion,
                                        'answer': answer
                                    })
                                    st.rerun()
                
                # Campo de pergunta
                st.markdown("---")
                question = st.text_input(
                    "Digite sua pergunta:",
                    value='',
                    placeholder="Ex: Qual o próximo atendimento prioritário?",
                    key="question_input"
                )
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("🔍 Perguntar", key="ask_question", type="secondary", use_container_width=True):
                        if question:
                            with st.spinner("Processando pergunta..."):
                                answer = st.session_state.llm_integration.answer_question(
                                    question=question,
                                    route=route,
                                    arrival_times=arrival_times,
                                    total_distance=total_distance,
                                    total_time=total_time
                                )
                                # Adicionar ao histórico
                                if 'qa_history' not in st.session_state:
                                    st.session_state.qa_history = []
                                st.session_state.qa_history.append({
                                    'question': question,
                                    'answer': answer
                                })
                                st.rerun()
                        else:
                            st.warning("Por favor, digite uma pergunta.")
                
                with col2:
                    if st.button("🗑️ Limpar", key="clear_history", type="secondary", use_container_width=True):
                        st.session_state.llm_integration.clear_conversation_history()
                        if 'qa_history' in st.session_state:
                            st.session_state.qa_history = []
                        st.success("Histórico limpo!")
                
                # Coluna 3 vazia
                with col3:
                    pass
                
                # Exibir histórico de perguntas e respostas
                if 'qa_history' in st.session_state and st.session_state.qa_history:
                    st.markdown("---")
                    st.markdown("##### 📜 Histórico de Conversação:")
                    for idx, qa in enumerate(reversed(st.session_state.qa_history)):
                        with st.expander(f"❓ {qa['question']}", expanded=(idx == 0)):
                            st.markdown("**Resposta:**")
                            st.write(qa['answer'])
        
        else:
            # LLM não disponível
            st.warning("⚠️ Assistente de IA não disponível")
            st.info("""
            Para habilitar o Assistente de IA, configure sua chave API no arquivo `.env`:
            
            1. Renomeie o arquivo `.env.example` para `.env`
            2. Adicione sua chave da OpenAI em `OPENAI_API_KEY`
            3. Reinicie a aplicação
            
            Ou execute: `cp .env.example .env` e edite o arquivo `.env`
            """)
        
        st.divider()
        
        st.markdown("### 🔧 Opções")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Reiniciar", type="secondary", use_container_width=True):
                # Salvar configurações atuais antes de limpar
                current_num_vehicles = st.session_state.get('num_vehicles', 1)
                current_max_generations = st.session_state.get('max_generations', 10)
                
                # Limpar arquivos temporários
                temp_dir = '/tmp'
                for filename in ['service_points.pkl', 'progress.pkl', 'pygame_final.png', 'depot_location.pkl', 'vehicle_speed.pkl']:
                    filepath = os.path.join(temp_dir, filename)
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except:
                            pass
                
                # Limpar estado da sessão
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                # Restaurar configurações e marcar para auto-start
                st.session_state.num_vehicles = current_num_vehicles
                st.session_state.max_generations = current_max_generations
                st.session_state.optimization_done = False
                st.session_state.auto_start = True
                st.rerun()
        
        with col2:
            if st.button("🔧 Alterar Parâmetros Iniciais", type="secondary", use_container_width=True):
                # Limpar arquivos temporários
                temp_dir = '/tmp'
                for filename in ['service_points.pkl', 'progress.pkl', 'pygame_final.png', 'depot_location.pkl', 'vehicle_speed.pkl']:
                    filepath = os.path.join(temp_dir, filename)
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except:
                            pass
                
                # Limpar estado da sessão
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                # Voltar para tela inicial (sem auto-start)
                st.session_state.optimization_done = False
                st.rerun()
        
        with col3:
            if st.button("❌ Encerrar", type="secondary", use_container_width=True):
                # Limpar arquivos temporários
                temp_dir = '/tmp'
                for filename in ['service_points.pkl', 'progress.pkl', 'pygame_final.png', 'vehicle_speed.pkl']:
                    filepath = os.path.join(temp_dir, filename)
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except:
                            pass
                
                # Executar make clean em background
                import subprocess
                import threading
                
                def run_clean():
                    try:
                        # Executar make clean no diretório raiz do projeto
                        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                        result = subprocess.run(['make', 'clean'],
                                              check=False,
                                              cwd=project_root,
                                              capture_output=True,
                                              text=True)
                        print(f"Make clean executado: {result.returncode}")
                        if result.stdout:
                            print(f"Output: {result.stdout}")
                        if result.stderr:
                            print(f"Errors: {result.stderr}")
                    except Exception as e:
                        print(f"Erro ao executar make clean: {e}")
                    # Encerrar o servidor após limpeza
                    import signal
                    time.sleep(1)
                    os.kill(os.getpid(), signal.SIGTERM)
                
                # Mensagem de encerramento
                st.markdown("### 👋 Aplicação Encerrada")
                st.markdown("✅ Limpeza concluída!")
                st.markdown("Você pode fechar esta aba do navegador.")
                st.info("O servidor será encerrado em alguns segundos...")
                
                # Executar limpeza e encerramento em thread separada
                cleanup_thread = threading.Thread(target=run_clean)
                cleanup_thread.daemon = True
                cleanup_thread.start()
                
                # Parar execução do Streamlit
                st.stop()

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', force=True)
    main()

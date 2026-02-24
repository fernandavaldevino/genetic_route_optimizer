#!/usr/bin/env python3
"""
Interface Gráfica com Streamlit para o Sistema de Otimização de Rotas

Autor: Fernanda Valdevino - Projeto Fase 2
"""

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

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.genetic_algorithm import (
    calculate_constrained_fitness,
    generate_priority_aware_population,
    sort_population_by_fitness,
    constrained_order_crossover,
    constrained_mutate,
    calculate_route_time_and_distance
)
from core.service_points import create_service_point, ServicePriority

# Configuração da página
st.set_page_config(
    page_title="Otimizador de Rotas - AG",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Parâmetros do AG
N_POINTS = 20
POPULATION_SIZE = 100
MUTATION_PROBABILITY = 0.5
MAX_GENERATIONS = 200

# Cores por prioridade (em formato hex para Streamlit)
PRIORITY_COLORS = {
    ServicePriority.EMERGENCY_OBSTETRIC: "#FF0000",
    ServicePriority.DOMESTIC_VIOLENCE: "#FFA500",
    ServicePriority.HORMONAL_MEDICATION: "#0000FF",
    ServicePriority.POSTPARTUM_CARE: "#800080",
    ServicePriority.REGULAR: "#808080"
}

def create_random_service_points(n_points):
    """Cria pontos de atendimento aleatórios com diferentes tipos"""
    service_points = []
    
    depot_location = (
        random.randint(470, 1300),
        random.randint(100, 700)
    )
    depot = create_service_point(0, depot_location, 'regular', None)
    depot.service_duration = 0.0
    service_points.append(depot)
    
    types_guaranteed = [
        'emergency', 'emergency',
        'violence', 'violence',
        'medication', 'medication',
        'postpartum', 'postpartum'
    ]
    
    for i, service_type in enumerate(types_guaranteed):
        location = (
            random.randint(470, 1300),
            random.randint(100, 700)
        )
        
        time_window = None
        if service_type == 'violence':
            time_window = (480, 600)
        elif service_type == 'postpartum':
            time_window = (540, 660)
        
        point = create_service_point(i + 1, location, service_type, time_window)
        service_points.append(point)
    
    for i in range(len(types_guaranteed), n_points):
        location = (
            random.randint(470, 1300),
            random.randint(100, 700)
        )
        point = create_service_point(i + 1, location, 'regular', None)
        service_points.append(point)
    
    return service_points

def format_time(minutes):
    """Formata minutos em HH:MM"""
    hours = int(minutes // 60) % 24
    mins = int(minutes % 60)
    return f"{hours:02d}:{mins:02d}"

def get_day_from_minutes(minutes):
    """Retorna o dia a partir dos minutos"""
    return int(minutes // 1440) + 1

def run_pygame_2_vehicles(service_points_file, progress_file, screenshot_file, depot_location):
    """Executa visualização com 2 veículos - chama main_2v.py integrado"""
    import subprocess
    import sys
    
    # Caminho para o main_2v.py do projeto
    main_2v_path = os.path.join(os.path.dirname(__file__), 'main_2v.py')
    
    # Executar o main_2v.py
    print(f"\n{'='*60}")
    print("EXECUTANDO OTIMIZAÇÃO COM 2 VEÍCULOS")
    print(f"{'='*60}\n")
    
    result = subprocess.run(
        [sys.executable, main_2v_path],
        cwd=os.path.dirname(__file__),
        capture_output=False
    )
    
    print(f"\n{'='*60}")
    print("OTIMIZAÇÃO COM 2 VEÍCULOS FINALIZADA")
    print(f"{'='*60}\n")
    
    # NÃO sobrescrever os dados - o pygame_viewer_2v.py já salvou tudo corretamente
    # Os dados estão em progress_file e screenshot_file


def run_pygame_with_full_visualization(service_points_file, progress_file, screenshot_file):
    """Executa visualização completa do Pygame (1 veículo)"""
    # Importar módulo completo do pygame_viewer
    from visualization import pygame_viewer
    import pygame
    
    # Carregar pontos
    with open(service_points_file, 'rb') as f:
        service_points = pickle.load(f)
    
    # Executar visualização completa (código do pygame_viewer.py adaptado)
    pygame.init()
    WIDTH, HEIGHT = 1400, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Roteamento com Restricoes - AG")
    clock = pygame.time.Clock()
    FPS = 10
    
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
        
        # Verificar se atingiu o critério de parada
        if generation >= MAX_GENERATIONS and not optimization_complete:
            optimization_complete = True
            # Salvar screenshot final
            pygame.image.save(screen, screenshot_file)
        
        # Se otimização completa, mostrar tela de conclusão
        if optimization_complete:
            # Desenhar tela de conclusão
            from visualization.pygame_viewer import draw_completion_screen
            draw_completion_screen(screen, generation, best_fitness, best_route, arrival_times, service_points)
            pygame.display.flip()
            
            # Salvar screenshot final
            pygame.image.save(screen, screenshot_file)
            
            # Aguardar um pouco antes de fechar
            time.sleep(2)
            running = False
            continue
        
        # Limpar tela
        screen.fill((255, 255, 255))
        
        # Calcular fitness
        fitness_values = [calculate_constrained_fitness(route) for route in population]
        
        # Ordenar população
        population, fitness_values = sort_population_by_fitness(population, fitness_values)
        
        best_fitness = fitness_values[0]
        best_route = population[0]
        
        best_fitness_history.append(best_fitness)
        
        # Calcular tempos de chegada
        _, _, arrival_times = calculate_route_time_and_distance(best_route)
        
        # Desenhar visualização completa
        from visualization.pygame_viewer import (
            draw_info_panel, draw_simple_plot, draw_route, 
            draw_service_points, NODE_RADIUS
        )
        
        # Desenhar painel de informações
        draw_info_panel(screen, generation, best_fitness, best_route, arrival_times)
        
        # Desenhar gráfico de evolução
        if len(best_fitness_history) > 1:
            draw_simple_plot(
                screen,
                list(range(len(best_fitness_history))),
                best_fitness_history,
                best_route,
                best_fitness,
                arrival_times
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

def display_results(best_route, best_fitness, arrival_times):
    """Exibe os resultados da otimização"""
    
    last_service_arrival = arrival_times[-1]
    max_day = get_day_from_minutes(last_service_arrival)
    time_str = format_time(last_service_arrival)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Fitness", f"{best_fitness:.2f}")
    
    with col2:
        if max_day == 1:
            st.metric("Dias para Entrega", f"{max_day} dia", delta="Ótimo", delta_color="normal")
        elif max_day == 2:
            st.metric("Dias para Entrega", f"{max_day} dias", delta="Aceitável", delta_color="off")
        else:
            st.metric("Dias para Entrega", f"{max_day} dias", delta="Atenção", delta_color="inverse")
    
    with col3:
        st.metric("Horário da Última Entrega", time_str)
    
    st.divider()
    
    # Ordem de Prioridades para Atendimento
    st.subheader("🎯 Ordem de Prioridades para Atendimento")
    
    priority_abbr = {
        ServicePriority.EMERGENCY_OBSTETRIC: "EME",
        ServicePriority.DOMESTIC_VIOLENCE: "VIO",
        ServicePriority.HORMONAL_MEDICATION: "MED",
        ServicePriority.POSTPARTUM_CARE: "POS",
        ServicePriority.REGULAR: "REG"
    }
    
    priority_names = {
        ServicePriority.EMERGENCY_OBSTETRIC: "Emergência Obstétrica",
        ServicePriority.DOMESTIC_VIOLENCE: "Violência Doméstica",
        ServicePriority.HORMONAL_MEDICATION: "Medicamento Hormonal",
        ServicePriority.POSTPARTUM_CARE: "Pós-Parto",
        ServicePriority.REGULAR: "Regular"
    }
    
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
            
            color = PRIORITY_COLORS[priority]
            st.markdown(f":{color}[●] **{priority_names[priority]} ({priority_abbr[priority]})** - {ids_str}")
    
    st.divider()
    
    st.subheader("📋 Melhor Solução Encontrada")
    route_without_depot = [p for p in best_route if p.id != 0]
    route_ids = [str(p.id) for p in route_without_depot]
    st.code(f"[ {', '.join(route_ids)} ]", language=None)

def display_results_multi_vehicle(best_solution, best_fitness):
    """Exibe os resultados da otimização com múltiplos veículos"""
    
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
        st.metric("Fitness Total", f"{best_fitness:.2f}")
    
    with col2:
        total_points = sum(len(v.route) for v in best_solution.vehicles)
        st.metric("Total de Pontos", total_points)
    
    with col3:
        total_distance = sum(v.total_distance for v in best_solution.vehicles)
        st.metric("Distância Total", f"{total_distance:.0f}")
    
    st.divider()
    
    # Informações dos veículos
    st.subheader("🚗 Informações dos Veículos")
    
    cols = st.columns(len(best_solution.vehicles))
    
    for i, vehicle in enumerate(best_solution.vehicles):
        with cols[i]:
            st.markdown(f"### :green[Veículo {vehicle.vehicle_id}]")
            st.metric("Pontos Atendidos", len(vehicle.route))
            st.metric("Distância", f"{vehicle.total_distance:.0f}")
            
            # Converter tempo de minutos para horas e minutos
            hours = int(vehicle.total_time // 60)
            minutes = int(vehicle.total_time % 60)
            st.metric("Tempo Total", f"{hours}h{minutes:02d}")
    
    st.divider()
    
    # Ordem de Prioridades para Atendimento
    st.subheader("🎯 Ordem de Prioridades para Atendimento")
    
    priority_abbr = {
        ServicePriority.EMERGENCY_OBSTETRIC: "EME",
        ServicePriority.DOMESTIC_VIOLENCE: "VIO",
        ServicePriority.HORMONAL_MEDICATION: "MED",
        ServicePriority.POSTPARTUM_CARE: "POS",
        ServicePriority.REGULAR: "REG"
    }
    
    priority_names = {
        ServicePriority.EMERGENCY_OBSTETRIC: "Emergência Obstétrica",
        ServicePriority.DOMESTIC_VIOLENCE: "Violência Doméstica",
        ServicePriority.HORMONAL_MEDICATION: "Medicamento Hormonal",
        ServicePriority.POSTPARTUM_CARE: "Pós-Parto",
        ServicePriority.REGULAR: "Regular"
    }
    
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
    
    for vehicle in best_solution.vehicles:
        st.markdown(f"**Veículo {vehicle.vehicle_id}:**")
        
        # Criar HTML com IDs coloridos por prioridade
        html_parts = ["<div style='font-family: monospace; font-size: 16px; padding: 10px; background-color: #0e1117; border-radius: 5px;'>[ "]
        
        for i, point in enumerate(vehicle.route):
            color = PRIORITY_COLORS_HTML.get(point.priority, "#000000")
            html_parts.append(f"<span style='color: {color}; font-weight: bold;'>{point.id}</span>")
            
            if i < len(vehicle.route) - 1:
                html_parts.append(", ")
        
        html_parts.append(" ]</div>")
        
        st.markdown("".join(html_parts), unsafe_allow_html=True)


def main():
    """Função principal da aplicação Streamlit"""
    
    st.title("🚗 Sistema de Otimização de Rotas com Restrições")
    st.markdown("**Algoritmo Genético para Roteamento de Atendimentos em Saúde da Mulher**")
    
    # Placeholder para sidebar (será preenchido depois)
    sidebar_placeholder = st.sidebar.empty()
    
    if 'optimization_done' not in st.session_state:
        st.session_state.optimization_done = False
    
    if 'num_vehicles' not in st.session_state:
        st.session_state.num_vehicles = 1
    
    if not st.session_state.optimization_done:
        # Verificar se deve auto-iniciar (após Reiniciar)
        auto_start = st.session_state.get('auto_start', False)
        
        if not auto_start:
            st.markdown("### 🚀 Configuração da Otimização")
            
            # CSS para aumentar o tamanho das fontes do radio button
            st.markdown("""
            <style>
            div[role="radiogroup"] label {
                font-size: 1.2rem !important;
                font-weight: 500 !important;
            }
            div[role="radiogroup"] label p {
                font-size: 1.2rem !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Criar duas colunas: uma para o seletor, outra para o texto de restrições
            col_selector, col_restriction = st.columns([1, 1.5])
            
            with col_selector:
                # Seletor de número de veículos
                num_vehicles = st.radio(
                    "**Escolha o número de veículos:**",
                    options=[1, 2],
                    format_func=lambda x: f"🚗 {x} veículo" if x == 1 else f"🚗🚗 {x} veículos",
                    horizontal=True,
                    help="1 veículo: Otimização tradicional | 2 veículos: Otimização multi-veículo com depósito",
                    key='num_vehicles_radio'
                )
                st.session_state.num_vehicles = num_vehicles
            
            with col_restriction:
                # Texto de restrição de medicamentos prioritários depende do número de veículos
                if num_vehicles == 1:
                    # Usar HTML para fonte maior e destaque (na mesma linha)
                    restriction_html = """
                    <div style='margin-top: 20px;'>
                        <span style='font-size: 18px; font-weight: 600;'>Medicamentos prioritários entregues </span>
                        <span style='font-size: 24px; font-weight: 700; color: #FF8C00; background-color: rgba(255, 140, 0, 0.1); padding: 4px 8px; border-radius: 4px;'>até o 1º dia</span>
                    </div>
                    """
                else:  # 2 veículos
                    restriction_html = """
                    <div style='margin-top: 20px;'>
                        <span style='font-size: 18px; font-weight: 600;'>Medicamentos prioritários entregues </span>
                        <span style='font-size: 24px; font-weight: 700; color: #FF8C00; background-color: rgba(255, 140, 0, 0.1); padding: 4px 8px; border-radius: 4px;'>até 12:00</span>
                    </div>
                    """
                
                st.markdown(restriction_html, unsafe_allow_html=True)
            
            st.divider()
            st.markdown("Clique no botão abaixo para iniciar o processo de otimização de rotas.")
    
    # Preencher sidebar com informações (agora que num_vehicles está definido)
    with sidebar_placeholder.container():
        st.header("ℹ️ Informações do Sistema")
        
        st.markdown("### 🧬 Parâmetros do Algoritmo Genético")
        st.markdown("""
        - **Pontos de Atendimento:** 20
        - **Tamanho da População:** 100
        - **Gerações Máximas:** 200
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
        
        # Texto de restrição de medicamentos prioritários depende do número de veículos
        if num_vehicles == 1:
            priority_restriction = "Devem ser entregues no :orange[**1º dia**]"
        else:  # 2 veículos
            priority_restriction = "Devem ser entregues até :orange[**12:00h**]"
        
        st.markdown(f"""
        - **Horário Comercial:** 8h às 18h
        - **Medicamentos prioritários:** {priority_restriction}
        - **Emergência Obstétrica:** Prioridade máxima
        - **Violência Doméstica:** 8h às 10h
        - **Pós-Parto:** 9h às 11h
        - **Medicamentos Hormonais:** Controle de temperatura
        """)
    
    if not st.session_state.optimization_done:
        if st.button("▶️ Start", type="primary", use_container_width=True) or auto_start:
            # Limpar flag de auto_start
            if 'auto_start' in st.session_state:
                del st.session_state['auto_start']
            
            # Obter número de veículos selecionado
            num_vehicles = st.session_state.num_vehicles
            
            # Arquivos temporários
            temp_dir = '/tmp'
            service_points_file = os.path.join(temp_dir, 'service_points.pkl')
            progress_file = os.path.join(temp_dir, 'progress.pkl')
            screenshot_file = os.path.join(temp_dir, 'pygame_final.png')
            depot_file = os.path.join(temp_dir, 'depot_location.pkl')
            
            # Limpar arquivos antigos
            for filepath in [progress_file, screenshot_file, depot_file]:
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except:
                        pass
            
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
                        random.randint(470, 1300),
                        random.randint(100, 700)
                    )
                    
                    time_window = None
                    if service_type == 'violence':
                        time_window = (480, 600)
                    elif service_type == 'postpartum':
                        time_window = (540, 660)
                    
                    point = create_service_point(i + 1, location, service_type, time_window)
                    service_points.append(point)
                
                for i in range(len(types_guaranteed), N_POINTS):
                    location = (
                        random.randint(470, 1300),
                        random.randint(100, 700)
                    )
                    point = create_service_point(i + 1, location, 'regular', None)
                    service_points.append(point)
                
                # Criar depósito separado
                depot_location = (
                    random.randint(470, 1300),
                    random.randint(100, 700)
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
                    args=(service_points_file, progress_file, screenshot_file)
                )
            else:  # 2 veículos
                with open(depot_file, 'rb') as f:
                    depot_location = pickle.load(f)
                pygame_process = multiprocessing.Process(
                    target=run_pygame_2_vehicles,
                    args=(service_points_file, progress_file, screenshot_file, depot_location)
                )
            
            pygame_process.start()
            
            # Monitorar progresso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            while pygame_process.is_alive():
                try:
                    if os.path.exists(progress_file):
                        with open(progress_file, 'rb') as f:
                            progress_data = pickle.load(f)
                        
                        generation = progress_data.get('generation', 0)
                        best_fitness = progress_data.get('best_fitness', 0)
                        
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
                'Geração': list(range(len(st.session_state.fitness_history))),
                'Fitness': st.session_state.fitness_history
            })
            st.line_chart(df.set_index('Geração'), width='stretch')
            
            # Verificar se há dados no histórico antes de acessar
            if st.session_state.fitness_history and len(st.session_state.fitness_history) > 0:
                col1, col2, col3, col4 = st.columns(4)
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
        
        st.markdown("### 🔧 Opções")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Reiniciar", type="secondary", use_container_width=True):
                # Salvar número de veículos atual antes de limpar
                current_num_vehicles = st.session_state.get('num_vehicles', 1)
                
                # Limpar arquivos temporários
                temp_dir = '/tmp'
                for filename in ['service_points.pkl', 'progress.pkl', 'pygame_final.png', 'depot_location.pkl']:
                    filepath = os.path.join(temp_dir, filename)
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except:
                            pass
                
                # Limpar estado da sessão
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                # Restaurar número de veículos e marcar para auto-start
                st.session_state.num_vehicles = current_num_vehicles
                st.session_state.optimization_done = False
                st.session_state.auto_start = True
                st.rerun()
        
        with col2:
            if st.button("🔧 Alterar Veículos", type="secondary", use_container_width=True):
                # Limpar arquivos temporários
                temp_dir = '/tmp'
                for filename in ['service_points.pkl', 'progress.pkl', 'pygame_final.png', 'depot_location.pkl']:
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
                for filename in ['service_points.pkl', 'progress.pkl', 'pygame_final.png']:
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
                        subprocess.run(['make', 'clean'], check=False, cwd=os.path.dirname(os.path.abspath(__file__)))
                    except:
                        pass
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

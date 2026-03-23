"""
Constantes centralizadas do projeto de otimização de rotas
Todas as constantes de configuração do sistema estão definidas aqui
"""

# ============================================================================
# CONSTANTES DO ALGORITMO GENÉTICO
# ============================================================================

# Parâmetros principais do AG
N_POINTS = 20                    # Número total de pontos de atendimento
POPULATION_SIZE = 100            # Tamanho da população
MUTATION_PROBABILITY = 0.3       # Probabilidade de mutação (1 veículo)
MUTATION_PROBABILITY_2V = 0.5    # Probabilidade de mutação (2 veículos)
MAX_GENERATIONS = 100            # Critério de parada (gerações máximas)
VEHICLE_SPEED = 60.0             # Velocidade dos veículos em km/h

# Parâmetros específicos para 2 veículos
NUM_VEHICLES = 2                 # Número de veículos (modo multi-veículo)
POPULATION_SIZE_2V = 150         # Tamanho da população para 2 veículos

# ============================================================================
# CONSTANTES DE VISUALIZAÇÃO PYGAME
# ============================================================================

# Dimensões da tela
WIDTH = 1400
HEIGHT = 800
NODE_RADIUS = 12                 # Raio dos círculos dos pontos de atendimento
FPS = 10                         # Frames por segundo

# Áreas da tela
INFO_PANEL_WIDTH = 350
MAP_X_START = INFO_PANEL_WIDTH + 20
MAP_WIDTH = WIDTH - MAP_X_START - 20
MAP_HEIGHT = HEIGHT - 20

# Área do gráfico de evolução
PLOT_X_START = 10
PLOT_Y_START = 500               # Posição do gráfico
PLOT_WIDTH = INFO_PANEL_WIDTH - 20
PLOT_HEIGHT = 180                # Altura do gráfico (1 veículo)
PLOT_HEIGHT_2V = 150             # Altura do gráfico (2 veículos)

# ============================================================================
# CORES RGB (PYGAME)
# ============================================================================

# Cores básicas
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

# ============================================================================
# CORES POR PRIORIDADE (PYGAME)
# ============================================================================

# Importar ServicePriority para mapeamento
from src.core.service_points import ServicePriority

PRIORITY_COLORS = {
    ServicePriority.EMERGENCY_OBSTETRIC: RED,
    ServicePriority.DOMESTIC_VIOLENCE: ORANGE,
    ServicePriority.HORMONAL_MEDICATION: BLUE,
    ServicePriority.POSTPARTUM_CARE: PURPLE,
    ServicePriority.REGULAR: GRAY
}

# ============================================================================
# CORES POR VEÍCULO (PYGAME - MODO MULTI-VEÍCULO)
# ============================================================================

VEHICLE_COLORS = {
    1: DARK_GREEN,  # Veículo 1: Verde escuro
    2: CYAN         # Veículo 2: Ciano
}

# ============================================================================
# CORES HEXADECIMAIS (STREAMLIT/WEB)
# ============================================================================

# Cores por prioridade em formato hexadecimal
PRIORITY_COLORS_HEX = {
    ServicePriority.EMERGENCY_OBSTETRIC: "#FF0000",  # Vermelho
    ServicePriority.DOMESTIC_VIOLENCE: "#FFA500",    # Laranja
    ServicePriority.HORMONAL_MEDICATION: "#0000FF",  # Azul
    ServicePriority.POSTPARTUM_CARE: "#800080",      # Roxo
    ServicePriority.REGULAR: "#808080"               # Cinza
}

# Cores por veículo em formato hexadecimal
VEHICLE_COLORS_HEX = {
    1: "#009600",  # Verde escuro
    2: "#00C8C8"   # Ciano
}

# ============================================================================
# CORES NOMEADAS (STREAMLIT)
# ============================================================================

PRIORITY_COLORS_STREAMLIT = {
    ServicePriority.EMERGENCY_OBSTETRIC: "red",
    ServicePriority.DOMESTIC_VIOLENCE: "orange",
    ServicePriority.HORMONAL_MEDICATION: "blue",
    ServicePriority.POSTPARTUM_CARE: "violet",
    ServicePriority.REGULAR: "gray"
}

# ============================================================================
# ABREVIAÇÕES DE PRIORIDADES
# ============================================================================

PRIORITY_ABBREVIATIONS = {
    ServicePriority.EMERGENCY_OBSTETRIC: "EME",
    ServicePriority.DOMESTIC_VIOLENCE: "VIO",
    ServicePriority.HORMONAL_MEDICATION: "MED",
    ServicePriority.POSTPARTUM_CARE: "POS",
    ServicePriority.REGULAR: "REG"
}

# ============================================================================
# NOMES COMPLETOS DE PRIORIDADES
# ============================================================================

PRIORITY_NAMES = {
    ServicePriority.EMERGENCY_OBSTETRIC: "Emergência Obstétrica",
    ServicePriority.DOMESTIC_VIOLENCE: "Violência Doméstica",
    ServicePriority.HORMONAL_MEDICATION: "Medicamento Hormonal",
    ServicePriority.POSTPARTUM_CARE: "Pós-Parto",
    ServicePriority.REGULAR: "Regular"
}

# ============================================================================
# RESTRIÇÕES DE TEMPO
# ============================================================================

# Horários em minutos desde 00:00
WORK_START_TIME = 480            # 8h (8 * 60)
WORK_END_TIME = 1080             # 18h (18 * 60)
MINUTES_PER_DAY = 1440           # 24h em minutos

# Janelas de tempo para tipos específicos (1 veículo)
VIOLENCE_TIME_WINDOW = (480, 720)      # 8h às 12h (4h)
POSTPARTUM_TIME_WINDOW = (540, 780)    # 9h às 13h (4h)

# Janelas de tempo para tipos específicos (2 veículos)
VIOLENCE_TIME_WINDOW_2V = (480, 600)   # 8h às 10h (2h)
POSTPARTUM_TIME_WINDOW_2V = (540, 660) # 9h às 11h (2h)

# Deadlines de prioridade
PRIORITY_DEADLINE_1V = 1440.0    # Fim do Dia 1 (1 veículo)
PRIORITY_DEADLINE_2V = 720.0     # 12:00h (2 veículos)

# ============================================================================
# CONFIGURAÇÕES DE GERAÇÃO DE PONTOS
# ============================================================================

# Tipos garantidos de atendimento (sempre presentes)
GUARANTEED_SERVICE_TYPES = [
    'emergency', 'emergency',      # 2 emergências
    'violence', 'violence',        # 2 violência doméstica
    'medication', 'medication',    # 2 medicamentos
    'postpartum', 'postpartum'     # 2 pós-parto
]

# Limites de coordenadas para geração de pontos (Pygame)
COORD_MIN_X = 470
COORD_MAX_X = 1300
COORD_MIN_Y = 100
COORD_MAX_Y = 700

# Limites de coordenadas para mapa (Pygame - 1 veículo)
MAP_COORD_MIN_X = MAP_X_START + NODE_RADIUS + 20
MAP_COORD_MAX_X = WIDTH - NODE_RADIUS - 20
MAP_COORD_MIN_Y = NODE_RADIUS + 20
MAP_COORD_MAX_Y = HEIGHT - NODE_RADIUS - 20

# Limites de coordenadas para mapa (Pygame - 2 veículos)
MAP_COORD_MIN_X_2V = MAP_X_START + NODE_RADIUS + 80
MAP_COORD_MAX_X_2V = WIDTH - NODE_RADIUS - 20

# Distância mínima do depósito (2 veículos)
MIN_DEPOT_DISTANCE = 100

# ============================================================================
# MENSAGENS DO SISTEMA (LLM)
# ============================================================================

# System messages para diferentes geradores LLM
QA_SYSTEM_MESSAGE = """
Você é um assistente inteligente especializado em rotas de atendimento de saúde da mulher.
Você tem acesso às informações da rota otimizada e pode responder perguntas sobre ela
em linguagem natural.

Seja preciso, objetivo e útil. Se não souber a resposta, diga claramente.
"""

MANUAL_SYSTEM_MESSAGE = """
Você é um especialista em saúde da mulher e logística de atendimento médico.
Sua função é criar manuais práticos e sensíveis para equipes de transporte
que realizam atendimentos domiciliares relacionados à saúde da mulher.

Seja claro, empático e prático. Considere as particularidades de cada tipo
de atendimento e forneça instruções específicas e acionáveis.
"""

ROUTE_SYSTEM_MESSAGE = """
Você é um assistente especializado em criar roteiros de visitas claros e práticos
para equipes de saúde. Transforme sequências numéricas de pontos em roteiros
legíveis e úteis para o dia a dia da equipe.
"""

# ============================================================================
# PERGUNTAS COMUNS (Q&A)
# ============================================================================

COMMON_QUESTIONS = {
    "distancia_total": "Qual a distância total da rota?",
    "emergencias": "Quantas paradas de emergência temos hoje?",
    "tempo_total": "Quanto tempo vai levar a rota completa?",
    "medicamentos": "Quais paradas envolvem entrega de medicamentos?",
    "pos_parto": "Quantos atendimentos pós-parto temos?",
    "violencia": "Há casos de violência doméstica na rota?",
}

# ============================================================================
# CONFIGURAÇÕES DE ARQUIVOS TEMPORÁRIOS
# ============================================================================

TEMP_DIR = '/tmp'
SERVICE_POINTS_FILE = 'service_points.pkl'
PROGRESS_FILE = 'progress.pkl'
SCREENSHOT_FILE = 'pygame_final.png'
DEPOT_FILE = 'depot_location.pkl'

# ============================================================================
# CONFIGURAÇÕES DE SELEÇÃO E EVOLUÇÃO (AG)
# ============================================================================

TOURNAMENT_SIZE = 5              # Tamanho do torneio para seleção
ELITE_SIZE = 1                   # Número de indivíduos elite (1 veículo)
ELITE_SIZE_2V = 10               # Número de indivíduos elite (2 veículos)

# Torneio adaptativo (2 veículos)
TOURNAMENT_SIZE_EARLY = 7        # Início: pressão seletiva alta
TOURNAMENT_SIZE_MID = 5          # Meio: pressão moderada
TOURNAMENT_SIZE_LATE = 3         # Final: mais diversidade

# Thresholds para torneio adaptativo (% de gerações)
TOURNAMENT_EARLY_THRESHOLD = 0.3  # Primeiros 30%
TOURNAMENT_MID_THRESHOLD = 0.7    # 30% a 70%

# Mutação dinâmica (2 veículos)
MUTATION_RATE_INITIAL = 0.7      # Taxa inicial de mutação (70%) - alta para exploração
MUTATION_RATE_FINAL = 0.2        # Taxa final de mutação (20%)

# Elitismo dinâmico (2 veículos)
ELITE_SIZE_INITIAL = 5           # Elitismo inicial (5 indivíduos)
ELITE_SIZE_FINAL = 10            # Elitismo final (10 indivíduos)

# Diversidade genética
DIVERSITY_THRESHOLD_LOW = 0.1    # Limiar de baixa diversidade (aumentar mutação)
DIVERSITY_THRESHOLD_HIGH = 0.5   # Limiar de alta diversidade (diminuir mutação)

# Simulated Annealing
INITIAL_TEMPERATURE = 100.0      # Temperatura inicial
FINAL_TEMPERATURE = 0.1          # Temperatura final
COOLING_RATE = 0.95              # Taxa de resfriamento

# Otimização 2-opt adaptativa
OPT2_INTERVAL_EARLY = 5          # A cada 5 gerações (0-100)
OPT2_INTERVAL_MID = 15           # A cada 15 gerações (100-300)
OPT2_INTERVAL_LATE = 30          # A cada 30 gerações (300+)
OPT2_EARLY_THRESHOLD = 100       # Threshold para fase inicial
OPT2_MID_THRESHOLD = 300         # Threshold para fase média

# Reinjeção de diversidade
STAGNATION_THRESHOLD = 30        # Gerações sem melhoria para detectar estagnação
DIVERSITY_INJECTION_MIN = 0.2    # Substituir 20% da população (estagnação leve)
DIVERSITY_INJECTION_MAX = 0.5    # Substituir 50% da população (estagnação severa)

# Geração guiada
GUIDED_GENERATION_THRESHOLD = 150  # Gerações sem melhoria para ativar geração guiada
GUIDED_TOP_SOLUTIONS = 5          # Número de melhores soluções para gerar novas

# Otimização forçada (cruzamentos)
FORCED_OPT_PASSES = 5             # Número de passadas 2-opt quando há cruzamentos

# ============================================================================
# CONFIGURAÇÕES DE VISUALIZAÇÃO
# ============================================================================

# Tamanhos de fonte (Pygame)
FONT_SIZE_TITLE = 26
FONT_SIZE_SUBTITLE = 18
FONT_SIZE_TEXT = 18
FONT_SIZE_SMALL = 14

# Margens e espaçamentos
MARGIN_LEFT = 60
MARGIN_RIGHT = 10
MARGIN_TOP = 25
MARGIN_BOTTOM = 25
LINE_HEIGHT = 22

# Configurações de setas (2 veículos)
ARROW_WIDTH = 3
ARROW_SIZE = 12
ARROW_SIZE_SMALL = 6
ARROW_MARGIN = 2

# ============================================================================
# CONVERSÕES E FATORES
# ============================================================================

DISTANCE_TO_KM_FACTOR = 0.1      # Fator de conversão de distância para km
SPEED_KM_PER_MIN = 1.0           # Velocidade padrão em km/min (60 km/h ÷ 60 = 1.0)
                                 # NOTA: Esta constante é mantida para compatibilidade,
                                 # mas a velocidade real é parametrizada pelo usuário

# ============================================================================
# OPÇÕES DE GERAÇÕES (STREAMLIT)
# ============================================================================

GENERATION_OPTIONS = [10, 100, 200, 500, 1000, 2000, 5000, 10000, 15000, 20000]
DEFAULT_GENERATION_INDEX = 0     # Índice padrão (10 gerações)

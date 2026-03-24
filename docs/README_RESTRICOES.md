# Sistema de Roteamento com Restrições e Prioridades

## 📑 Índice

- [Visão Geral](#visão-geral)
- [Estrutura de Arquivos](#estrutura-de-arquivos)
  - [1. src/core/service_points.py](#1-srccoreservice_pointspy)
  - [2. src/core/genetic_algorithm.py](#2-srccoregenetic_algorithmpy)
  - [3. src/visualization/pygame_viewer.py](#3-srcvisualizationpygame_viewerpy)
- [Como Usar](#como-usar)
  - [Instalação](#instalação)
  - [Execução](#execução)
  - [Exemplo Básico](#exemplo-básico)
- [Restrições Implementadas](#restrições-implementadas)
  - [1. Ordem de Prioridade](#1-ordem-de-prioridade)
  - [2. Casos de Violência Doméstica](#2-casos-de-violência-doméstica)
  - [3. Medicamentos Hormonais](#3-medicamentos-hormonais)
  - [4. Atendimento Pós-Parto](#4-atendimento-pós-parto)
- [Função de Fitness](#função-de-fitness)
  - [Pesos das Penalidades](#pesos-das-penalidades)
- [Parâmetros Configuráveis](#parâmetros-configuráveis)
  - [Em src/core/service_points.py](#em-srccoreservice_pointspy)
  - [Em src/core/genetic_algorithm.py](#em-srccoregenetic_algorithmpy)
- [Executando os Testes](#executando-os-testes)
- [Saída Esperada](#saída-esperada)
- [Integração com Interface Gráfica](#integração-com-interface-gráfica)
- [Referências](#referências)

---

## Visão Geral

Este sistema estende o algoritmo genético para TSP (Traveling Salesman Problem) para incluir restrições específicas de atendimento em saúde da mulher, considerando:

- **Ordem de prioridade** para diferentes pontos de atendimento
- **Janelas de tempo específicas** para cada tipo de atendimento
- **Requisitos especiais** como temperatura controlada e protocolos de segurança
- **Penalizações** por violação de restrições

## Estrutura de Arquivos

### 1. [`src/core/service_points.py`](../src/core/service_points.py)
Define as estruturas de dados e validações:

- **`ServicePriority`**: Enum com níveis de prioridade
  - `EMERGENCY_OBSTETRIC` (1) - Prioridade máxima
  - `DOMESTIC_VIOLENCE` (2) - Protocolos especiais
  - `HORMONAL_MEDICATION` (3) - Temperatura controlada
  - `POSTPARTUM_CARE` (4) - Janelas de tempo específicas
  - `REGULAR` (5) - Atendimento regular

- **`TimeWindow`**: Gerencia janelas de tempo para atendimentos
- **`ServicePoint`**: Representa um ponto de atendimento com todas suas características
- **Funções de validação**: Verificam temperatura controlada e protocolos especiais

### 2. [`src/core/genetic_algorithm.py`](../src/core/genetic_algorithm.py)
Implementa o algoritmo genético com restrições:

- **`calculate_constrained_fitness()`**: Função de fitness que considera todas as restrições
- **`generate_priority_aware_population()`**: Gera população inicial com viés para prioridades
- **`constrained_order_crossover()`**: Crossover que preserva blocos de alta prioridade
- **`constrained_mutate()`**: Mutação que respeita restrições de prioridade

### 3. [`src/visualization/pygame_viewer.py`](../src/visualization/pygame_viewer.py)
Interface gráfica com Pygame:

- Visualização em tempo real da evolução
- Gráfico de Evolução do Fitness com marcador da última geração em que ocorreu otimização
- Mapa de rotas colorido por prioridade
- Painel de informações detalhadas

## Como Usar

### Instalação

```bash
# Opção 1: Usando Makefile (Recomendado)
make install

# Opção 2: Manual
python3 -m venv ga_routes
source ga_routes/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Execução

```bash
# Opção 1: Usando Makefile
make run

# Opção 2: Manual
python app/main.py
```

### Exemplo Básico

```python
from src.core.service_points import create_service_point
from src.core.genetic_algorithm import (
    generate_priority_aware_population,
    calculate_constrained_fitness,
    sort_population_by_fitness,
    constrained_order_crossover,
    constrained_mutate
)

# 1. Criar pontos de atendimento
service_points = [
    # Emergência obstétrica (prioridade máxima)
    create_service_point(1, (100, 200), 'emergency'),
    
    # Caso de violência doméstica (protocolo especial)
    # Janela de tempo: 8h às 10h (480-600 minutos)
    create_service_point(2, (300, 400), 'violence', time_window=(480, 600)),
    
    # Medicamento hormonal (temperatura controlada)
    create_service_point(3, (500, 100), 'medication'),
    
    # Atendimento pós-parto (janela específica: 9h às 11h)
    create_service_point(4, (200, 300), 'postpartum', time_window=(540, 660)),
    
    # Atendimento regular
    create_service_point(5, (400, 500), 'regular'),
]

# 2. Configurar parâmetros do algoritmo genético
POPULATION_SIZE = 50
N_GENERATIONS = 100
MUTATION_PROBABILITY = 0.3

# 3. Gerar população inicial (com viés para prioridades)
population = generate_priority_aware_population(service_points, POPULATION_SIZE)

# 4. Executar algoritmo genético
for generation in range(N_GENERATIONS):
    # Calcular fitness considerando todas as restrições
    fitness_values = [calculate_constrained_fitness(route) for route in population]
    
    # Ordenar população (menor fitness = melhor)
    population, fitness_values = sort_population_by_fitness(population, fitness_values)
    
    # Criar nova população
    new_population = [population[0]]  # Elitismo
    
    while len(new_population) < POPULATION_SIZE:
        # Seleção
        parent1, parent2 = random.sample(population[:10], 2)
        
        # Crossover com preservação de prioridades
        child = constrained_order_crossover(parent1, parent2)
        
        # Mutação respeitando restrições
        child = constrained_mutate(child, MUTATION_PROBABILITY)
        
        new_population.append(child)
    
    population = new_population

# 5. Obter melhor solução
best_route = population[0]
best_fitness = fitness_values[0]
```

## Restrições Implementadas

### 1. Ordem de Prioridade

O sistema segue uma ordem estrita de prioridades na hora de montar a rota: **EME → VIO → MED → POS → REG**

```python
# Ordem de prioridades (do mais urgente ao menos urgente)
priority_order = [
    ServicePriority.EMERGENCY_OBSTETRIC,      # Prioridade 1
    ServicePriority.DOMESTIC_VIOLENCE,        # Prioridade 2
    ServicePriority.HORMONAL_MEDICATION,      # Prioridade 3
    ServicePriority.POSTPARTUM_CARE,          # Prioridade 4
    ServicePriority.REGULAR                   # Prioridade 5
]

# Penalidade por violação de ordem: 5.000 pontos por posição violada
if min_next < max_current:
    violation_size = max_current - min_next
    priority_order_penalty += violation_size * 5000
```

**Características:**
- Permite até **1 parada** entre pontos da mesma prioridade para otimizar distância
- Penalidade moderada por violação de ordem (5.000 pontos/posição)
- Penalidade leve por gaps maiores que 1 (1.000 pontos por parada extra)

### 2. Casos de Violência Doméstica

Requerem **protocolos especiais** com tempo adequado:

```python
create_service_point(
    id=2,
    location=(300, 400),
    service_type='violence',
    time_window=(480, 600)  # 8h às 10h
)
# Duração automática: 45 minutos (mais tempo para atendimento cuidadoso)
# Requer protocolo especial
```

**Validações:**
- Tempo mínimo de serviço: 30 minutos (validado automaticamente)
- Penalidade por violação de protocolo: **20.000 pontos**
- Não é recomendado agrupar múltiplos casos consecutivamente

**Janelas de tempo:**
- **1 veículo**: 8h às 10h (480-600 min) + deadline prioritários até o fim do 1º dia (1440 min)
- **2 veículos**: 8h às 10h (480-600 min) + deadline prioritários até 12h (720 min)

### 3. Medicamentos Hormonais

Requerem **temperatura controlada** (2-8°C):

```python
create_service_point(
    id=3,
    location=(500, 100),
    service_type='medication',
    time_window=(480, 1080)  # Horário comercial: 8h às 18h
)
# Duração: 10 minutos (atendimento rápido)
# Requer controle de temperatura
```

**Validações:**
- Tempo máximo sem controle de temperatura: **120 minutos**
- Penalidade por violação: **50.000 pontos**

**Janelas de tempo:**
- **1 veículo**: Horário comercial 8h às 18h (480-1080 min) + deadline prioritários até o fim do 1º dia (1440 min)
- **2 veículos**: Horário comercial 8h às 18h (480-1080 min) + deadline prioritários até 12h (720 min)

### 4. Atendimento Pós-Parto

Têm **janelas de tempo específicas** respeitando horários de amamentação:

```python
create_service_point(
    id=4,
    location=(200, 300),
    service_type='postpartum',
    time_window=(540, 660)  # 9h às 11h
)
# Duração: 20 minutos
# Penalidade por atraso: 5.000x o tempo de atraso (em minutos)
```

**Características:**
- Chegar cedo: sem penalidade (pode esperar)
- Chegar atrasado: **5.000 pontos por minuto** de atraso

**Janelas de tempo:**
- **1 veículo**: 9h às 11h (540-660 min) ou padrão 8h às 12h (480-720 min) + deadline prioritários até o fim do 1º dia (1440 min)
- **2 veículos**: 9h às 11h (540-660 min) ou padrão 8h às 12h (480-720 min) + deadline prioritários até 12h (720 min)

### 5. Emergências Obstétricas

**Prioridade máxima** - devem ser atendidas primeiro:

```python
create_service_point(
    id=1,
    location=(100, 200),
    service_type='emergency'
)
# Duração: 30 minutos (atendimento mais longo)
# Requer protocolo especial
```

**Características:**
- Sempre no início da rota (após depósito)
- Penalidade por atraso: **100x** o tempo base

**Deadline de prioritários:**
- **1 veículo**: Até o fim do º dia (1440 min)
- **2 veículos**: Até 12h (720 min)

## Função de Fitness

A função de fitness balanceia distância e restrições:

```
fitness_total = (distância_base × 10)           # Peso principal
              + priority_order_penalty          # 5.000/posição violada
              + gap_penalty                     # 1.000/parada extra
              + time_window_penalty             # 5.000/min de atraso
              + temperature_penalty             # 50.000 (se violado)
              + protocol_penalty                # 20.000 (se violado)
              + overtime_penalty                # 100/min extra
              + priority_deadline_penalty       # 10.000/min após deadline
```

### Pesos das Penalidades

| Tipo de Violação | Penalidade | Observação |
|------------------|------------|------------|
| **Violação de temperatura** | 50.000 pontos | Medicamentos > 120 min sem controle |
| **Violação de protocolo** | 20.000 pontos | Tempo insuficiente para protocolo especial |
| **Violação de ordem de prioridade** | 5.000 pontos/posição | Por cada posição fora de ordem |
| **Gap entre prioridades** | 1.000 pontos/parada | Por cada parada além de 1 |
| **Atraso em janela de tempo** | 5.000 pontos/minuto | Multiplicado pelo tempo de atraso |
| **Deadline de prioritários** | 10.000 pontos/minuto | Após 1º dia (1v) ou 12:00 (2v) |
| **Hora extra** | 100 pontos/minuto | Após 8 horas de trabalho |
| **Distância** | 10 pontos/unidade | Peso principal (distância × 10) |

## Parâmetros Configuráveis

### Em `src/core/service_points.py`:

```python
# Tempo máximo sem controle de temperatura (minutos)
max_time_without_control = 120.0

# Velocidade média do veículo (km/h)
speed = 80.0

# Tempo de início da jornada (minutos desde meia-noite)
start_time = 480.0  # 8h da manhã
```

### Em `src/core/genetic_algorithm.py`:

```python
# Viés para ordem de prioridade na população inicial
priority_bias = 0.9  # 90% das rotas iniciais seguem prioridades

# Preservar blocos de prioridade no crossover (80% das vezes)
preserve_priority_blocks = True

# Respeitar prioridades na mutação (90% das vezes)
respect_priorities = True
```

## Executando os Testes

### Com Makefile:
```bash
make test
```

### Manual:
```bash
cd tests
python test_restrictions.py
```

## Saída Esperada

```
Iniciando Algoritmo Genético com Restrições...

Geração 0: Melhor fitness = 15234.56
  Ordem de prioridades na melhor rota:
    1. Ponto 1 - EMERGENCY_OBSTETRIC
    2. Ponto 8 - EMERGENCY_OBSTETRIC
    3. Ponto 2 - DOMESTIC_VIOLENCE
    4. Ponto 4 - POSTPARTUM_CARE
    5. Ponto 3 - HORMONAL_MEDICATION

...

============================================================
MELHOR ROTA ENCONTRADA:
============================================================

Fitness total: 8456.23
Distância total: 1234.56
Tempo total: 245.00 minutos (4.08 horas)

Ordem de atendimento:
1. Ponto 1 - EMERGENCY_OBSTETRIC
   Chegada: 08:00
   Duração serviço: 30.0 min
   
2. Ponto 8 - EMERGENCY_OBSTETRIC
   Chegada: 08:35
   Duração serviço: 30.0 min
   
3. Ponto 2 - DOMESTIC_VIOLENCE
   Chegada: 09:10
   Duração serviço: 45.0 min
   Janela: 08:00 - 10:00
   
...
```

## Integração com Interface Gráfica

O sistema já está integrado. Execute:

```bash
make run
# ou
python app/main.py
```

A interface mostra:
- Mapa com rotas coloridas por prioridade
- Gráfico de evolução do fitness
- Painel de informações detalhadas
- Ordem de atendimento em 2 colunas


## Referências

- Algoritmo genético: [`src/core/genetic_algorithm.py`](../src/core/genetic_algorithm.py)
- Interface gráfica: [`src/visualization/pygame_viewer.py`](../src/visualization/pygame_viewer.py)
- Estruturas de dados: [`src/core/service_points.py`](../src/core/service_points.py)
- Documentação principal: [`README.md`](../README.md)
- Guia rápido: [`GUIA_RAPIDO.md`](GUIA_RAPIDO.md)
- Documentação FIAP: [`README_FIAP.md`](README_FIAP.md)

---

**Autor**: Fernanda Valdevino - Projeto Fase 2  
**Última atualização**: 17 de fevereiro de 2026

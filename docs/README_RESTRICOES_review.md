# Sistema de Roteamento com Restrições e Prioridades

## Visão Geral

Este sistema estende o algoritmo genético para TSP (Traveling Salesman Problem) para incluir restrições específicas de atendimento em saúde da mulher, considerando:

- **Ordem de prioridade** para diferentes pontos de atendimento
- **Janelas de tempo** específicas para cada tipo de atendimento
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
- Gráfico de fitness
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
python main.py
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

As emergências obstétricas têm **prioridade máxima** e devem ser atendidas primeiro:

```python
# Penalidade por posição na rota
if point.priority == ServicePriority.EMERGENCY_OBSTETRIC:
    priority_penalty += position_factor * 10000  # Penalidade muito alta
```

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
```

### 3. Medicamentos Hormonais

Requerem **temperatura controlada**:

```python
# Validação automática: medicamentos não podem ficar mais de 120 min sem controle
is_valid, message = validate_temperature_control_route(route)
# Se inválido: penalidade de 50.000 pontos no fitness
```

### 4. Atendimento Pós-Parto

Têm **janelas de tempo específicas**:

```python
create_service_point(
    id=4,
    location=(200, 300),
    service_type='postpartum',
    time_window=(540, 660)  # 9h às 11h
)
# Penalidade por atraso: 50x o tempo de atraso
```

## Função de Fitness

A função de fitness considera múltiplos fatores:

```
fitness_total = distância_base 
              + penalidade_janela_tempo
              + penalidade_prioridade
              + penalidade_temperatura
              + penalidade_protocolo
              + penalidade_hora_extra
```

### Pesos das Penalidades

- **Violação de temperatura**: 50.000 pontos
- **Violação de protocolo**: 20.000 pontos
- **Emergência em posição tardia**: até 10.000 pontos
- **Violência doméstica tardia**: até 5.000 pontos
- **Atraso em janela de tempo**: 50x o tempo de atraso

## Parâmetros Configuráveis

### Em `src/core/service_points.py`:

```python
# Tempo máximo sem controle de temperatura (minutos)
max_time_without_control = 120.0

# Velocidade média do veículo (km/h)
speed = 40.0

# Tempo de início da jornada (minutos desde meia-noite)
start_time = 480.0  # 8h da manhã
```

### Em `src/core/genetic_algorithm.py`:

```python
# Viés para ordem de prioridade na população inicial
priority_bias = 0.7  # 70% das rotas iniciais seguem prioridades

# Preservar blocos de prioridade no crossover
preserve_priority_blocks = True

# Respeitar prioridades na mutação
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
python main.py
```

A interface mostra:
- Mapa com rotas coloridas por prioridade
- Gráfico de evolução do fitness
- Painel de informações detalhadas
- Ordem de atendimento em 2 colunas

## Extensões Futuras

1. **Múltiplos veículos**: Dividir rotas entre vários profissionais
2. **Prioridades dinâmicas**: Ajustar prioridades em tempo real
3. **Otimização multi-objetivo**: Balancear tempo, distância e satisfação
4. **Restrições de capacidade**: Limitar quantidade de medicamentos por veículo
5. **Zonas de risco**: Evitar áreas perigosas em casos de violência doméstica

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

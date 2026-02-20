# Guia Rápido: Sistema de Roteamento com Restrições

## 📋 Resumo

Sistema completo para roteamento de atendimentos em saúde da mulher com suporte a:

✅ **Prioridades**: Emergências obstétricas, violência doméstica, medicamentos, pós-parto, regular  
✅ **Janelas de tempo**: Horários específicos para cada tipo de atendimento  
✅ **Controle de temperatura**: Validação para medicamentos hormonais  
✅ **Protocolos especiais**: Tempo adequado para casos sensíveis  
✅ **Penalizações inteligentes**: Fitness considera todas as restrições  

## 🚀 Como Usar

### Opção 1: Usando Makefile (Recomendado)

```bash
cd genetic_algorithm_routes_optimization

# Ver todos os comandos disponíveis
make help

# Instalar tudo (cria env + instala dependências)
make install

# Executar o sistema
make run

# Fazer tudo de uma vez
make all

# Executar testes
make test

# Limpar ambiente
make clean
```

### Opção 2: Execução Manual

```bash
cd genetic_algorithm_routes_optimization

# Criar ambiente virtual
python3 -m venv ga_routes

# Ativar ambiente (macOS/Linux)
source ga_routes/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar sistema
python main.py

# Executar testes
cd tests
python test_restrictions.py
```

## 📁 Estrutura do Projeto

```
genetic_algorithm_routes_optimization/
├── main.py                      # Ponto de entrada principal
├── Makefile                     # Automação de tarefas
├── requirements.txt             # Dependências
├── README.md                    # Documentação principal
│
├── src/                         # Código fonte
│   ├── core/                    # Lógica principal
│   │   ├── service_points.py   # Pontos de atendimento
│   │   └── genetic_algorithm.py # Algoritmo genético
│   └── visualization/           # Interface gráfica
│       └── pygame_viewer.py    # Visualização Pygame
│
├── tests/                       # Testes
│   └── test_restrictions.py    # Testes de validação
│
└── docs/                        # Documentação
    ├── GUIA_RAPIDO.md          # Este arquivo
    ├── README_RESTRICOES.md    # Detalhes das restrições
    └── README_FIAP.md          # Documentação FIAP
```

## 💻 Uso Programático

### 1. Criar Pontos de Atendimento

```python
from src.core.service_points import create_service_point

# Emergência obstétrica (prioridade máxima)
emergency = create_service_point(1, (100, 200), 'emergency')

# Violência doméstica (protocolo especial, janela 8h-10h)
violence = create_service_point(2, (300, 400), 'violence', 
                                time_window=(480, 600))

# Medicamento hormonal (temperatura controlada)
medication = create_service_point(3, (500, 100), 'medication')

# Pós-parto (janela 9h-11h)
postpartum = create_service_point(4, (200, 300), 'postpartum',
                                  time_window=(540, 660))

# Atendimento regular
regular = create_service_point(5, (400, 500), 'regular')
```

### 2. Executar Algoritmo Genético

```python
from src.core.genetic_algorithm import (
    generate_priority_aware_population,
    calculate_constrained_fitness,
    sort_population_by_fitness,
    constrained_order_crossover,
    constrained_mutate
)

# Parâmetros
POPULATION_SIZE = 50
N_GENERATIONS = 100
MUTATION_PROBABILITY = 0.3

# Criar população inicial (com viés para prioridades)
population = generate_priority_aware_population(
    service_points, 
    POPULATION_SIZE,
    priority_bias=0.7  # 70% seguem ordem de prioridade
)

# Loop evolutivo
for generation in range(N_GENERATIONS):
    # Avaliar fitness
    fitness_values = [
        calculate_constrained_fitness(route) 
        for route in population
    ]
    
    # Ordenar (menor fitness = melhor)
    population, fitness_values = sort_population_by_fitness(
        population, fitness_values
    )
    
    # Nova geração
    new_population = [population[0]]  # Elitismo
    
    while len(new_population) < POPULATION_SIZE:
        # Seleção
        parent1, parent2 = random.sample(population[:10], 2)
        
        # Crossover (preserva blocos de prioridade)
        child = constrained_order_crossover(parent1, parent2)
        
        # Mutação (respeita restrições)
        child = constrained_mutate(child, MUTATION_PROBABILITY)
        
        new_population.append(child)
    
    population = new_population

# Melhor solução
best_route = population[0]
```

## 🎯 Ordem de Prioridade

1. **EMERGENCY_OBSTETRIC** (peso 1) - 🔴 Vermelho
   - Prioridade máxima
   - Penalidade: 10.000 pontos se atendida tarde
   - Duração: 30 minutos

2. **DOMESTIC_VIOLENCE** (peso 2) - 🟠 Laranja
   - Protocolos especiais
   - Penalidade: 5.000 pontos se atendida tarde
   - Duração: 45 minutos

3. **HORMONAL_MEDICATION** (peso 3) - 🔵 Azul
   - Temperatura controlada (máx 120 min)
   - Penalidade: 2.000 pontos se atendida tarde
   - Duração: 10 minutos

4. **POSTPARTUM_CARE** (peso 4) - 🟣 Roxo
   - Janela de tempo específica
   - Penalidade: 3.000 pontos se atendida tarde
   - Duração: 20 minutos

5. **REGULAR** (peso 5) - ⚫ Cinza
   - Atendimento padrão
   - Duração: 15 minutos

## ⚙️ Parâmetros Configuráveis

### Em `src/core/service_points.py`:

```python
# Tempo máximo sem controle de temperatura
max_time_without_control = 120.0  # minutos

# Velocidade média do veículo
speed = 40.0  # km/h

# Fator de escala (1 unidade = quantos km)
scale_factor = 0.1  # 1 unidade = 100 metros
```

### Em `src/core/genetic_algorithm.py`:

```python
# Viés para ordem de prioridade na população inicial
priority_bias = 0.7  # 0.0 a 1.0

# Preservar blocos de prioridade no crossover
preserve_priority_blocks = True

# Respeitar prioridades na mutação
respect_priorities = True

# Tempo máximo de jornada
max_work_time = 480.0  # 8 horas
```

## 🎮 Controles da Visualização

Ao executar `make run` ou `python main.py`:

- **Q** ou **ESC**: Sair
- **R**: Reiniciar com novos pontos aleatórios

## 📈 Componentes do Fitness

```
fitness_total = distância_base
              + penalidade_janela_tempo
              + penalidade_prioridade
              + penalidade_temperatura (50.000 se violada)
              + penalidade_protocolo (20.000 se violada)
              + penalidade_hora_extra (100 por minuto extra)
```

## ✅ Validações Automáticas

1. **Temperatura**: Medicamentos não podem ficar >120 min sem controle
2. **Protocolos**: Casos especiais têm tempo mínimo de 30 minutos
3. **Janelas de tempo**: Penalidade de 50x o atraso
4. **Prioridades**: Emergências devem ser atendidas primeiro

## 🔍 Exemplo de Saída

```
Geração 0: Fitness = 15234.56
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
```

## 📚 Documentação Completa

Para mais detalhes, consulte:
- [`README.md`](../README.md) - Documentação principal
- [`README_RESTRICOES.md`](README_RESTRICOES.md) - Detalhes das restrições
- [`README_FIAP.md`](README_FIAP.md) - Documentação FIAP

## 🐛 Solução de Problemas

### Erro: "ModuleNotFoundError"
```bash
# Certifique-se de ter instalado as dependências
make install
```

### Pygame não abre
```bash
# Verificar instalação do Pygame
pip list | grep pygame
```

### Testes falhando
```bash
# Executar testes para diagnóstico
make test
```

## 💡 Dicas de Uso

1. **População inicial**: Use `priority_bias=0.7` ou maior para convergência mais rápida
2. **Mutação**: Valores entre 0.2-0.4 funcionam bem
3. **Tamanho da população**: 50-100 indivíduos é suficiente
4. **Gerações**: 100-200 gerações para problemas pequenos (<15 pontos)

## 🎓 Conceitos Implementados

- ✅ Algoritmo Genético com elitismo
- ✅ Order Crossover (OX) adaptado
- ✅ Mutação por troca respeitando restrições
- ✅ Seleção por torneio
- ✅ Função de fitness multi-objetivo
- ✅ Validação de restrições hard e soft
- ✅ Penalizações adaptativas por prioridade

---

**Desenvolvido para**: Roteamento de atendimentos em saúde da mulher  
**Tecnologias**: Python, Pygame, Algoritmos Genéticos  
**Autor**: Fernanda Valdevino - Projeto Fase 2  
**Status**: ✅ Todos os testes passando (6/6)

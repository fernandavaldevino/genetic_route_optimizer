# Sistema de Roteamento Inteligente para Saúde da Mulher

## 📋 Descrição do Projeto

Sistema de otimização de rotas para entregas de medicamentos e atendimentos na área de saúde da mulher, desenvolvido utilizando **Algoritmo Genético** com múltiplas restrições e prioridades. O sistema garante que medicamentos críticos sejam entregues dentro de prazos específicos, respeitando janelas de tempo, controle de temperatura e protocolos especiais.

**Autor**: Fernanda Valdevino - Projeto Fase 2

---

## 🎯 Objetivos

1. **Otimizar rotas de entrega** minimizando distância total percorrida
2. **Respeitar ordem de prioridades** para diferentes tipos de atendimento
3. **Garantir entregas críticas** no Dia 1 (medicamentos prioritários)
4. **Cumprir janelas de tempo** específicas para cada tipo de atendimento
5. **Manter controle de temperatura** para medicamentos hormonais
6. **Seguir protocolos especiais** para casos de violência doméstica
7. **Respeitar horário comercial** (8h às 18h) com pausas noturnas

---

## 🏥 Tipos de Atendimento e Prioridades

### Ordem de Prioridades (do maior para o menor)

| Prioridade | Tipo | Código | Cor | Restrições Especiais |
|------------|------|--------|-----|---------------------|
| 1 | **Emergências Obstétricas** | EME | 🔴 Vermelho | Prioridade máxima, atendimento de 30 min |
| 2 | **Violência Doméstica** | VIO | 🟠 Laranja | Janela: 8h-10h, protocolo especial, 45 min |
| 3 | **Medicamentos Hormonais** | MED | 🔵 Azul | Janela: 8h-18h, temperatura controlada, 10 min |
| 4 | **Pós-Parto** | POS | 🟣 Roxo | Janela: 9h-11h, 20 min |
| 5 | **Regular** | REG | ⚫ Cinza | Sem restrições especiais, 15 min |

---

## 🚨 Restrições Implementadas

### 1. **Ordem de Prioridades Hierárquica**
- Medicamentos devem ser entregues seguindo a ordem: **EME → VIO → MED → POS → REG**
- Permite até **1 parada** entre pontos da mesma prioridade para otimizar distância
- Penalidade proporcional por violação de ordem (5.000 pontos por violação)

### 2. **Medicamentos Prioritários no Dia 1**
- **EME, VIO, MED e POS** devem ser entregues obrigatoriamente no **Dia 1**
- Penalidade massiva: **1.000.000 pontos** por medicamento prioritário fora do Dia 1
- Atendimentos **REG** podem ser entregues em dias subsequentes

### 3. **Horário Comercial (8h às 18h)**
- Entregas apenas entre **8h e 18h**
- Se passar das 18h, rota pausa e continua às **8h do dia seguinte**
- Sistema calcula automaticamente pausas noturnas

### 4. **Janelas de Tempo Específicas**

| Tipo | Janela de Tempo | Penalidade |
|------|----------------|------------|
| VIO | 8h às 10h | 10x por minuto de atraso, 50x por minuto de antecipação |
| POS | 9h às 11h | 10x por minuto de atraso, 50x por minuto de antecipação |
| MED | 8h às 18h | 10x por minuto de atraso, 50x por minuto de antecipação |

### 5. **Controle de Temperatura**
- Medicamentos hormonais (MED) requerem **temperatura controlada**
- Tempo máximo sem controle: **120 minutos**
- Penalidade: **50.000 pontos** por violação

### 6. **Protocolos Especiais**
- Casos de violência doméstica (VIO) e emergências (EME) requerem **protocolos especiais**
- Tempo mínimo de atendimento: **30 minutos**
- Penalidade: **20.000 pontos** por violação

### 7. **Tempo Máximo de Trabalho**
- Jornada máxima: **8 horas por dia** (480 minutos)
- Penalidade: **100 pontos** por minuto extra

---

## 🧬 Algoritmo Genético

### Parâmetros

```python
POPULATION_SIZE = 100        # Tamanho da população
N_POINTS = 20               # Número de pontos de atendimento
MUTATION_PROBABILITY = 0.3  # Probabilidade de mutação (30%)
FPS = 10                    # Velocidade de visualização
```

### Operadores Genéticos

#### 1. **População Inicial**
- **90%** das rotas geradas com viés de prioridade
- **10%** completamente aleatórias (diversidade)
- Embaralhamento dentro de grupos da mesma prioridade

#### 2. **Função de Fitness**
```python
fitness = (distância × 10) + 
          (5000 × violações_ordem) + 
          (1000 × gaps_extras) +
          (1000000 × prioridades_fora_D1) +
          penalidades_janelas_tempo +
          penalidades_temperatura +
          penalidades_protocolos +
          penalidades_overtime
```

#### 3. **Seleção**
- **Torneio** com 5 indivíduos
- **Elitismo**: melhor solução sempre preservada

#### 4. **Crossover (Order Crossover - OX)**
- **80%** preserva blocos de prioridade
- **20%** crossover padrão (diversidade)

#### 5. **Mutação**
- **90%** troca apenas dentro do mesmo grupo de prioridade
- **10%** mutação livre (swap ou inversão)

---

## 📊 Interface Visual

### Painel de Informações (Esquerda)

1. **Geração e Fitness** atual
2. **Ordem de Prioridades para Atendimento**
   - Mostra range de IDs: `EME - (1, 2)`
3. **Ordem de Atendimento** (2 colunas)
   - Formato: `1. P2-EME (08:00, D1)`
   - Indicadores de dia coloridos:
     - **D1**: Preto (normal)
     - **D2**: Verde escuro (REG) ou 🔴 Vermelho (prioridades - ALERTA!)
     - **D3+**: Azul escuro

### Mapa (Centro/Direita)

- **Pontos coloridos** por prioridade
- **Linhas coloridas** conectando a rota
- **Círculos de destaque** nos pontos iniciais de cada dia:
  - **Dia 1**: Círculo preto grosso
  - **Dia 2**: Círculo verde escuro grosso
  - **Dia 3+**: Círculo azul escuro grosso

### Gráfico de Evolução (Inferior Esquerdo)

- **Evolução do Fitness** ao longo das gerações
- **Best Solution**: Vetor com IDs coloridos por prioridade
- **Fitness**: Valor numérico
- **Entregas em**: Número de dias necessários (colorido)
  - 🟢 **1 dia**: Verde (ótimo)
  - 🟠 **2 dias**: Laranja escuro (aceitável)
  - 🔴 **3+ dias**: Vermelho (atenção)

---

## 🚀 Como Executar

### Pré-requisitos

```bash
# Python 3.10+
# pip
# make (opcional, mas recomendado)
```

### Instalação

#### Opção 1: Usando Makefile (Recomendado)

```bash
cd genetic_route_optimizer

# Ver comandos disponíveis
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

#### Opção 2: Manual

```bash
cd genetic_route_optimizer

# Criar ambiente virtual
python3 -m venv ga_routes

# Ativar ambiente (macOS/Linux)
source ga_routes/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar sistema
python app/main.py
```

### Controles

- **Q** ou **ESC**: Sair
- **R**: Reiniciar com novos pontos aleatórios

---

## 📁 Estrutura de Arquivos

```
genetic_route_optimizer/
├── app/                         # Aplicações principais
│   ├── main.py                  # Pygame 1 veículo (standalone)
│   └── main_2v.py               # Pygame 2 veículos (standalone)
├── Makefile                     # Automação de tarefas
├── requirements.txt             # Dependências
├── README.md                    # Documentação principal
├── .gitignore                   # Arquivos ignorados pelo Git
│
├── src/                         # Código fonte
│   ├── __init__.py
│   ├── core/                    # Lógica principal
│   │   ├── __init__.py
│   │   ├── service_points.py   # Pontos de atendimento
│   │   └── genetic_algorithm.py # Algoritmo genético
│   ├── visualization/           # Interface gráfica
│   │   ├── __init__.py
│   │   └── pygame_viewer.py    # Visualização Pygame
│   └── utils/                   # Utilitários
│       └── __init__.py
│
├── tests/                       # Testes
│   ├── __init__.py
│   └── test_restrictions.py    # Testes de validação
│
└── docs/                        # Documentação
    ├── GUIA_RAPIDO.md          # Guia rápido de uso
    ├── README_RESTRICOES.md    # Detalhes das restrições
    └── README_FIAP.md          # Este documento
```

---

## 🔧 Arquitetura do Sistema

### 1. **src/core/service_points.py**
- `ServicePriority`: Enum com níveis de prioridade
- `TimeWindow`: Classe para janelas de tempo
- `ServicePoint`: Dataclass para pontos de atendimento
- Funções de validação (temperatura, protocolos)

### 2. **src/core/genetic_algorithm.py**
- `calculate_route_time_and_distance()`: Calcula tempo e distância com pausas noturnas
- `calculate_constrained_fitness()`: Função de fitness multi-objetivo
- `generate_priority_aware_population()`: Gera população inicial
- `constrained_order_crossover()`: Crossover que preserva prioridades
- `constrained_mutate()`: Mutação que respeita grupos de prioridade

### 3. **src/visualization/pygame_viewer.py**
- Interface gráfica com Pygame
- Visualização em tempo real
- Painel de informações
- Gráfico de evolução
- Destaque visual de alertas

### 4. **app/main.py**
- Ponto de entrada do sistema
- Configuração inicial
- Execução da visualização

---

## 📈 Resultados Esperados

### Rotas Válidas

O sistema garante que:
- ✅ Todos os medicamentos prioritários (EME, VIO, MED, POS) sejam entregues no **Dia 1**
- ✅ Ordem de prioridades seja respeitada
- ✅ Janelas de tempo sejam cumpridas
- ✅ Controle de temperatura seja mantido
- ✅ Protocolos especiais sejam seguidos
- ✅ Distância total seja minimizada (dentro das restrições)

### Exemplo de Rota Ótima

```
Dia 1 (D1):
08:00 - P1-EME (Emergência 1)
09:15 - P2-EME (Emergência 2)
10:30 - P3-VIO (Violência 1)
11:45 - P4-VIO (Violência 2)
13:00 - P5-MED (Medicamento 1)
14:15 - P6-MED (Medicamento 2)
15:30 - P7-POS (Pós-parto 1)
16:45 - P8-POS (Pós-parto 2)

Dia 2 (D2):
08:00 - P9-REG (Regular 1)
09:15 - P10-REG (Regular 2)
...
```

---

## 🎓 Conceitos Aplicados

### Algoritmos Genéticos
- População, fitness, seleção, crossover, mutação, elitismo
- Operadores especializados para TSP com restrições

### Otimização Multi-Objetivo
- Balanceamento entre distância e restrições
- Penalidades proporcionais vs. absolutas

### Problema do Caixeiro Viajante (TSP)
- Variante com janelas de tempo (TSPTW)
- Múltiplas restrições hard e soft

### Visualização de Dados
- Interface gráfica interativa
- Gráficos de evolução em tempo real
- Sistema de alertas visuais

---

## 🔍 Validações e Testes

### Testes Implementados

Execute os testes com:
```bash
make test
# ou
cd tests
python test_restrictions.py
```

**Testes incluem:**
- ✅ Validação de janelas de tempo
- ✅ Validação de controle de temperatura
- ✅ Validação de protocolos especiais
- ✅ Validação de ordem de prioridades
- ✅ Validação de pausas noturnas
- ✅ Validação de operadores genéticos

---

## 📊 Métricas de Desempenho

### Fitness
- **Menor é melhor**
- Valores típicos: 1.000 - 10.000 (rotas válidas)
- Valores > 100.000 indicam violações graves

### Convergência
- Geralmente converge em **50-100 gerações**
- Melhoria significativa nas primeiras 20 gerações

### Tempo de Execução
- ~10 gerações por segundo (FPS = 10)
- Ajustável via parâmetro `FPS`

---

## 🛠️ Personalização

### Ajustar Número de Pontos

```python
# Em src/visualization/pygame_viewer.py
N_POINTS = 20  # Alterar para o número desejado
```

### Ajustar Penalidades

```python
# Em src/core/genetic_algorithm.py
priority_order_penalty += violation_size * 5000  # Ajustar multiplicador
priority_day_penalty += 1000000  # Ajustar penalidade
```

### Ajustar Horário Comercial

```python
# Em src/core/genetic_algorithm.py
work_start = 480.0   # 8h (em minutos)
work_end = 1080.0    # 18h (em minutos)
```

---

## 🐛 Troubleshooting

### Problema: Medicamentos prioritários no Dia 2
**Solução**: Aumentar penalidade `priority_day_penalty` ou reduzir número de pontos

### Problema: Fitness muito alto
**Solução**: Verificar se há violações de restrições críticas (janelas de tempo, temperatura)

### Problema: Convergência lenta
**Solução**: Aumentar `POPULATION_SIZE` ou ajustar `MUTATION_PROBABILITY`

### Problema: Erro de import
**Solução**: Verificar se o ambiente virtual está ativado e dependências instaladas
```bash
make install
```

---

## 📚 Referências

- Goldberg, D. E. (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning*
- Holland, J. H. (1992). *Adaptation in Natural and Artificial Systems*
- Laporte, G. (1992). *The Vehicle Routing Problem: An overview of exact and approximate algorithms*

---

## 👥 Autor

**Fernanda Valdevino**
- Projeto: Fase 2
- Instituição: FIAP
- Sistema de Roteamento Inteligente para Saúde da Mulher
- Algoritmo Genético com Múltiplas Restrições

---

## 📝 Licença

Este projeto é desenvolvido para fins educacionais.

---

## 🔄 Versão

**Versão 3.0 - MVP** - Sistema completo com:
- ✅ Estrutura profissional de MVP
- ✅ Makefile para automação
- ✅ Múltiplas prioridades
- ✅ Janelas de tempo
- ✅ Pausas noturnas
- ✅ Alertas visuais
- ✅ Validações completas
- ✅ Interface otimizada
- ✅ Documentação completa
- ✅ Testes automatizados

---

## 📞 Suporte

Para dúvidas ou sugestões sobre o projeto, consulte a documentação adicional:
- [`README.md`](../README.md) - Documentação principal
- [`README_RESTRICOES.md`](README_RESTRICOES.md) - Detalhes técnicos das restrições
- [`GUIA_RAPIDO.md`](GUIA_RAPIDO.md) - Guia rápido de uso

---

**Última atualização**: 17 de fevereiro de 2026

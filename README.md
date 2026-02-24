g# Sistema de Otimização de Rotas com Restrições

**Algoritmo Genético para Roteamento de Atendimentos em Saúde da Mulher**

Autor: Fernanda Valdevino - Projeto Fase 2

---

## 📋 Descrição

Sistema de otimização de rotas utilizando Algoritmo Genético para resolver o problema de roteamento de atendimentos em saúde da mulher, considerando múltiplas restrições e prioridades.

### Características Principais

- **Ordem de Prioridade Hierárquica**:
  1. 🔴 Emergências Obstétricas (prioridade máxima)
  2. 🟠 Casos de Violência Doméstica (protocolos especiais)
  3. 🔵 Medicamentos Hormonais (temperatura controlada)
  4. 🟣 Atendimento Pós-Parto (janelas de tempo específicas)
  5. ⚪ Atendimentos Regulares

- **Restrições Implementadas**:
  - Janelas de tempo específicas para atendimentos sensíveis
  - Controle de temperatura para medicamentos hormonais
  - Horário comercial (8h-18h) com pausas noturnas
  - Protocolos especiais para casos de violência doméstica
  - Penalização por atrasos em atendimentos prioritários

- **Visualização em Tempo Real**:
  - **Interface Pygame**: Visualização animada completa
  - **Interface Streamlit**: Dashboard web interativo
  - **Opção de 1 ou 2 veículos**: Escolha na interface
  - Gráfico de evolução do fitness
  - Mapa de rotas colorido por prioridade
  - Informações detalhadas de cada atendimento
  - Screenshot final da otimização

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.10+
- pip
- make (opcional, mas recomendado)

### Opção 1: Usando Makefile (Recomendado)

```bash
# Ver todos os comandos disponíveis
make help

# Instalar tudo automaticamente (cria env + instala dependências)
make install

# Executar o sistema
make run

# Fazer tudo de uma vez (install + run)
make all

# Executar testes
make test

# Limpar ambiente e cache
make clean

# Ver informações do ambiente
make info
```

### Opção 2: Instalação Manual

1. Criar ambiente virtual:
```bash
python3 -m venv .ga_routes
```

2. Ativar ambiente virtual:
```bash
# No macOS/Linux
source .ga_routes/bin/activate

# No Windows
.ga_routes\Scripts\activate
```

3. Instalar dependências:
```bash
pip install -r requirements.txt
```

---

## 💻 Uso

### Opção 1: Interface Streamlit (Recomendado)

**Com Makefile:**
```bash
make all
# ou
make streamlit
```

**Manualmente:**
```bash
streamlit run app_streamlit.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

**Funcionalidades:**
- 🚗 **Seletor de Veículos**: Escolha entre 1 ou 2 veículos
  - **1 veículo**: Otimização tradicional (múltiplos dias)
  - **2 veículos**: Otimização multi-veículo com depósito (1 dia)
- ▶️ **Start**: Inicia otimização (Pygame + Streamlit)
- 🔄 **Reiniciar**: Nova otimização automática
- ❌ **Encerrar**: Limpa tudo e fecha

### Opção 2: Interface Pygame (Standalone)

**Com Makefile:**
```bash
make run
```

**Manualmente:**
```bash
python main.py
```

**Controles:**
- **Q** ou **ESC**: Sair do sistema
- **R**: Reiniciar com novos pontos aleatórios

### Executar os Testes

**Com Makefile:**
```bash
make test
```

**Manualmente:**
```bash
cd tests
python test_restrictions.py
```

---

## 📁 Estrutura do Projeto

```
genetic_route_optimizer/
├── README.md                    # Este arquivo
├── README_STREAMLIT.md          # Documentação Streamlit
├── requirements.txt             # Dependências do projeto
├── Makefile                     # Comandos automatizados
├── main.py                      # Pygame 1 veículo (standalone)
├── main_2v.py                   # Pygame 2 veículos (standalone)
├── app_streamlit.py             # Interface Streamlit (recomendado)
│
├── src/                         # Código fonte
│   ├── __init__.py
│   ├── core/                    # Lógica principal
│   │   ├── __init__.py
│   │   ├── service_points.py   # Pontos de atendimento e restrições
│   │   ├── genetic_algorithm.py # Algoritmo genético (1 veículo)
│   │   └── multi_vehicle.py    # Algoritmo genético (2 veículos)
│   ├── visualization/           # Interface gráfica
│   │   ├── __init__.py
│   │   ├── pygame_viewer.py    # Visualização 1 veículo
│   │   └── pygame_viewer_2v.py # Visualização 2 veículos
│   └── utils/                   # Utilitários
│       └── __init__.py
│
├── tests/                       # Testes
│   ├── __init__.py
│   └── test_restrictions.py    # Testes de validação
│
└── docs/                        # Documentação
    ├── GUIA_RAPIDO_review.md   # Guia rápido de uso
    ├── README_RESTRICOES_review.md # Detalhes das restrições
    └── README2_FIAP_review.md  # Documentação FIAP
```

---

## 🧬 Algoritmo Genético

### Parâmetros

- **População**: 100 indivíduos
- **Taxa de Mutação**: 30%
- **Seleção**: Torneio (tamanho 5)
- **Elitismo**: Melhor indivíduo preservado
- **Crossover**: Order Crossover (OX) com viés de prioridade
- **Mutação**: Swap com respeito às restrições

### Função de Fitness

A função de fitness considera:
- Distância total percorrida
- Penalização por ordem incorreta de prioridades
- Penalização por violação de janelas de tempo
- Penalização por violação de controle de temperatura
- Penalização por atrasos em atendimentos prioritários

---

## 📊 Restrições Detalhadas

### 1. Emergências Obstétricas (EME)
- **Prioridade**: Máxima (peso 1)
- **Restrição**: Devem ser atendidas primeiro
- **Penalização**: Alta por atrasos

### 2. Violência Doméstica (VIO)
- **Prioridade**: Alta (peso 2)
- **Janela de Tempo**: 8h às 10h (horário discreto)
- **Protocolo Especial**: Atendimento sensível

### 3. Medicamentos Hormonais (MED)
- **Prioridade**: Média-Alta (peso 3)
- **Restrição**: Controle de temperatura
- **Tempo Máximo sem Controle**: 120 minutos

### 4. Pós-Parto (POS)
- **Prioridade**: Média (peso 4)
- **Janela de Tempo**: 9h às 11h
- **Restrição**: Atendimento em horário específico

### 5. Regular (REG)
- **Prioridade**: Normal (peso 5)
- **Restrição**: Horário comercial (8h-18h)

---

## 📈 Resultados

O sistema otimiza rotas considerando:
- Minimização da distância total
- Respeito à hierarquia de prioridades
- Cumprimento de janelas de tempo
- Controle de temperatura para medicamentos
- Estimativa de dias necessários para completar todos os atendimentos

---

## 🔧 Desenvolvimento

### Adicionar Novos Tipos de Atendimento

Edite `src/core/service_points.py`:
```python
class ServicePriority(Enum):
    NOVO_TIPO = 6  # Adicionar novo tipo
```

### Modificar Parâmetros do AG

Edite `src/visualization/pygame_viewer.py`:
```python
POPULATION_SIZE = 100
MUTATION_PROBABILITY = 0.3
```

---

## 📝 Licença

Projeto acadêmico - FIAP Fase 2

---

## 👤 Autor

**Fernanda Valdevino**
- Projeto: Fase 2
- Instituição: FIAP

---

## 🌐 Interface Streamlit

A interface Streamlit oferece uma experiência web completa:

### Características:
- **Seleção de Veículos**: Escolha entre 1 ou 2 veículos
  - **1 veículo**: Otimização tradicional (pode levar múltiplos dias)
  - **2 veículos**: Otimização multi-veículo com depósito (todos os pontos em 1 dia)
- **Visualização Dupla**: Pygame (animado) + Streamlit (resultados)
- **Progresso em Tempo Real**: Barra e status durante otimização
- **Screenshot Final**: Captura da tela do Pygame exibida no Streamlit
- **Gráficos Interativos**: Evolução do fitness, estatísticas
- **Métricas Detalhadas**: Fitness, dias, horários, melhorias
- **Controles Intuitivos**: Start, Reiniciar (auto-executa), Encerrar

### Documentação Completa:
Veja [`README_STREAMLIT.md`](README_STREAMLIT.md) para detalhes completos.

---

## 📚 Documentação Adicional

- [Interface Streamlit](README_STREAMLIT.md) - **Recomendado**
- [Guia Rápido](docs/GUIA_RAPIDO_review.md)
- [Detalhes das Restrições](docs/README_RESTRICOES_review.md)
- [Documentação FIAP](docs/README2_FIAP_review.md)

---

## 🐛 Problemas Conhecidos

Nenhum problema conhecido no momento.

---

## 🔮 Melhorias Futuras

- [x] Interface web com Streamlit ✅
- [ ] Exportação de rotas para CSV/JSON
- [ ] Análise estatística de múltiplas execuções
- [ ] Integração com APIs de mapas reais
- [ ] Otimização multi-objetivo (Pareto)
- [ ] Histórico de execuções no Streamlit

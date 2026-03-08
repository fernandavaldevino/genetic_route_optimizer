# 🚗 Sistema de Otimização de Rotas com Algoritmo Genético

**Sistema inteligente de otimização de rotas para atendimentos em saúde da mulher utilizando Algoritmo Genético com múltiplas restrições**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.5.0+-green.svg)](https://www.pygame.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0+-red.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-140%20passed-success.svg)](tests/)
[![License](https://img.shields.io/badge/License-Educational-yellow.svg)](LICENSE)

**[Documentação Técnica](docs/README_RESTRICOES.md)** | **[Interface Streamlit](docs/README_STREAMLIT.md)** | **[Integração LLM](docs/README_LLM.md)** | **[Testes](docs/README_TESTS.md)**

---

## 📋 Índice

### Sobre o Projeto
- [Sobre o Projeto](#-sobre-o-projeto)
- [Características](#-características)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Estrutura do Projeto](#-estrutura-do-projeto)

### Sobre o Sistema
- [Arquitetura do Sistema](#-arquitetura-do-sistema)
- [Algoritmo Genético](#-algoritmo-genético)
- [Restrições e Prioridades](#-restrições-e-prioridades)
- [Interfaces Disponíveis](#-interfaces-disponíveis)
- [Testes](#-testes)
- [Métricas e Resultados](#-métricas-e-resultados)

### Informações Adicionais
- [Documentação Adicional](#-documentação-adicional)
- [Troubleshooting](#-troubleshooting)
- [Melhorias Futuras](#-melhorias-futuras)
- [Autores](#-autores)
- [Licença](#-licença)
- [Agradecimentos](#-agradecimentos)

---

## 🎯 Sobre o Projeto

Este projeto implementa um **sistema completo de otimização de rotas** para atendimentos em saúde da mulher, utilizando **Algoritmo Genético** com múltiplas restrições e prioridades hierárquicas. O sistema foi desenvolvido como parte do projeto acadêmico da **Fase 2 da Pós-Tech FIAP (IA para Devs)**, entregue em Março/2026.

### Objetivos

1. **Otimizar rotas de atendimento** minimizando distância total percorrida
2. **Respeitar hierarquia de prioridades** para diferentes tipos de atendimento
3. **Garantir cumprimento de janelas de tempo** específicas para cada tipo de serviço
4. **Manter controle de temperatura** para medicamentos hormonais
5. **Seguir protocolos especiais** para casos sensíveis (violência doméstica)
6. **Suportar múltiplos veículos** com otimização de depósito central
7. **Fornecer visualização em tempo real** da evolução do algoritmo

### Contexto

O sistema resolve o problema de **Roteamento de Veículos com Janelas de Tempo (VRPTW)** aplicado ao contexto de saúde da mulher, onde diferentes tipos de atendimento possuem prioridades e restrições específicas que devem ser respeitadas durante a otimização.

---

## ✨ Características

- 🧬 **Algoritmo Genético Avançado**: Operadores especializados com preservação de prioridades
- 🎯 **Sistema de Prioridades Hierárquicas**: 5 níveis de prioridade (Emergência → Regular)
- ⏰ **Janelas de Tempo Dinâmicas**: Validação e penalização por violações
- 🌡️ **Controle de Temperatura**: Monitoramento para medicamentos hormonais
- 🚗 **Suporte Multi-Veículo**: Otimização com 1 ou 2 veículos e depósito central
- 🎨 **Visualização em Tempo Real**: Interface Pygame com animação da evolução
- 🌐 **Dashboard Web Interativo**: Interface Streamlit responsiva e intuitiva
- 📊 **Métricas Detalhadas**: Fitness, distância, tempo, dias necessários
- 🧪 **Cobertura de Testes**: 95 testes automatizados com pytest
- 📈 **Gráficos de Evolução**: Acompanhamento visual do progresso do algoritmo
- 🔄 **Pausas Noturnas**: Respeito ao horário comercial (8h-18h)
- 📸 **Captura de Screenshots**: Registro visual dos resultados finais
- 🤖 **Assistente Inteligente com IA**: Geração automática de manuais, roteiros e Q&A usando LLMs
- 🌐 **Suporte Multi-Provedor LLM**: OpenAI (nuvem) e Ollama (local)
- 📄 **Exportação em PDF**: Manuais, roteiros e checklists em formato profissional
- 📦 **Documentos Multi-Veículo**: Geração automática de PDFs em ZIP para múltiplos veículos

---

## 🛠 Tecnologias Utilizadas

### Core
- **Python 3.12+** - Linguagem principal
- **NumPy 1.24+** - Computação científica e arrays
- **Pandas 2.0+** - Manipulação e análise de dados

### Visualização
- **Pygame 2.5+** - Interface gráfica animada (desktop)
- **Matplotlib 3.7+** - Gráficos de evolução (Streamlit)
- **Pillow 10.0+** - Captura de screenshots (Streamlit)

### Web & Interface
- **Streamlit 1.28+** - Dashboard web interativo

### LLM Integration
- **OpenAI 1.12+** - Integração com modelos GPT (nuvem)
- **Ollama 0.1+** - Suporte para modelos locais (Llama2, Mistral, CodeLlama)
- **Python-dotenv 1.0+** - Gerenciamento de variáveis de ambiente
- **FPDF2 2.7+** - Geração de documentos PDF profissionais

### Testes
- **Pytest 7.4+** - Framework de testes
- **Pytest-cov 4.1+** - Cobertura de código
- **Pytest-xdist 3.3+** - Execução paralela de testes

---

## 🏗 Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTRADA DE DADOS                         │
│  - Pontos de Atendimento (coordenadas, tipo, prioridade)    │
│  - Janelas de Tempo                                         │
│  - Restrições Especiais                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│              ALGORITMO GENÉTICO                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. População Inicial (com viés de prioridade)      │   │
│  │  2. Avaliação de Fitness (multi-objetivo)           │   │
│  │  3. Seleção por Torneio                             │   │
│  │  4. Crossover (Order Crossover - OX)                │   │
│  │  5. Mutação (respeitando restrições)                │   │
│  │  6. Elitismo (preserva melhor solução)              │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  VALIDAÇÃO DE RESTRIÇÕES                    │
│  - Ordem de Prioridades                                     │
│  - Janelas de Tempo                                         │
│  - Controle de Temperatura                                  │
│  - Protocolos Especiais                                     │
│  - Horário Comercial                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├──────────────────┬──────────────────────┐
                     ▼                  ▼                      ▼
         ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
         │  Pygame Viewer   │  │  Streamlit   │  │  Resultados      │
         │  (Visualização   │  │  Dashboard   │  │  - Rota ótima    │
         │   Animada)       │  │  (Web UI)    │  │  - Métricas      │
         └──────────────────┘  └──────────────┘  │  - Screenshots   │
                                                 └──────────────────┘
```

---

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

- **Sistema Operacional**: macOS, Linux ou Windows
- **Python**: Versão 3.12 ou superior
- **Pip**: Gerenciador de pacotes Python
- **Git**: Para controle de versão
- **Make** (Opcional): Para utilizar os comandos do Makefile

### Verificando as versões instaladas

```bash
python3 --version
pip3 --version
git --version
make --version  # Opcional
```

---

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone <repo-url>
cd genetic_route_optimizer
```

### 2. Crie e Ative um Ambiente Virtual

Se quiser uma experiência automatizada, vá para a seção [Como Usar](#-como-usar).

#### macOS / Linux
```bash
python3 -m venv .ga_routes
source .ga_routes/bin/activate
```

#### Windows (PowerShell)
```powershell
python3 -m venv .ga_routes
.\.ga_routes\Scripts\Activate.ps1
```

#### Windows (CMD)
```cmd
python3 -m venv .ga_routes
.\.ga_routes\Scripts\activate.bat
```

### 3. Instale as Dependências

#### Usando Makefile (Recomendado para macOS/Linux)
```bash
make install
```

#### Manualmente
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente (Opcional - para LLM)

Se você pretende usar funcionalidades de LLM (Large Language Models):

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env e adicione sua API Key da OpenAI
# OPENAI_API_KEY=sk-proj-sua-chave-aqui
```

**Como obter sua API Key da OpenAI:**
1. Acesse: https://platform.openai.com/api-keys
2. Faça login na sua conta OpenAI
3. Clique em **"Create new secret key"**
4. Copie a chave que começa com `sk-proj-...` ou `sk-...`
5. Cole no arquivo `.env` (sem aspas ou texto adicional)

**Formato correto no `.env`:**
```env
OPENAI_API_KEY=sk-proj-abc123...
OPENAI_MODEL=gpt-3.5-turbo
```

⚠️ **IMPORTANTE:**
- Cole apenas a chave, sem aspas ou texto adicional
- ❌ Errado: `OPENAI_API_KEY="My API Key: sk-proj-..."`
- ✅ Correto: `OPENAI_API_KEY=sk-proj-...`

### 5. Verifique a Instalação

```bash
python3 -c "import pygame, streamlit, numpy, pandas; print('✓ Instalação bem-sucedida!')"
```

---

## 💻 Como Usar

### Método 1: Interface Streamlit (Recomendado)

A interface Streamlit oferece a experiência mais completa e intuitiva.

#### Usando Makefile
```bash
make app
```

Este comando irá:
1. Criar o ambiente virtual
2. Instalar todas as dependências
3. Iniciar o Streamlit automaticamente

#### Manualmente
```bash
streamlit run streamlit/app_streamlit.py
```

A aplicação abrirá automaticamente no navegador em: `http://localhost:8501`

#### Funcionalidades da Interface Streamlit

1. **Seletor de Veículos**: Escolha entre 1 ou 2 veículos
   - **1 veículo**: Otimização tradicional (pode levar múltiplos dias)
   - **2 veículos**: Otimização multi-veículo com depósito (todos os pontos em 1 dia)

2. **Controles**:
   - ▶️ **Iniciar Otimização**: Inicia o processo de otimização (Pygame + Streamlit)
   - 🔄 **Reiniciar**: Inicia um novo processo de otimização automaticamente
   - ❌ **Encerrar**: Encerra a aplicação e limpa o ambiente virtual criado.

3. **Visualização**:
   - Progresso em tempo real com barra de status
   - Gráficos de evolução do fitness
   - Mapa de rotas colorido por prioridade
   - Screenshot final da otimização
   - Métricas detalhadas (fitness, dias, horários)

### Método 2: Interface Pygame (Standalone)

Para executar apenas a visualização Pygame:

#### Usando Makefile
```bash
make run
```

#### Manualmente
```bash
python3 app/main.py      # 1 veículo
python3 app/main_2v.py   # 2 veículos
```

#### Controles Pygame
- **Q** ou **ESC**: Sair do sistema
- **R**: Reiniciar com novos pontos aleatórios

### Método 3: Comandos Individuais

```bash
# Ver todos os comandos disponíveis
make help

# Apenas criar ambiente virtual
make setup

# Apenas instalar dependências
make install

# Executar testes
make test

# Limpar ambiente e cache
make clean

# Ver informações do ambiente
make info
```

---

## 📁 Estrutura do Projeto

```
genetic_route_optimizer/
│
├── README.md                        # Este arquivo
├── requirements.txt                 # Dependências do projeto
├── Makefile                         # Comandos automatizados
├── pytest.ini                       # Configuração do pytest
├── .gitignore                       # Arquivos ignorados pelo Git
├── .env.example                     # Template de configuração (copie para .env)
│
├── app/                             # Aplicações principais
│   ├── main.py                      # Pygame 1 veículo (standalone)
│   └── main_2v.py                   # Pygame 2 veículos (standalone)
│
├── src/                             # Código fonte
│   ├── __init__.py
│   ├── constants.py                 # Constantes do sistema
│   ├── core/                        # Lógica principal
│   │   ├── __init__.py
│   │   ├── service_points.py       # Pontos de atendimento e restrições
│   │   ├── genetic_algorithm.py    # Algoritmo genético (1 veículo)
│   │   └── multi_vehicle.py        # Algoritmo genético (2 veículos)
│   ├── llm/                         # Integração com LLM
│   │   ├── __init__.py
│   │   ├── providers/               # Provedores de LLM
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Interface base
│   │   │   ├── factory.py          # Factory para criar provedores
│   │   │   ├── openai_provider.py  # Provedor OpenAI (nuvem)
│   │   │   └── ollama_provider.py  # Provedor Ollama (local)
│   │   ├── generators/              # Geradores de conteúdo
│   │   │   ├── __init__.py
│   │   │   ├── manual_generator.py      # Gerador de manuais
│   │   │   ├── itinerary_generator.py   # Gerador de roteiros
│   │   │   ├── qa_generator.py          # Gerador de Q&A
│   │   │   ├── qa_system.py             # Sistema de perguntas
│   │   │   └── route_generator.py       # Gerador de rotas
│   │   ├── prompts/                 # Templates de prompts
│   │   │   ├── __init__.py
│   │   │   ├── manual_templates.py      # Templates de manuais
│   │   │   ├── qa_templates.py          # Templates de Q&A
│   │   │   ├── route_prompts.py         # Prompts de rotas
│   │   │   └── route_templates.py       # Templates de rotas
│   │   └── utils/                   # Utilitários LLM
│   │       ├── __init__.py
│   │       ├── formatters.py            # Formatadores de dados
│   │       ├── pdf_generator.py         # Gerador de PDFs
│   │       ├── streamlit_integration.py # Integração Streamlit
│   │       └── validators.py            # Validadores
│   ├── visualization/               # Interface gráfica
│   │   ├── __init__.py
│   │   ├── pygame_viewer.py        # Visualização 1 veículo
│   │   └── pygame_viewer_2v.py     # Visualização 2 veículos
│   └── utils/                       # Utilitários
│       └── __init__.py
│
├── streamlit/                       # Interface web
│   └── app_streamlit.py            # Aplicação Streamlit
│
├── tests/                           # Testes automatizados
│   ├── __init__.py
│   ├── conftest.py                  # Fixtures compartilhadas
│   ├── test_service_points.py      # Testes de pontos de serviço
│   ├── test_genetic_algorithm.py   # Testes do algoritmo genético
│   ├── test_streamlit_utils.py     # Testes de utilitários Streamlit
│   ├── test_integration.py         # Testes de integração
│   ├── test_restrictions.py        # Testes de restrições (legado)
│   └── test_llm/                    # Testes de provedores LLM
│       ├── __init__.py
│       ├── test_openai_provider.py      # Testes do provedor OpenAI
│       ├── test_ollama_provider.py      # Testes do provedor Ollama
│       ├── test_providers.py            # Testes de provedores base
│       ├── test_generators.py           # Testes de geradores
│       ├── test_llm_integration.py      # Testes de integração LLM
│       └── llm_integration_example.py   # Exemplo de uso
│
└── docs/                            # Documentação
    ├── README_RESTRICOES.md        # Detalhes técnicos das restrições
    ├── README_STREAMLIT.md         # Documentação da interface web
    ├── README_TESTS.md             # Documentação dos testes
    └── README2_FIAP_review.md      # Documentação acadêmica FIAP
```

### Descrição das Pastas Principais

| Pasta | Descrição |
|-------|-----------|
| [`app/`](app/) | Aplicações principais (`main.py` para 1 veículo, `main_2v.py` para 2 veículos) |
| [`src/core/`](src/core/) | Lógica principal do algoritmo genético e pontos de serviço |
| [`src/llm/`](src/llm/) | Integração com LLM (OpenAI, Ollama) - provedores, geradores, prompts e utils |
| [`src/llm/providers/`](src/llm/providers/) | Provedores LLM: OpenAI (nuvem), Ollama (local) e Factory Pattern |
| [`src/llm/generators/`](src/llm/generators/) | Geradores de conteúdo: manuais, roteiros, Q&A |
| [`src/llm/utils/`](src/llm/utils/) | Utilitários: formatadores, gerador de PDF, validadores |
| [`src/visualization/`](src/visualization/) | Interfaces gráficas Pygame |
| [`streamlit/`](streamlit/) | Dashboard web interativo |
| [`tests/`](tests/) | Testes automatizados (111 testes, ~75% cobertura) |
| [`tests/test_llm/`](tests/test_llm/) | Testes de provedores LLM (OpenAI, Ollama, integração) |
| [`docs/`](docs/) | Documentação técnica e acadêmica (5 documentos) |

---

## 🧬 Algoritmo Genético

### Parâmetros Principais

```python
POPULATION_SIZE = 100           # Tamanho da população
N_POINTS = 20                   # Número de pontos de atendimento
MUTATION_PROBABILITY = 0.3      # Taxa de mutação (1 veículo)
MUTATION_PROBABILITY = 0.5      # Taxa de mutação (2 veículos)
N_GENERATIONS = Parameterized   # Número de gerações selecionado através de um filtro
```

### Operadores Genéticos

#### 1. População Inicial
- **90%** das rotas geradas com viés de prioridade
- **10%** completamente aleatórias (diversidade)
- Embaralhamento dentro de grupos da mesma prioridade

#### 2. Função de Fitness

A função de fitness é **multi-objetivo** e considera:

```python
fitness = (distância_km × 10) + 
          penalidade_ordem_prioridade +
          penalidade_janela_tempo +
          penalidade_temperatura +
          penalidade_protocolo +
          penalidade_overtime
```

**Componentes das Penalidades:**
- **Distância base**: Distância total × 10
- **Ordem de prioridade**: 5.000 pontos por violação
- **Janelas de tempo**: 50× o tempo de atraso/antecipação
- **Controle de temperatura**: 50.000 pontos por violação
- **Protocolos especiais**: 20.000 pontos por violação
- **Hora extra**: 100 pontos por minuto além da jornada

#### 3. Seleção
- **Método**: Torneio com 5 indivíduos
- **Elitismo**: Melhor solução sempre preservada

#### 4. Crossover (Order Crossover - OX)
- **80%** preserva blocos de prioridade
- **20%** crossover padrão (diversidade)
- Mantém ordem relativa dos elementos

#### 5. Mutação
- **90%** troca apenas dentro do mesmo grupo de prioridade
- **10%** mutação livre (swap ou inversão)
- Respeita restrições de prioridade

---

## 🎯 Restrições e Prioridades

### Hierarquia de Prioridades

| Prioridade | Tipo | Código | Cor | Duração | Restrições |
|------------|------|--------|-----|---------|------------|
| 1 | **Emergência Obstétrica** | EME | 🔴 Vermelho | 30 min | Prioridade máxima, protocolo especial |
| 2 | **Violência Doméstica** | VIO | 🟠 Laranja | 45 min | Janela: 8h-10h, protocolo especial |
| 3 | **Medicamento Hormonal** | MED | 🔵 Azul | 10 min | Temperatura controlada (máx 120 min) |
| 4 | **Pós-Parto** | POS | 🟣 Roxo | 20 min | Janela: 9h-11h |
| 5 | **Regular** | REG | ⚫ Cinza | 15 min | Horário comercial (8h-18h) |
| - | **Depósito** | DEP | 🟡 Amarelo | 0 min | Ponto de partida/retorno (2 veículos) |

### Restrições Implementadas

#### 1. Ordem de Prioridades Hierárquica
- Atendimentos devem seguir ordem: **EME → VIO → MED → POS → REG**
- Permite até **1 parada** entre pontos da mesma prioridade
- Penalidade: **5.000 pontos** por violação

#### 2. Janelas de Tempo Específicas
- **VIO**: 8h às 10h (horário discreto)
- **POS**: 9h às 11h
- **MED**: 8h às 18h
- Penalidade: **50× o tempo** de atraso/antecipação

#### 3. Controle de Temperatura
- Medicamentos hormonais (MED) requerem temperatura controlada
- Tempo máximo sem controle: **120 minutos**
- Penalidade: **50.000 pontos** por violação

#### 4. Protocolos Especiais
- Casos de violência (VIO) e emergências (EME) requerem protocolos especiais
- Tempo mínimo de atendimento: **30 minutos**
- Penalidade: **20.000 pontos** por violação

#### 5. Horário Comercial
- Atendimentos apenas entre **8h e 18h**
- Pausas noturnas automáticas
- Sistema calcula dias necessários

#### 6. Tempo Máximo de Trabalho
- Jornada máxima: **8 horas por dia** (480 minutos)
- Penalidade: **100 pontos** por minuto extra

---

## 🖥 Interfaces Disponíveis

### 1. Interface Streamlit (Web)

**Características:**
- Dashboard web completo e responsivo
- Seleção de 1 ou 2 veículos
- Visualização dupla (Pygame + Streamlit)
- Progresso em tempo real
- Gráficos interativos
- Screenshot final automático
- Métricas detalhadas

**Como acessar:**
```bash
make app
# ou
streamlit run streamlit/app_streamlit.py
```

Acesse: `http://localhost:8501`

### 2. Interface Pygame (Desktop)

**Características:**
- Visualização animada em tempo real
- Gráfico de evolução do fitness
- Mapa de rotas colorido
- Painel de informações detalhadas
- Controles por teclado

**Como executar:**
```bash
make run
# ou
python3 app/main.py      # 1 veículo
python3 app/main_2v.py   # 2 veículos
```

---

## 🤖 Assistente Inteligente com IA

O sistema inclui um **Assistente Inteligente** baseado em LLMs (Large Language Models) que gera automaticamente documentação e responde perguntas sobre as rotas otimizadas.

### Provedores Suportados

#### 1. 🌐 OpenAI (Nuvem)
- **Modelos**: GPT-3.5-turbo, GPT-4, GPT-4-turbo
- **Vantagens**: Alta qualidade, rápido, sem setup local
- **Desvantagens**: Pago (por token), requer internet, dados enviados para OpenAI
- **Configuração**: Requer API Key da OpenAI

#### 2. 🏠 Ollama (Local)
- **Modelos**: Llama2, Mistral, CodeLlama, Neural-Chat
- **Vantagens**: Gratuito, privado (dados locais), offline, sem limites
- **Desvantagens**: Requer hardware (8GB+ RAM), modelos menores, setup inicial
- **Configuração**: Requer instalação do Ollama e download de modelos

### Funcionalidades

#### 1. 📋 Manual de Instruções
Gera manual profissional para equipe de transporte com:
- Instruções detalhadas para cada parada
- Protocolos específicos por tipo de atendimento
- Alertas de prioridades e janelas de tempo
- Checklist pré-operação
- **Exportação em PDF** com formatação profissional

#### 2. 🗺️ Roteiro Detalhado
Cria roteiro passo a passo para motoristas com:
- Sequência de paradas com horários
- Distâncias e tempos de viagem
- Observações importantes
- Resumo de prioridades
- **Exportação em PDF** com formatação profissional

#### 3. 💬 Perguntas & Respostas
Sistema de Q&A em linguagem natural:
- Perguntas sobre a rota otimizada
- Sugestões inteligentes de perguntas
- Histórico de conversação
- Respostas contextualizadas

#### 4. 📦 Suporte Multi-Veículo
Para rotas com 2 veículos:
- Gera documentos separados para cada veículo
- **Download em ZIP** com todos os PDFs
- Manuais, roteiros e resumos de prioridades individualizados

### Como Usar

#### Opção 1: OpenAI (Nuvem)

1. **Configure a API Key** no arquivo `.env`:
   ```bash
   cp .env.example .env
   # Edite .env e adicione:
   # LLM_PROVIDER=openai
   # OPENAI_API_KEY=sk-proj-sua-chave-aqui
   # OPENAI_MODEL=gpt-3.5-turbo
   ```

2. **Obtenha sua API Key**:
   - Acesse: https://platform.openai.com/api-keys
   - Crie uma conta ou faça login
   - Clique em "Create new secret key"
   - Copie a chave e adicione no `.env`

#### Opção 2: Ollama (Local)

1. **Instale o Ollama**:
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows: baixe em https://ollama.ai/download
   ```

2. **Baixe um modelo**:
   ```bash
   ollama pull llama2
   ```

3. **Configure no `.env`**:
   ```bash
   cp .env.example .env
   # Edite .env e adicione:
   # LLM_PROVIDER=ollama
   # OLLAMA_MODEL=llama2
   # OLLAMA_BASE_URL=http://localhost:11434
   ```

4. **Inicie o Ollama** (se não estiver rodando):
   ```bash
   ollama serve
   ```

#### Usando o Assistente

1. **Execute a otimização** no Streamlit
2. **Acesse a aba "🤖 Assistente Inteligente"** após os resultados
3. **Gere documentos** ou faça perguntas sobre a rota

### Exemplos de Perguntas

- "Quantas paradas de emergência temos hoje?"
- "Como devo transportar os medicamentos hormonais?"
- "Quais pontos têm janelas de tempo restritas?"
- "Qual é a distância total da rota?"
- "Em que horário termina a rota?"

### Exportação de Documentos

- **1 Veículo**: Botões de download individual para cada documento (PDF)
- **2 Veículos**: Botão de download em ZIP com documentos de ambos os veículos

Para documentação completa sobre esta funcionalidade, consulte: **[docs/README_LLM.md](docs/README_LLM.md)**

---

## 🧪 Testes

O projeto possui **140 testes automatizados** com cobertura de ~75% do código.

### Executar Todos os Testes

```bash
# Usando Makefile
make test

# Manualmente
pytest tests/ -v
```

### Executar Testes Específicos

```bash
# Testes de pontos de serviço
pytest tests/test_service_points.py -v

# Testes do algoritmo genético
pytest tests/test_genetic_algorithm.py -v

# Testes de integração
pytest tests/test_integration.py -v

# Teste específico por classe e método
pytest tests/test_service_points.py::TestPriorityOrdering::test_sort_by_priority_correct_order -v
```

### Testes LLM (Provedores de IA)

O projeto inclui testes para integração com provedores LLM (OpenAI e Ollama):

#### Testes OpenAI

```bash
# Executar todos os testes OpenAI (pede confirmação - consome tokens)
make test-openai

# Executar apenas testes básicos (NÃO consome tokens)
make test-openai-basic

# Executar apenas testes de integração (consome tokens)
make test-openai-integration
```

**Tipos de Testes OpenAI:**
- **Básicos**: Inicialização, configuração, parâmetros - NÃO consome tokens
- **Integração**: Conexão real com API, geração de texto - Consome tokens da OpenAI

⚠️ **ATENÇÃO:** Testes de integração OpenAI consomem tokens da sua conta. Use `make test-openai-basic` para testes sem custo.

#### Testes Ollama

```bash
# Executar todos os testes Ollama (pede confirmação - requer Ollama rodando)
make test-ollama

# Executar apenas testes básicos (NÃO requer Ollama)
make test-ollama-basic

# Executar apenas testes de integração (requer Ollama rodando)
make test-ollama-integration
```

**Tipos de Testes Ollama:**
- **Básicos**: Inicialização, configuração, parâmetros - NÃO requer Ollama rodando
- **Integração**: Conexão real com Ollama, geração de texto - Requer Ollama rodando

⚠️ **ATENÇÃO:** Testes de integração Ollama requerem que o Ollama esteja rodando (`ollama serve`).

#### Testes de Integração Completa

```bash
# Testes de integração usando provedor configurado no .env
make test-llm-integration
```

Usa o provedor configurado em `LLM_PROVIDER` no arquivo `.env` (openai ou ollama).

### Cobertura de Código

```bash
# Gerar relatório de cobertura
make test-cov

# Gerar relatório HTML de cobertura
make test-html
# Abrir htmlcov/index.html no navegador
```

### Estatísticas de Testes

- **Total**: 140 testes
- **Unitários**: 64 testes
- **Interface**: 13 testes
- **Integração**: 18 testes
- **LLM**: 45 testes (OpenAI, Ollama, geradores, integração completa)

### Cobertura de Código

| Módulo | Cobertura | Descrição |
|--------|-----------|-----------|
| [`src/core/service_points.py`](src/core/service_points.py) | ~80% | Pontos de atendimento, prioridades e restrições |
| [`src/core/genetic_algorithm.py`](src/core/genetic_algorithm.py) | ~75% | Algoritmo genético (1 veículo) |
| [`src/core/multi_vehicle.py`](src/core/multi_vehicle.py) | ~70% | Algoritmo genético (2 veículos) |
| [`src/llm/providers/openai_provider.py`](src/llm/providers/openai_provider.py) | ~90% | Provedor OpenAI para LLM |
| [`src/visualization/pygame_viewer.py`](src/visualization/pygame_viewer.py) | ~40% | Interface gráfica Pygame |
| [`streamlit/app_streamlit.py`](streamlit/app_streamlit.py) | ~50% | Interface web Streamlit |

**Cobertura Geral**: ~75% do código core (lógica de negócio)

Para mais detalhes, consulte: [`docs/README_TESTS.md`](docs/README_TESTS.md)

---

## 📚 Documentação Adicional

> 💡 **Navegação**:
> - **No VSCode**: Clique nos links para abrir o documento. Use `Ctrl+K V` (Windows/Linux) ou `Cmd+K V` (macOS) para preview lado a lado.
> - **No GitHub**: Os links abrem diretamente no navegador.

### Documentação Técnica
- **[Restrições e Implementação](docs/README_RESTRICOES.md)** - Detalhes técnicos das restrições implementadas
- **[Interface Streamlit](docs/README_STREAMLIT.md)** - Guia completo da interface web
- **[Integração com LLMs](docs/README_LLM.md)** - Assistente Inteligente com IA (manuais, roteiros e Q&A)
- **[Testes Automatizados](docs/README_TESTS.md)** - Documentação dos 95 testes

### Documentação Acadêmica
- **[Documentação FIAP](docs/README2_FIAP_review.md)** - Documentação completa do projeto acadêmico

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError"

**Solução**: Certifique-se de que o ambiente virtual está ativado e as dependências instaladas:
```bash
source .ga_routes/bin/activate  # macOS/Linux
make install
```

### Erro: "pygame.error: No available video device"

**Solução**: Certifique-se de que está executando em um ambiente com display gráfico. Para servidores sem GUI, use apenas a interface Streamlit.

### Erro: "Port already in use" (Streamlit)

**Solução**: Mate o processo que está usando a porta 8501:
```bash
# macOS/Linux
lsof -ti:8501 | xargs kill -9

# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

### Pygame não abre

**Solução**: Verifique a instalação do Pygame:
```bash
pip list | grep pygame
pip install --upgrade pygame
```

### Testes falhando

**Solução**: Execute os testes para diagnóstico:
```bash
make test
# ou
pytest tests/ -v --tb=short
```

### Performance lenta

**Solução**: Ajuste os parâmetros do algoritmo:
- Reduza `POPULATION_SIZE` (ex: 50)
- Reduza `N_GENERATIONS` (ex: 100)
- Aumente `FPS` para visualização mais rápida

---

## 📊 Métricas e Resultados

### Unidades de Medida

#### Distância
- **1 unidade de coordenada (distância euclidiana) = 100 metros (0,1 km)**
- **Fator de escala**: 0.1
- **Fórmula**: `distância_km = distância_unidades × 0.1`

#### Tempo de Viagem
- **Velocidade padrão**: 60 km/h
- **Fórmula**: `tempo_minutos = (distância_km / 60) × 60`

### Resultados Típicos

Para 20 pontos de atendimento:
- **Fitness**: 1.000 - 10.000 (rotas válidas)
- **Distância**: 50 - 300 km
- **Tempo**: 4 - 8 horas
- **Dias**: 1 - 3 dias
- **Convergência**: 50 - 100 gerações

---

## 🔮 Melhorias Futuras

- [x] Interface web com Streamlit ✅
- [x] Suporte para múltiplos veículos ✅
- [x] Testes automatizados completos ✅
- [x] Integração com LLMs (OpenAI e Ollama) ✅
- [x] Geração de PDFs profissionais ✅
- [x] Suporte multi-veículo para documentos ✅
- [ ] Exportação de rotas para CSV/JSON
- [ ] Análise estatística de múltiplas execuções
- [ ] Integração com APIs de mapas reais (Google Maps, OpenStreetMap)
- [ ] Otimização multi-objetivo (Pareto)
- [ ] Histórico de execuções no Streamlit
- [ ] Suporte para mais de 2 veículos
- [ ] Interface de configuração de parâmetros
- [ ] Suporte para mais provedores LLM (Anthropic Claude, Google Gemini)
- [ ] Tradução multilíngue de documentos
- [ ] Integração com WhatsApp/Telegram para notificações

---

## 👨‍💻 Autores

Desenvolvido como projeto acadêmico da **Pós-Tech FIAP - Fase 2 - IA para Devs**.

**Fernanda Valdevino**
- Projeto: Sistema de Otimização de Rotas com Algoritmo Genético
- Instituição: FIAP - Pós-Graduação IA para Devs
- Fase: 2 (Março/2026)

🐙 [@fernandavaldevino](https://github.com/fernandavaldevino)

---

## 📝 Licença

Este projeto é desenvolvido para fins educacionais como parte do programa de Pós-Graduação em IA para Devs da FIAP.

---

## 🙏 Agradecimentos

- **FIAP** - Pela oportunidade e suporte acadêmico
- **Comunidade Python** - Pelas excelentes bibliotecas open-source
- **Pygame Community** - Pela biblioteca de visualização
- **Streamlit Team** - Pelo framework web intuitivo
- **OpenAI** - Pelos modelos GPT e API acessível
- **Ollama Team** - Por democratizar o acesso a LLMs locais

---

<div align="center">

**Made with ❤️ and ☕**

*Sistema de Otimização de Rotas - Algoritmo Genético*

</div>

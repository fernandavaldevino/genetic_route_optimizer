# 🚗 Sistema de Otimização de Rotas com Algoritmo Genético

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Run-4285F4?style=flat&logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Terraform](https://img.shields.io/badge/Terraform-1.x-7B42BC?style=flat&logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Pytest](https://img.shields.io/badge/Pytest-7.4+-0A9EDC?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-55%25-yellow?style=flat)](docs/README_TESTS.md)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat)](LICENSE)

Sistema inteligente de otimização de rotas para múltiplos veículos utilizando Algoritmo Genético, com integração de LLM (Large Language Models) para geração de relatórios e análises. Desenvolvido como projeto da Pós-Tech FIAP.

## 📋 Índice

- [Características](#-características)
- [Arquitetura](#-arquitetura)
- [Tecnologias](#-tecnologias)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [API](#-api)
- [Telegram Bot](#-telegram-bot)
- [Execução de Testes](#-execução-de-testes)
- [Documentação](#-documentação)
- [Licença](#-licença)
- [Contato](#-contato)

## 🎯 Características

### 🧬 Algoritmo Genético e Otimização

- ✅ **Algoritmo Genético Avançado**: Implementação otimizada com operadores especializados
  - Seleção por torneio adaptativo
  - Crossover com preservação de blocos de prioridade (Order Crossover - OX)
  - Mutação dinâmica respeitando grupos de prioridade
  - Elitismo para preservar melhores soluções
  - População inicial com viés de prioridade (90% ordenada, 10% aleatória)
  
- ✅ **Suporte Multi-Veículos**: Otimização para 1 ou 2 veículos simultaneamente
  - Balanceamento automático de carga entre veículos
  - Rotas independentes com depósito compartilhado
  - Visualização diferenciada por veículo (cores distintas)

- ✅ **Critérios de Parada Inteligentes**:
  - Modo normal: Número fixo de gerações (configurável via [`MAX_GENERATIONS`](src/constants.py:15))
  - Modo infinito: Parada por estagnação (5000 gerações sem melhoria)
  - Detecção automática de convergência

### 🏥 Restrições e Prioridades

Documentação completa: [`README_RESTRICOES.md`](docs/README_RESTRICOES.md)

- ✅ **Sistema de Prioridades Hierárquico**:
  - **Prioridade 1**: Emergências Obstétricas (EME) - Atendimento imediato, 30 min
  - **Prioridade 2**: Violência Doméstica (VIO) - Protocolo especial, janela 8h-10h (1v) ou 8h-12h (2v), 45 min
  - **Prioridade 3**: Medicamentos Hormonais (MED) - Temperatura controlada 2-8°C, 10 min
  - **Prioridade 4**: Pós-Parto (POS) - Janela 9h-11h (1v) ou 9h-13h (2v), 20 min
  - **Prioridade 5**: Regular (REG) - Atendimento padrão, 15 min

- ✅ **Janelas de Tempo Específicas**:
  - Validação automática de horários de atendimento
  - Penalidades proporcionais por atrasos (50x por minuto)
  - Penalidades por antecipação (10x por minuto)
  - Horário comercial: 8h às 18h com pausas noturnas automáticas

- ✅ **Controle de Temperatura**:
  - Medicamentos hormonais requerem temperatura controlada (2-8°C)
  - Tempo máximo sem controle: 120 minutos
  - Penalidade massiva por violação: 50.000 pontos

- ✅ **Protocolos Especiais**:
  - Casos de violência doméstica com discrição absoluta
  - Emergências obstétricas com equipamentos especiais
  - Tempo mínimo de atendimento garantido
  - Penalidade por violação: 20.000 pontos

- ✅ **Restrições de Entrega**:
  - Medicamentos prioritários (EME, VIO, MED, POS) devem ser entregues no Dia 1
  - Penalidade massiva: 1.000.000 pontos por medicamento prioritário fora do Dia 1
  - Atendimentos regulares (REG) podem ser distribuídos em dias subsequentes

### 🎨 Visualização e Interface

Documentação completa: [`README_STREAMLIT.md`](docs/README_STREAMLIT.md)

- ✅ **Interface Pygame Interativa**:
  - Visualização em tempo real da evolução do algoritmo
  - Mapa de rotas colorido por prioridade e veículo
  - Gráfico de evolução do fitness
  - Painel de informações detalhadas com ordem de atendimento
  - Indicadores visuais de dias (D1, D2, D3+) com cores distintas
  - Setas direcionais mostrando fluxo da rota
  - Controles: R (reiniciar), Q/ESC (sair), SPACE (pausar)

- ✅ **Dashboard Streamlit Web**:
  - Interface web moderna e responsiva
  - Configuração interativa de parâmetros
  - Seleção de número de veículos (1 ou 2)
  - Modo de gerações: Normal (100) ou Infinito
  - Visualização de métricas em tempo real
  - Exportação de resultados
  - Integração com assistente LLM

- ✅ **Visualização Multi-Veículos**:
  - Rotas diferenciadas por cores (ciano e verde)
  - Camadas de visualização: prioridade + veículo
  - Estatísticas separadas por veículo
  - Balanceamento visual de carga

### 🤖 Assistente Inteligente com LLM

Documentação completa: [`README_LLM.md`](docs/README_LLM.md)

- ✅ **Geração de Manuais de Instruções**:
  - Manual completo para equipe de transporte
  - Instruções específicas por tipo de atendimento
  - Seção de prioridades e alertas
  - Checklist pré-rota com itens essenciais
  - Orientações para imprevistos

- ✅ **Roteiro Detalhado de Visitas**:
  - Roteiro passo a passo para motoristas
  - Horários de chegada previstos
  - Tempo estimado em cada local
  - Próximo destino e tempo de viagem
  - Observações importantes por parada
  - Destaque visual para paradas prioritárias

- ✅ **Sistema de Perguntas e Respostas (Q&A)**:
  - Perguntas em linguagem natural sobre a rota
  - Histórico de conversação
  - Sugestões inteligentes de perguntas
  - Análise contextualizada de prioridades e janelas de tempo
  - Exemplos: "Qual o próximo atendimento prioritário?", "Quantas emergências temos hoje?"

- ✅ **Suporte a Múltiplos Provedores LLM**:
  - **OpenAI**: GPT-3.5-turbo, GPT-4, GPT-4-turbo
  - **Ollama**: Modelos locais (Llama2, Mistral, CodeLlama)
  - Configuração via arquivo `.env`
  - Validação automática de conexão
  - Temperatura ajustável (0.0 - 2.0)

### 📡 API REST e Integrações

- ✅ **API FastAPI Completa**:
  - Documentação automática (Swagger/OpenAPI)
  - Endpoints de otimização de rotas
  - Health checks e métricas
  - Validação de dados com Pydantic
  - Tratamento global de exceções
  - Middleware CORS configurável

- ✅ **Telegram Bot**:
  - Interface conversacional para otimização
  - Comandos: `/start`, `/help`, `/optimize`, `/status`
  - Suporte a webhooks (produção) e polling (desenvolvimento)
  - Integração com rotas otimizadas
  - Envio de mapas e resultados

- ✅ **Deploy em Cloud (Google Cloud Platform)**:
  
  Documentação completa: [`ARQUITETURA_GCP.md`](docs/ARQUITETURA_GCP.md)
  
  - Google Cloud Run (serverless)
  - Google Artifact Registry para imagens Docker
  - Terraform para infraestrutura como código (IaC)
  - Google Cloud Build para CI/CD
  - Configuração de variáveis de ambiente
  - Escalabilidade automática
  - Diagrama de arquitetura completo

### 🧪 Testes e Qualidade

Documentação completa: [`README_TESTS.md`](docs/README_TESTS.md)

- ✅ **Cobertura de Testes Abrangente**:
  - **264 testes automatizados**
  - **Cobertura geral: ~55%**
  - **Cobertura de módulos críticos: ~75%**

- ✅ **Testes por Módulo**:
  - **Core - Algoritmo Genético**: 95%+ cobertura (32 testes)
  - **Core - Service Points**: 95%+ cobertura (20 testes)
  - **API REST**: 90%+ cobertura (57 testes)
  - **Cloud/Deployment**: 85%+ cobertura (33 testes)
  - **Telegram Bot**: 75%+ cobertura (32 testes)
  - **LLM Integration**: 70%+ cobertura (55 testes)
  - **Integração E2E**: 80%+ cobertura (16 testes)
  - **Streamlit**: 30%+ cobertura (17 testes)
  - **Elitismo Dinâmico**: 100% cobertura (2 testes)

- ✅ **Tipos de Testes**:
  - Testes unitários (54 testes)
  - Testes de integração (16 testes)
  - Testes de API (57 testes: básicos, avançados e integração)
  - Testes de deployment (33 testes)
  - Testes de Telegram Bot (32 testes)
  - Testes de LLM (55 testes: múltiplos provedores)
  - Testes de interface (17 testes)

- ✅ **Ferramentas de Teste**:
  - pytest com fixtures compartilhadas
  - pytest-cov para cobertura
  - Relatórios HTML e XML
  - Marcadores para testes rápidos/lentos
  - Integração com CI/CD

### 🔧 Configuração e Personalização

- ✅ **Parâmetros Configuráveis** ([`src/constants.py`](src/constants.py)):
  - Tamanho da população
  - Número máximo de gerações
  - Probabilidade de mutação
  - Taxa de crossover
  - Tamanho da elite
  - Velocidade de visualização (FPS)

- ✅ **Modos de Operação**:
  - Modo desenvolvimento (local)
  - Modo produção (cloud)
  - Modo debug com logs detalhados
  - Modo headless (sem interface gráfica)

### 🛠️ Integrações e Tecnologias

- 🤖 **OpenAI GPT**: Geração de relatórios e análises inteligentes
- 🦙 **Ollama**: Suporte para modelos locais (Llama, Mistral, etc.)
- 📱 **Telegram**: Bot para interação via mensagens
- ☁️ **Google Cloud Run**: Deploy serverless escalável
- 🏗️ **Terraform**: Infraestrutura como código (IaC)
- 🐳 **Docker**: Containerização multiplataforma
- 🎨 **Pygame**: Visualização gráfica interativa
- 🌐 **Streamlit**: Dashboard web moderno

## 🏗️ Arquitetura

```
genetic_route_optimizer/
├── api/                      # API REST (FastAPI)
│   ├── main.py              # Endpoints da API
│   └── models.py            # Modelos Pydantic
├── src/
│   ├── core/                # Algoritmo Genético
│   │   ├── genetic_algorithm.py
│   │   ├── multi_vehicle.py
│   │   └── service_points.py
│   ├── llm/                 # Integração LLM
│   │   ├── providers/       # OpenAI, Ollama
│   │   ├── generators/      # Geradores de conteúdo
│   │   └── prompts/         # Templates de prompts
│   ├── visualization/       # Visualização Pygame
│   └── utils/              # Utilitários
├── telegram_bot/            # Bot do Telegram
│   ├── bot.py              # Lógica do bot
│   └── webhook_handler.py  # Handler de webhooks
├── streamlit/              # Dashboard Streamlit
│   └── app_streamlit.py
├── terraform/              # Infraestrutura (IaC)
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── tests/                  # Testes automatizados
├── docs/                   # Documentação
├── Dockerfile             # Container Docker
├── cloudbuild.yaml        # Google Cloud Build
├── main.py               # API minimalista Cloud Run
└── requirements.txt      # Dependências Python
```

## 🛠️ Tecnologias

### Backend
- **Python 3.11+**: Linguagem principal
- **FastAPI**: Framework web moderno e rápido
- **Uvicorn**: Servidor ASGI de alta performance
- **Pydantic**: Validação de dados

### Algoritmo
- **NumPy**: Computação numérica
- **Algoritmo Genético**: Otimização heurística customizada

### LLM & IA
- **OpenAI API**: GPT-4, GPT-3.5
- **Ollama**: Modelos locais (Llama 3, Mistral, etc.)
- **LangChain**: Framework para aplicações LLM

### Visualização
- **Pygame**: Visualização gráfica de rotas
- **Streamlit**: Dashboard web interativo
- **Matplotlib**: Gráficos e plots

### Cloud & DevOps
- **Google Cloud Run**: Serverless container platform
- **Google Artifact Registry**: Registro de imagens Docker
- **Terraform**: Infraestrutura como código (IaC)
- **Docker**: Containerização
- **Google Cloud Build**: CI/CD

### Comunicação
- **python-telegram-bot**: Bot do Telegram
- **Webhooks**: Integração em tempo real

## 📦 Instalação

### Pré-requisitos

- **Python 3.11+**: Linguagem principal do projeto
- **pip**: Gerenciador de pacotes Python (incluído com Python)
- **Git**: Para clonar o repositório
- **Docker** (opcional): Para containerização
- **Google Cloud SDK** (opcional): Para deploy no GCP
- **Terraform** (opcional): Para infraestrutura como código

### Início Rápido (Recomendado)

A forma mais rápida de começar é usando o comando [`make app`](Makefile:653), que automatiza todo o processo:

```bash
# 1. Clonar o repositório
git clone https://github.com/seu-usuario/genetic_route_optimizer.git
cd genetic_route_optimizer

# 2. Editar .env com suas credenciais (⚠️ Fazer antes do comando make app)
#    Verificar seção "Configuração do Arquivo `.env`" abaixo
.env

# 3. Executar setup completo e iniciar aplicação
make app
```

O comando [`make app`](Makefile:653) automaticamente:
- ✅ Cria o ambiente virtual (`.ga_routes`)
- ✅ Instala todas as dependências do [`requirements.txt`](requirements.txt)
- ✅ Verifica e inicia o Ollama (se instalado)
- ✅ Inicia a API FastAPI em background (porta 8080)
- ✅ Inicia o Bot do Telegram (se configurado)
- ✅ Abre o Dashboard Streamlit no navegador

### Instalação Manual (Alternativa ao make app)

Se preferir executar cada etapa de instalação manualmente:

```bash
# 1. Clonar o repositório
git clone https://github.com/seu-usuario/genetic_route_optimizer.git
cd genetic_route_optimizer

# 2. Configurar variáveis de ambiente com suas credenciais (⚠️ Fazer antes de executar a aplicação)
#    Verificar seção "Configuração do Arquivo `.env`" abaixo
.env 

# 3. Criar ambiente virtual
python3 -m venv .ga_routes

# 4. Ativar ambiente virtual
source .ga_routes/bin/activate  # Linux/Mac
# ou
.ga_routes\Scripts\activate  # Windows

# 5. Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# 6. Iniciar serviços manualmente
make start-api      # API FastAPI (porta 8080)
make start-bot      # Bot do Telegram (opcional)
make streamlit      # Dashboard Streamlit (porta 8501)
```

### Configuração do Arquivo `.env`

**⚠️ IMPORTANTE:** Configure o arquivo `.env` ANTES de executar [`make app`](Makefile:653), pois ele contém variáveis essenciais para o funcionamento da aplicação.

```bash
# ===== PROVEDOR PRINCIPAL =====
# Opções: openai, ollama
LLM_PROVIDER=openai

# ===== CONFIGURAÇÃO OPENAI =====
# Obtenha sua API Key em: https://platform.openai.com/api-keys
# IMPORTANTE: Cole apenas a chave, sem aspas ou texto adicional
OPENAI_API_KEY=sua-chave-aqui

# Modelos disponíveis: gpt-3.5-turbo, gpt-4, gpt-4-turbo
OPENAI_MODEL="gpt-3.5-turbo"

# Temperatura (0.0 = mais determinístico, 2.0 = mais criativo)
OPENAI_TEMPERATURE=0.7

# ===== CONFIGURAÇÃO OLLAMA (LOCAL) =====
# Para usar modelos locais com Ollama
# Instale Ollama: https://ollama.ai
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TEMPERATURE=0.7

# ===== CONFIGURAÇÃO BOT TELEGRAM =====
# Obtenha o token do bot em: https://t.me/BotFather
TELEGRAM_BOT_TOKEN=seu-token-aqui

# Nome de usuário do bot (sem @)
TELEGRAM_BOT_USERNAME=SeuBotUsername

# Nome do bot
BOT_NAME=SeuBotName

# ===== GOOGLE CLOUD (para deploy) =====
GOOGLE_CLOUD_PROJECT=seu-projeto-gcp
GOOGLE_APPLICATION_CREDENTIALS=./key.json
```

## 🚀 Uso

### Início Automático

O comando [`make app`](Makefile:653) é a forma mais simples de iniciar todos os serviços:

```bash
make app
```

Este comando executa automaticamente:
- Cria o ambiente virtual
- Instala todas as dependências
- Inicia a API FastAPI em background
- Inicia o Bot do Telegram (se configurado)
- Abre o Dashboard Streamlit

### Execução Individual de Serviços

Após a instalação, você pode iniciar cada serviço **individualmente** conforme necessário:

#### 1. API REST (FastAPI)

```bash
# Usando Makefile (recomendado)
make start-api

# Ou diretamente com uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080

# Parar a API
make stop-api
```

**Acesso:**
- Documentação Swagger: http://localhost:8080/docs
- Documentação ReDoc: http://localhost:8080/redoc
- Health Check: http://localhost:8080/health

#### 2. Dashboard Streamlit

```bash
# Usando Makefile (recomendado)
make streamlit

# Ou diretamente
streamlit run streamlit/app_streamlit.py
```

**Acesso:** http://localhost:8501

#### 3. Bot do Telegram

```bash
# Usando Makefile (recomendado)
make start-bot

# Ou diretamente (modo polling)
python telegram_bot/bot.py

# Parar o bot
make stop-bot
```

#### 4. Visualização Pygame (Sistema Principal)

```bash
# Usando Makefile (recomendado)
make run

# Ou diretamente
python app/main.py
```

### 5. Exemplo de Uso Programático

```python
from src.core.genetic_algorithm import GeneticAlgorithm
from src.core.service_points import ServicePoint

# Definir pontos de serviço
points = [
    ServicePoint(id=0, x=0, y=0, demand=0, priority=1, time_window=(0, 480)),
    ServicePoint(id=1, x=10, y=20, demand=5, priority=2, time_window=(60, 180)),
    ServicePoint(id=2, x=30, y=40, demand=3, priority=1, time_window=(120, 240)),
]

# Configurar algoritmo genético
ga = GeneticAlgorithm(
    service_points=points,
    population_size=100,
    generations=500,
    mutation_rate=0.01,
    elite_size=20
)

# Executar otimização
best_route, best_distance = ga.run()

print(f"Melhor rota: {best_route}")
print(f"Distância total: {best_distance:.2f} km")
```

## 📡 API

### Documentação Interativa

**IMPORTANTE:** Antes de acessar a documentação local, inicie a API com `make start-api`

Acesse a documentação Swagger em:
- **Local**: http://localhost:8080/docs (requer `make start-api`)
- **Produção**: https://genetic-route-optimizer-api-wzfyhoxurq-uc.a.run.app/docs

### Exemplo de Requisição

```bash
# Health Check
curl https://genetic-route-optimizer-api-wzfyhoxurq-uc.a.run.app/health

# Resposta
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-03-17T22:58:34.109027"
}
```

### Modelos de Dados

```python
from pydantic import BaseModel
from typing import List, Tuple

class ServicePointInput(BaseModel):
    id: int
    x: float
    y: float
    demand: int
    priority: int
    time_window: Tuple[int, int]

class OptimizationRequest(BaseModel):
    service_points: List[ServicePointInput]
    num_vehicles: int = 1
    vehicle_capacity: int = 100
    population_size: int = 100
    generations: int = 500
```

## 🤖 Telegram Bot

### Comandos Disponíveis

**Comandos de Rota:**
- `/start` - Iniciar o bot e exibir mensagem de boas-vindas
- `/iniciar_rota` - Iniciar rota do dia
- `/proxima` - Ver próxima parada
- `/concluido` - Marcar parada como concluída
- `/concluir_rota` - Finalizar rota do dia
- `/encerrar_rota` - Encerrar rota sem concluir todas as paradas
- `/recarregar` - Recarregar rota mais recente

**Comandos de Consulta:**
- `/help` - Exibir ajuda e lista de comandos disponíveis
- `/rota` - Ver rota completa (todas as paradas)
- `/paradas` - Número total de paradas
- `/instrucoes` - Instruções gerais de transporte

**Tipos de Atendimento:**
- 🔴 **EME** - Emergência Obstétrica (Prioridade 1)
- 🟠 **VIO** - Violência Doméstica (Prioridade 2)
- 🔵 **MED** - Medicamento Hormonal (Prioridade 3)
- 🟣 **POS** - Pós-Parto (Prioridade 4)
- ⚫ **REG** - Regular (Prioridade 5)

### Funcionalidades

- ✅ **Suporte Multi-Veículos**: Selecione veículo 1 ou 2 com `/start` ou `/start veiculo2`
- ✅ **Teclados Interativos**: Botões inline para navegação rápida
- ✅ **Agrupamento por Dias**: Rotas multi-dia são agrupadas automaticamente
- ✅ **Integração com Otimização**: Carrega automaticamente rotas otimizadas de `data/routes/`
- ✅ **Confirmação de Encerramento**: Proteção contra encerramento acidental da rota

### Exemplo de Uso

```
Usuário: /start
Bot: 👋 Bem-vindo ao Assistente de Rotas!
     🟢 Veículo 1
     
     🤖 Sou seu assistente virtual para informações sobre rotas...
     [Botões: Ver Rota | Iniciar Rota | Instruções | Ajuda]

Usuário: [Clica em "Iniciar Rota"]
Bot: 🚀 ROTA INICIADA!
     
     📊 Resumo do Dia:
     • Total de paradas: 12
     • Distância total: 85.5 km
     • Tempo estimado: 6h 30min
     ...

Usuário: /proxima
Bot: ➡️ PRÓXIMA PARADA (12 restantes)
     
     🔴 Parada 1 - EME
     🎯 Prioridade 1
     
     📍 Endereço: Rua das Flores, 123
     🕐 Horário: 08:15
     ⏱️ Duração: 30 min
     ...

Usuário: /concluido
Bot: ✅ Atendimento 1 concluído!
     
     ➡️ PRÓXIMA PARADA (11 restantes)
     ...
```

## 🧪 Execução de Testes

### Comandos do Makefile (Recomendado)

O projeto possui comandos [`make`](Makefile) preparados para facilitar a execução de testes:

```bash
# Executar testes (pergunta se inclui testes pagos)
make test

# Executar TODOS os testes (incluindo testes pagos sem perguntar)
make all-tests

# Executar teste específico
make test-specific FILE=test_service_points.py

# Testes por categoria
make test-api                 # Todos os testes da API
make test-api-unit            # Apenas testes unitários da API
make test-api-integration     # Apenas testes de integração da API
make test-telegram            # Testes do Bot do Telegram
make test-cloud               # Testes de Cloud/Deployment

# Testes LLM - OpenAI
make test-openai              # Todos os testes OpenAI
make test-openai-basic        # Testes básicos (sem gastar tokens)
make test-openai-integration  # Testes de integração (gasta tokens)

# Testes LLM - Ollama
make test-ollama              # Todos os testes Ollama
make test-ollama-basic        # Testes básicos (sem conexão)
make test-ollama-integration  # Testes de integração (requer Ollama)

# Relatórios de cobertura
make test-cov                 # Mostra cobertura de código
make test-html                # Gera relatório HTML
make test-coverage-report     # Relatório completo (HTML + Terminal)
```

### Execução Manual com Pytest

Se preferir executar os testes diretamente com [`pytest`](pytest.ini):

```bash
# Ativar ambiente virtual
source .ga_routes/bin/activate  # Linux/Mac
# ou
.ga_routes\Scripts\activate  # Windows

# Executar todos os testes
pytest

# Com cobertura detalhada
pytest --cov=src --cov=api --cov=telegram_bot --cov-report=html

# Testes específicos por módulo
pytest tests/test_genetic_algorithm.py
pytest tests/test_api.py
pytest tests/test_cloud_deployment.py
pytest tests/test_llm/

# Executar apenas testes rápidos (sem integração)
pytest -m "not integration"

# Executar apenas testes de integração
pytest -m integration

# Gerar relatório HTML de cobertura
pytest --cov=src --cov=api --cov=telegram_bot --cov-report=html --cov-report=term

# Abrir relatório no navegador
open htmlcov/index.html      # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html     # Windows
```

**⚠️ Nota sobre Testes de Integração:**
- Testes marcados como `integration` fazem chamadas reais às APIs de LLM
- Estes testes consomem tokens da sua conta OpenAI
- Use [`make test`](Makefile:266) para ser perguntado antes de executá-los
- Use [`make test-openai-basic`](Makefile:387) para testes sem gastar tokens

### Estrutura de Testes

```
tests/
├── conftest.py                    # Fixtures compartilhadas
├── test_service_points.py         # 20 testes - Pontos de serviço (95%+)
├── test_genetic_algorithm.py      # 32 testes - Algoritmo genético (95%+)
├── test_elitism_verification.py   # 2 testes - Elitismo dinâmico (100%)
├── test_streamlit_utils.py        # 17 testes - Utilitários Streamlit (30%+)
├── test_integration.py            # 8 testes - Integração end-to-end (80%+)
├── test_restrictions.py           # 8 testes - Restrições e validações (80%+)
├── test_api.py                    # 24 testes - API REST básica (90%+)
├── test_api_advanced.py           # 22 testes - API REST avançada (90%+)
├── test_api_integration.py        # 11 testes - Integração da API (90%+)
├── test_cloud_deployment.py       # 33 testes - Cloud/Deploy (85%+)
├── test_telegram_bot.py           # 32 testes - Bot do Telegram (75%+)
└── test_llm/                      # 55 testes - Integração LLM (70%+)
    ├── test_providers.py          # 2 testes - Factory e base
    ├── test_openai_provider.py    # 16 testes - OpenAI
    ├── test_ollama_provider.py    # 17 testes - Ollama
    ├── test_generators.py         # 3 testes - Geradores
    └── test_llm_integration.py    # 17 testes - Integração completa
```

**Total: 264 testes em 17 arquivos**

### Cobertura de Testes por Módulo

| Módulo | Cobertura | Testes | Arquivos de Teste | Status |
|:-------|:---------:|:------:|:------------------|:------:|
| **🧬 Core - Algoritmo Genético** | `95%+` | 32 | [`test_genetic_algorithm.py`](tests/test_genetic_algorithm.py) | 🟢 Excelente |
| **📍 Core - Service Points** | `95%+` | 20 | [`test_service_points.py`](tests/test_service_points.py) | 🟢 Excelente |
| **🚗 Core - Multi-Vehicle** | `0%` | 0 | ⚠️ Pendente | 🔴 Crítico |
| **🌐 API REST** | `90%+` | 57 | [`test_api.py`](tests/test_api.py), [`test_api_advanced.py`](tests/test_api_advanced.py), [`test_api_integration.py`](tests/test_api_integration.py) | 🟢 Excelente |
| **☁️ Cloud/Deployment** | `85%+` | 33 | [`test_cloud_deployment.py`](tests/test_cloud_deployment.py) | 🟢 Muito Bom |
| **💬 Telegram Bot** | `75%+` | 32 | [`test_telegram_bot.py`](tests/test_telegram_bot.py) | 🟢 Muito Bom |
| **🤖 LLM Integration** | `70%+` | 55 | [`test_llm/*`](tests/test_llm/) (5 arquivos) | 🟢 Bom |
| **🔗 Integração E2E** | `80%+` | 16 | [`test_integration.py`](tests/test_integration.py), [`test_restrictions.py`](tests/test_restrictions.py) | 🟢 Muito Bom |
| **🎨 Visualization** | `5%` | 0 | ⚠️ Limitado | 🟠 Baixo |
| **📊 Streamlit** | `30%+` | 17 | [`test_streamlit_utils.py`](tests/test_streamlit_utils.py) | 🟡 Razoável |
| **⚡ Elitismo Dinâmico** | `100%` | 2 | [`test_elitism_verification.py`](tests/test_elitism_verification.py) | 🟢 Excelente |

### Estatísticas de Testes

- **Total de Testes:** 264
- **Total de Arquivos de Teste:** 16
- **Total de Classes de Teste:** 73+
- **Cobertura Geral:** ~55%
- **Cobertura de Módulos Críticos:** ~75%

## 📚 Documentação

### Documentos Disponíveis

- [README.md](README.md) - Este arquivo
- [ARQUITETURA_GCP.md](docs/ARQUITETURA_GCP.md) - **Arquitetura completa da solução em Google Cloud Platform**
- [README_LLM.md](docs/README_LLM.md) - Integração com LLMs
- [README_RESTRICOES.md](docs/README_RESTRICOES.md) - Restrições do algoritmo
- [README_STREAMLIT.md](docs/README_STREAMLIT.md) - Dashboard Streamlit
- [README_TESTS.md](docs/README_TESTS.md) - Guia de testes

### API Documentation

A documentação completa da API está disponível em:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`


## 📄 Licença

Este projeto está licenciado sob a **Licença MIT** - uma licença de software livre permissiva que permite uso comercial, modificação, distribuição e uso privado, com a única exigência de manter o aviso de copyright e a licença em todas as cópias ou partes substanciais do software.

**Em resumo, a Licença MIT permite:**
- ✅ Uso comercial
- ✅ Modificação do código
- ✅ Distribuição
- ✅ Uso privado

**Requisitos:**
- Incluir o aviso de copyright original
- Incluir a licença MIT

Consulte o arquivo [`LICENSE`](LICENSE) para o texto completo da licença.

## 👥 Autores

- **Fernanda Valdevino** - [GitHub](https://github.com/fernandavaldevino)
- **Marcos Câmara** - [GitHub](https://github.com/marcosvrc)

## 🎓 Projeto Acadêmico

Este projeto foi desenvolvido como parte do curso de Pós-Tech da FIAP.

### Objetivos do Projeto

- ✅ Implementar algoritmo genético para otimização de rotas
- ✅ Integrar com LLMs para geração de relatórios
- ✅ Criar API REST escalável
- ✅ Deploy em cloud (Google Cloud Platform)
- ✅ Implementar testes automatizados
- ✅ Documentação completa
- ✅ Interface conversacional (Telegram Bot)
- ✅ Dashboard interativo (Streamlit)

## 🔗 Links Úteis

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Cloud Run](https://cloud.google.com/run/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [Ollama](https://ollama.ai/)
- [python-telegram-bot](https://python-telegram-bot.org/)

## 📊 Status do Projeto

- ✅ **Algoritmo Genético**: Completo e testado
- ✅ **API REST**: Funcional e documentada
- ✅ **Deploy GCP**: Funcionando em produção
- ✅ **Terraform IaC**: Implementado
- ✅ **Telegram Bot**: Funcional
- ✅ **Streamlit Dashboard**: Funcional
- ✅ **Integração LLM**: OpenAI e Ollama
- ✅ **Testes**: Cobertura > 85%
- ✅ **Documentação**: Completa


## 📧 Contato

Para dúvidas, sugestões ou feedback:

- **📧 Email**: fernandavaldevino.gcp@gmail.com
- **🐛 GitHub Issues**: [Criar Issue](https://github.com/seu-usuario/genetic_route_optimizer/issues)

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!

**Desenvolvido com ❤️ e ☕️ usando Python, FastAPI e Google Cloud Platform**

# 🚗 Sistema de Otimização de Rotas com Algoritmo Genético

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Run-orange.svg)](https://cloud.google.com/run)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-purple.svg)](https://www.terraform.io/)
[![Tests](https://img.shields.io/badge/Tests-140+-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-55%25-yellow.svg)](docs/COVERAGE_REPORT.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema inteligente de otimização de rotas para múltiplos veículos utilizando Algoritmo Genético, com integração de LLM (Large Language Models) para geração de relatórios e análises. Desenvolvido como projeto da Pós-Tech FIAP.

## 📋 Índice

- [Características](#-características)
- [Arquitetura](#-arquitetura)
- [Tecnologias](#-tecnologias)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Deploy no GCP](#-deploy-no-gcp)
- [API](#-api)
- [Telegram Bot](#-telegram-bot)
- [Testes](#-testes)
- [Documentação](#-documentação)
- [Troubleshooting](#-troubleshooting)
- [Contribuindo](#-contribuindo)

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

- ✅ **Deploy em Cloud**:
  - Google Cloud Run (serverless)
  - Google Artifact Registry para imagens Docker
  - Terraform para infraestrutura como código (IaC)
  - Google Cloud Build para CI/CD
  - Configuração de variáveis de ambiente
  - Escalabilidade automática

### 🧪 Testes e Qualidade

Documentação completa: [`README_TESTS.md`](docs/README_TESTS.md)

- ✅ **Cobertura de Testes Abrangente**:
  - **140+ testes automatizados**
  - **Cobertura geral: ~55%**
  - **Cobertura de módulos críticos: ~75%**

- ✅ **Testes por Módulo**:
  - **Core - Algoritmo Genético**: 95%+ cobertura
  - **Core - Service Points**: 95%+ cobertura
  - **API REST**: 90%+ cobertura
  - **Cloud/Deployment**: 85%+ cobertura
  - **LLM Integration**: 70%+ cobertura
  - **Telegram Bot**: 60%+ cobertura

- ✅ **Tipos de Testes**:
  - Testes unitários (64 testes)
  - Testes de integração (18 testes)
  - Testes de API avançados (21 testes)
  - Testes de deployment (38 testes)
  - Testes de LLM (múltiplos provedores)

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

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Docker (opcional, para containerização)
- Google Cloud SDK (para deploy no GCP)
- Terraform (para IaC)

### Instalação Local

```bash
# 1. Clonar o repositório
git clone https://github.com/seu-usuario/genetic_route_optimizer.git
cd genetic_route_optimizer

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais
```

### Configuração do `.env`

```bash
# OpenAI (opcional)
OPENAI_API_KEY=sk-...

# Telegram Bot (opcional)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_WEBHOOK_URL=https://seu-dominio.com/webhook

# Google Cloud (para deploy)
GOOGLE_CLOUD_PROJECT=seu-projeto-gcp
GOOGLE_APPLICATION_CREDENTIALS=./key.json
```

## 🚀 Uso

### 1. API Local

```bash
# Iniciar servidor de desenvolvimento
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Acessar documentação interativa
# http://localhost:8000/docs
```

### 2. Streamlit Dashboard

```bash
# Iniciar dashboard
streamlit run streamlit/app_streamlit.py

# Acessar em http://localhost:8501
```

### 3. Telegram Bot

```bash
# Iniciar bot (polling mode)
python telegram_bot/bot.py

# Ou configurar webhook (produção)
python scripts/setup_telegram_webhook.py
```

### 4. Visualização Pygame

```bash
# Executar otimização com visualização
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

## ☁️ Deploy no GCP

### Pré-requisitos

1. Conta Google Cloud Platform
2. Projeto GCP criado
3. Google Cloud SDK instalado
4. Terraform instalado

### Deploy Rápido

```bash
# 1. Autenticar no GCP
gcloud auth login
gcloud config set project project-1804e3ce-8509-46cd-b62

# 2. Habilitar APIs necessárias
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 3. Criar Artifact Registry
gcloud artifacts repositories create gro-repository \
  --repository-format=docker \
  --location=us-central1 \
  --description="Genetic Route Optimizer Repository"

# 4. Construir imagem com Cloud Build
gcloud builds submit --config cloudbuild.yaml

# 5. Obter digest da imagem
gcloud artifacts docker images describe \
  us-central1-docker.pkg.dev/project-1804e3ce-8509-46cd-b62/gro-repository/genetic-route-optimizer-api:latest

# 6. Atualizar terraform/terraform.tfvars com o digest SHA256

# 7. Deploy com Terraform
cd terraform
terraform init
terraform plan
terraform apply -auto-approve

# 8. Obter URL da API
terraform output api_url
```

### URL da API em Produção

```
https://genetic-route-optimizer-api-wzfyhoxurq-uc.a.run.app
```

### Endpoints Disponíveis

- `GET /` - Informações da API
- `GET /health` - Health check
- `GET /docs` - Documentação Swagger
- `POST /optimize` - Otimizar rota (em desenvolvimento)


## 📡 API

### Documentação Interativa

Acesse a documentação Swagger em:
- **Local**: http://localhost:8000/docs
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

- `/start` - Iniciar bot
- `/help` - Ajuda
- `/optimize` - Otimizar rota
- `/status` - Status do sistema

### Exemplo de Uso

```
Usuário: /optimize
Bot: Envie os pontos de serviço no formato:
     x1,y1,demanda1,prioridade1
     x2,y2,demanda2,prioridade2

Usuário: 10,20,5,2
         30,40,3,1
         
Bot: ✅ Rota otimizada!
     Distância total: 45.23 km
     Tempo estimado: 1h 23min
     [Mapa da rota]
```

## 🧪 Testes

### Executar Todos os Testes

```bash
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
```

### Estrutura de Testes

```
tests/
├── conftest.py                    # Fixtures compartilhadas
├── test_genetic_algorithm.py      # Testes do algoritmo genético (95%+)
├── test_service_points.py         # Testes de pontos de serviço (95%+)
├── test_api.py                    # Testes da API REST (90%+)
├── test_api_advanced.py           # Testes avançados da API (NOVO)
├── test_api_integration.py        # Testes de integração da API
├── test_cloud_deployment.py       # Testes de Cloud/Deploy (NOVO)
├── test_integration.py            # Testes de integração end-to-end
├── test_restrictions.py           # Testes de restrições
├── test_telegram_bot.py           # Testes do bot do Telegram
├── test_streamlit_utils.py        # Testes de utilitários Streamlit
└── test_llm/                      # Testes de integração LLM
    ├── test_providers.py          # Testes de provedores (OpenAI, Ollama)
    ├── test_generators.py         # Testes de geradores
    ├── test_llm_integration.py    # Testes de integração LLM
    ├── test_openai_provider.py    # Testes específicos OpenAI
    └── test_ollama_provider.py    # Testes específicos Ollama
```

### Cobertura de Testes por Módulo

| Módulo | Cobertura | Arquivos de Teste | Status |
|--------|-----------|-------------------|--------|
| **Core - Algoritmo Genético** | 95%+ | `test_genetic_algorithm.py` | ✅ Excelente |
| **Core - Service Points** | 95%+ | `test_service_points.py` | ✅ Excelente |
| **Core - Multi-Vehicle** | 0% | ⚠️ Pendente | ❌ Crítico |
| **API REST** | 90%+ | `test_api.py`, `test_api_advanced.py` | ✅ Excelente |
| **Cloud/Deployment** | 85%+ | `test_cloud_deployment.py` | ✅ Muito Bom |
| **Telegram Bot** | 60%+ | `test_telegram_bot.py` | ⚠️ Bom |
| **LLM Integration** | 70%+ | `test_llm/*` | ✅ Bom |
| **Visualization** | 5% | ⚠️ Limitado | ⚠️ Baixo |
| **Streamlit** | 20% | `test_streamlit_utils.py` | ⚠️ Baixo |

### Estatísticas de Testes

- **Total de Arquivos de Teste:** 15+
- **Total de Classes de Teste:** 70+
- **Cobertura Geral Estimada:** ~55%
- **Cobertura de Módulos Críticos:** ~75%

### Novos Testes Adicionados (2026-03-18)

#### 1. **test_cloud_deployment.py** (NOVO)
Testes completos para infraestrutura e deployment:
- ✅ Configuração do Cloud Build (cloudbuild.yaml)
- ✅ Configuração do Terraform (main.tf, variables.tf, outputs.tf)
- ✅ Dockerfile e configuração Docker
- ✅ Variáveis de ambiente (.env.example)
- ✅ Documentação de deployment GCP
- ✅ Makefile e targets
- ✅ Cloud Run deployment
- ✅ Integração Cloud Build

**Classes de Teste:**
- `TestCloudBuildConfiguration` (7 testes)
- `TestTerraformConfiguration` (9 testes)
- `TestDockerConfiguration` (7 testes)
- `TestEnvironmentConfiguration` (3 testes)
- `TestGCPDeploymentDocumentation` (3 testes)
- `TestMakefile` (2 testes)
- `TestCloudRunDeployment` (5 testes)
- `TestCloudBuildIntegration` (2 testes)

#### 2. **test_api_advanced.py** (NOVO)
Testes avançados para funcionalidades específicas da API:
- ✅ Webhook do Telegram (recebimento, validação, erros)
- ✅ Inicialização do bot do Telegram
- ✅ Integração de rotas (conversão, salvamento)
- ✅ Metadados da API (título, versão, tags)
- ✅ Otimização com diferentes parâmetros (2 veículos, depot customizado)
- ✅ Validação de tipos de serviço (todos os tipos)
- ✅ Validação de janelas de tempo
- ✅ Estrutura de resposta (execution_time, vehicles array)
- ✅ Tratador global de exceções
- ✅ Middleware CORS

**Classes de Teste:**
- `TestTelegramWebhook` (4 testes)
- `TestTelegramBotInitialization` (2 testes)
- `TestRouteIntegration` (1 teste)
- `TestAPIMetadata` (2 testes)
- `TestOptimizationWithDifferentParameters` (4 testes)
- `TestServiceTypeValidation` (1 teste)
- `TestTimeWindowValidation` (2 testes)
- `TestResponseStructure` (2 testes)
- `TestGlobalExceptionHandler` (1 teste)
- `TestCORSMiddleware` (2 testes)


### Executar Testes com Relatório de Cobertura

```bash
# Gerar relatório HTML de cobertura
pytest --cov=src --cov=api --cov=telegram_bot --cov-report=html --cov-report=term

# Abrir relatório no navegador
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## 📚 Documentação

### Documentos Disponíveis

- [README.md](README.md) - Este arquivo
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

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- **Fernanda Valdevino** - *Desenvolvimento Inicial* - [GitHub](https://github.com/fernandavaldevino)

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


## 📞 Contato

Para dúvidas, sugestões ou feedback:

- **Email**: fernandavaldevino.gcp@gmail.com
- **GitHub Issues**: [Criar Issue](https://github.com/seu-usuario/genetic_route_optimizer/issues)

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!

**Desenvolvido com ❤️ usando Python, FastAPI e Google Cloud**

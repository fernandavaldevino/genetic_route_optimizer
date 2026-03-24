# Testes do Projeto - Otimizador de Rotas

## 📑 Índice

- [Visão Geral](#visão-geral)
- [📁 Estrutura dos Testes](#-estrutura-dos-testes)
- [🧪 Módulos de Teste](#-módulos-de-teste)
  - [1. conftest.py](#1-conftestpy)
  - [2. test_service_points.py](#2-test_service_pointspy)
  - [3. test_genetic_algorithm.py](#3-test_genetic_algorithmpy)
  - [4. test_streamlit_utils.py](#4-test_streamlit_utilspy)
  - [5. test_integration.py](#5-test_integrationpy)
  - [6. test_api.py](#6-test_apipy)
  - [7. test_telegram_bot.py](#7-test_telegram_botpy)
  - [8. test_cloud_deployment.py](#8-test_cloud_deploymentpy)
  - [9. test_llm/](#9-test_llm)
- [🚀 Como Executar os Testes](#-como-executar-os-testes)
  - [Comandos do Makefile (Recomendado)](#comandos-do-makefile-recomendado)
  - [Execução Manual com Pytest](#execução-manual-com-pytest)
  - [Executar Testes Específicos](#executar-testes-específicos)
  - [Executar com Marcadores](#executar-com-marcadores)
- [📊 Cobertura de Testes](#-cobertura-de-testes)
  - [Estatísticas Gerais](#estatísticas-gerais)
  - [Cobertura por Módulo](#cobertura-por-módulo)
  - [Testes por Categoria](#testes-por-categoria)
- [🔧 Configuração do pytest](#-configuração-do-pytest)
- [📝 Convenções de Nomenclatura](#-convenções-de-nomenclatura)
- [🐛 Debugging](#-debugging)
- [📈 Relatórios](#-relatórios)
- [🔄 Integração Contínua](#-integração-contínua)
- [📚 Recursos Adicionais](#-recursos-adicionais)

---

## Visão Geral

Este diretório contém os **263 testes automatizados** do projeto, organizados de forma modular usando pytest. A cobertura geral é de **~55%**, com módulos críticos atingindo **~75%** de cobertura.

**📖 Para informações resumidas sobre testes, consulte a seção [Execução de Testes](../README.md#-execução-de-testes) no README principal.**

## 📁 Estrutura dos Testes

```
tests/
├── conftest.py                    # Configuração e fixtures compartilhadas
├── test_service_points.py         # Testes unitários para pontos de serviço
├── test_genetic_algorithm.py      # Testes para algoritmo genético (unitários + edge cases)
├── test_streamlit_utils.py        # Testes para utilitários do Streamlit
├── test_integration.py            # Testes de integração end-to-end
├── test_restrictions.py           # Testes de integração legados
├── test_api.py                    # Testes da API REST
├── test_api_advanced.py           # Testes avançados da API
├── test_api_integration.py        # Testes de integração da API
├── test_cloud_deployment.py       # Testes de Cloud/Deploy
├── test_telegram_bot.py           # Testes do bot do Telegram
└── test_llm/                      # Testes de integração LLM
    ├── test_providers.py          # Testes de provedores (OpenAI, Ollama)
    ├── test_generators.py         # Testes de geradores
    ├── test_llm_integration.py    # Testes de integração LLM
    ├── test_openai_provider.py    # Testes específicos OpenAI
    └── test_ollama_provider.py    # Testes específicos Ollama
```

## 🧪 Módulos de Teste

### 1. `conftest.py`
Arquivo de configuração do pytest com fixtures compartilhadas:
- `sample_service_points`: Pontos de serviço de exemplo
- `depot_point`: Ponto de depósito
- `medication_route`: Rota com medicamentos
- `priority_ordered_route`: Rota ordenada por prioridade
- `priority_reversed_route`: Rota com prioridades invertidas

### 2. `test_service_points.py`
Testa o módulo [`src/core/service_points.py`](../src/core/service_points.py):
- **TestServicePointCreation**: Criação de pontos de diferentes tipos
- **TestPriorityOrdering**: Ordenação por prioridade
- **TestTimeWindows**: Validação de janelas de tempo
- **TestTemperatureControl**: Controle de temperatura para medicamentos
- **TestDistanceCalculation**: Cálculo de distâncias euclidianas

### 3. `test_genetic_algorithm.py`
Testa o módulo [`src/core/genetic_algorithm.py`](../src/core/genetic_algorithm.py):
- **TestFitnessCalculation**: Cálculo de fitness com restrições
- **TestPopulationGeneration**: Geração de população com viés de prioridade
- **TestPopulationSorting**: Ordenação de população por fitness
- **TestGeneticOperators**: Crossover e mutação
- **TestRouteCalculations**: Cálculos de tempo e distância de rotas

### 4. `test_streamlit_utils.py`
Testa funções utilitárias do [`streamlit/app_streamlit.py`](../streamlit/app_streamlit.py):
- **TestTimeFormatting**: Formatação de minutos para HH:MM
- **TestDayCalculation**: Cálculo de dia a partir de minutos
- **TestServicePointsCreation**: Criação aleatória de pontos de serviço

### 5. `test_integration.py`
Testes de integração end-to-end:
- **TestEndToEndOptimization**: Ciclo completo de otimização
- **TestIntegrationWithConstraints**: Integração com restrições
- **TestRobustness**: Testes de robustez e estabilidade

### 6. `test_api.py`
Testa a API REST ([`api/main.py`](../api/main.py)):
- **TestHealthEndpoint**: Health check da API
- **TestOptimizationEndpoint**: Endpoint de otimização
- **TestErrorHandling**: Tratamento de erros
- **TestValidation**: Validação de dados de entrada

### 7. `test_telegram_bot.py`
Testa o Bot do Telegram ([`telegram_bot/bot.py`](../telegram_bot/bot.py)):
- **TestBotCommands**: Comandos do bot (/start, /help, /optimize, etc.)
- **TestBotIntegration**: Integração com sistema de rotas
- **TestWebhookHandler**: Handler de webhooks

### 8. `test_cloud_deployment.py`
Testa configurações de Cloud/Deploy:
- **TestDockerfile**: Validação do Dockerfile
- **TestCloudBuild**: Configuração do Cloud Build
- **TestTerraform**: Validação de arquivos Terraform
- **TestEnvironmentVariables**: Variáveis de ambiente

### 9. `test_llm/`
Testes de integração com LLMs:
- **test_providers.py**: Testes de provedores (OpenAI, Ollama)
- **test_generators.py**: Testes de geradores de conteúdo
- **test_llm_integration.py**: Testes de integração completa
- **test_openai_provider.py**: Testes específicos OpenAI (básicos + integração)
- **test_ollama_provider.py**: Testes específicos Ollama (básicos + integração)

## 🚀 Como Executar os Testes

### Comandos do Makefile (Recomendado)

O projeto possui comandos [`make`](../Makefile) preparados para facilitar a execução de testes:

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

**⚠️ Nota sobre Testes de Integração:**
- Testes marcados como `integration` fazem chamadas reais às APIs de LLM
- Estes testes consomem tokens da sua conta OpenAI
- Use [`make test`](../Makefile:266) para ser perguntado antes de executá-los
- Use [`make test-openai-basic`](../Makefile:387) para testes sem gastar tokens

### Execução Manual com Pytest

Se preferir executar os testes diretamente com [`pytest`](../pytest.ini):

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

### Executar Testes Específicos
```bash
# Apenas testes de service_points
pytest tests/test_service_points.py

# Apenas testes de algoritmo genético
pytest tests/test_genetic_algorithm.py

# Apenas testes de utilitários Streamlit
pytest tests/test_streamlit_utils.py

# Executar uma classe específica
pytest tests/test_service_points.py::TestPriorityOrdering

# Executar um teste específico
pytest tests/test_service_points.py::TestPriorityOrdering::test_sort_by_priority_correct_order
```

### Executar com Marcadores
```bash
# Executar apenas testes rápidos (se marcados)
pytest tests/ -m "not slow"

# Executar com saída de print
pytest tests/ -s
```

## 📊 Cobertura de Testes

### Estatísticas Gerais

- **Total de Testes:** 263
- **Total de Arquivos de Teste:** 15+
- **Total de Classes de Teste:** 70+
- **Cobertura Geral:** ~55%
- **Cobertura de Módulos Críticos:** ~75%

### Cobertura por Módulo

| Módulo | Cobertura | Arquivos de Teste | Status |
|:-------|:---------:|:------------------|:------:|
| **🧬 Core - Algoritmo Genético** | `95%+` | [`test_genetic_algorithm.py`](../tests/test_genetic_algorithm.py) | 🟢 Excelente |
| **📍 Core - Service Points** | `95%+` | [`test_service_points.py`](../tests/test_service_points.py) | 🟢 Excelente |
| **🚗 Core - Multi-Vehicle** | `0%` | ⚠️ Pendente | 🔴 Crítico |
| **🌐 API REST** | `90%+` | [`test_api.py`](../tests/test_api.py), [`test_api_advanced.py`](../tests/test_api_advanced.py) | 🟢 Excelente |
| **☁️ Cloud/Deployment** | `85%+` | [`test_cloud_deployment.py`](../tests/test_cloud_deployment.py) | 🟢 Muito Bom |
| **💬 Telegram Bot** | `60%+` | [`test_telegram_bot.py`](../tests/test_telegram_bot.py) | 🟡 Bom |
| **🤖 LLM Integration** | `70%+` | [`test_llm/*`](../tests/test_llm/) | 🟢 Bom |
| **🎨 Visualization** | `5%` | ⚠️ Limitado | 🟠 Baixo |
| **📊 Streamlit** | `20%` | [`test_streamlit_utils.py`](../tests/test_streamlit_utils.py) | 🟠 Baixo |

### Testes por Categoria

#### Testes Unitários (64 testes)
- ✅ **Pontos de Serviço** (25 testes): Criação, validação, ordenação por prioridade
- ✅ **Janelas de Tempo** (4 testes): Validação e penalidades
- ✅ **Controle de Temperatura** (3 testes): Validação de rotas com medicamentos
- ✅ **Cálculo de Distância** (5 testes): Distâncias euclidianas
- ✅ **Algoritmo Genético** (27 testes):
  - Cálculo de fitness com restrições (8 testes + edge cases)
  - Geração de população com viés (4 testes + edge cases)
  - Operadores genéticos: crossover e mutação (10 testes + edge cases)
  - Cálculos de tempo e distância (5 testes + edge cases)

#### Testes de Interface (13 testes)
- ✅ **Streamlit Utils**: Formatação de tempo, cálculo de dias, criação de pontos

#### Testes de Integração (18 testes)
- ✅ **End-to-End** (2 testes): Ciclo completo de otimização, evolução multi-geracional
- ✅ **Restrições** (3 testes): Prioridade, temperatura, janelas de tempo
- ✅ **Robustez** (3 testes): População grande, muitas gerações, distâncias extremas
- ✅ **Legados** (10 testes): Testes de integração do sistema original

#### Testes de API (60+ testes)
- ✅ **API Básica** (20+ testes): Endpoints, validação, health checks
- ✅ **API Avançada** (21 testes): Casos complexos, edge cases
- ✅ **API Integração** (19+ testes): Integração com algoritmo genético

#### Testes de Cloud/Deploy (38 testes)
- ✅ **Dockerfile**: Validação de configuração
- ✅ **Cloud Build**: Configuração de CI/CD
- ✅ **Terraform**: Infraestrutura como código
- ✅ **Variáveis de Ambiente**: Configurações

#### Testes de LLM (70+ testes)
- ✅ **Provedores**: OpenAI e Ollama
- ✅ **Geradores**: Manual, Roteiro, Q&A
- ✅ **Integração**: Testes end-to-end com LLMs

## 🔧 Configuração do pytest

Você pode criar um arquivo `pytest.ini` na raiz do projeto para configurações adicionais:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

## 📝 Convenções de Nomenclatura

- **Arquivos**: `test_<modulo>.py`
- **Classes**: `Test<Funcionalidade>`
- **Métodos**: `test_<comportamento_esperado>`

## 🐛 Debugging

Para debugar um teste específico:
```bash
# Com pdb (Python debugger)
pytest tests/test_service_points.py::test_name --pdb

# Parar no primeiro erro
pytest tests/ -x

# Mostrar variáveis locais em falhas
pytest tests/ -l
```

## 📈 Relatórios

### Gerar Relatório HTML de Cobertura
```bash
pytest tests/ --cov=src --cov-report=html
# Abrir htmlcov/index.html no navegador
```

### Gerar Relatório XML (para CI/CD)
```bash
pytest tests/ --cov=src --cov-report=xml --junitxml=junit.xml
```

## 🔄 Integração Contínua

Os testes podem ser integrados em pipelines de CI/CD (GitHub Actions, GitLab CI, etc.):

```yaml
# Exemplo para GitHub Actions
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest tests/ --cov=src --cov-report=xml
```

## 📚 Recursos Adicionais

- [Documentação do pytest](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Boas práticas de testes](https://docs.pytest.org/en/stable/goodpractices.html)

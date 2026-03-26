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

Este diretório contém os **264 testes automatizados** do projeto, organizados de forma modular usando pytest. A cobertura geral é de **~55%**, com módulos críticos atingindo **~75%** de cobertura.

**📖 Para informações resumidas sobre testes, consulte a seção [Execução de Testes](../README.md#-execução-de-testes) no README principal.**

## 📁 Estrutura dos Testes

```
tests/
├── conftest.py                    # Configuração e fixtures compartilhadas
├── test_service_points.py         # 20 testes - Pontos de serviço
├── test_genetic_algorithm.py      # 32 testes - Algoritmo genético
├── test_elitism_verification.py   # 2 testes - Elitismo dinâmico (1V e 2V)
├── test_streamlit_utils.py        # 17 testes - Utilitários do Streamlit
├── test_integration.py            # 8 testes - Integração end-to-end
├── test_restrictions.py           # 8 testes - Restrições e validações
├── test_api.py                    # 24 testes - API REST básica
├── test_api_advanced.py           # 22 testes - API REST avançada
├── test_api_integration.py        # 11 testes - Integração da API
├── test_cloud_deployment.py       # 33 testes - Cloud/Deploy
├── test_telegram_bot.py           # 32 testes - Bot do Telegram
└── test_llm/                      # 55 testes - Integração LLM
    ├── test_providers.py          # 2 testes - Factory e base
    ├── test_openai_provider.py    # 16 testes - OpenAI (básicos + integração)
    ├── test_ollama_provider.py    # 17 testes - Ollama (básicos + integração)
    ├── test_generators.py         # 3 testes - Geradores de conteúdo
    ├── test_llm_integration.py    # 17 testes - Integração completa
    └── llm_integration_example.py # Exemplo de uso (não é teste)
```

**Total: 264 testes em 17 arquivos**

## 🧪 Módulos de Teste

### 1. `conftest.py`
Arquivo de configuração do pytest com fixtures compartilhadas:
- `sample_service_points`: Pontos de serviço de exemplo
- `depot_point`: Ponto de depósito
- `medication_route`: Rota com medicamentos
- `priority_ordered_route`: Rota ordenada por prioridade
- `priority_reversed_route`: Rota com prioridades invertidas

### 2. `test_service_points.py` (20 testes)
Testa o módulo [`src/core/service_points.py`](../src/core/service_points.py):
- **TestServicePointCreation**: Criação de pontos de diferentes tipos
- **TestPriorityOrdering**: Ordenação por prioridade
- **TestTimeWindows**: Validação de janelas de tempo
- **TestTemperatureControl**: Controle de temperatura para medicamentos
- **TestDistanceCalculation**: Cálculo de distâncias euclidianas

### 3. `test_genetic_algorithm.py` (32 testes)
Testa o módulo [`src/core/genetic_algorithm.py`](../src/core/genetic_algorithm.py):
- **TestFitnessCalculation**: Cálculo de fitness com restrições
- **TestPopulationGeneration**: Geração de população com viés de prioridade
- **TestPopulationSorting**: Ordenação de população por fitness
- **TestGeneticOperators**: Crossover e mutação
- **TestRouteCalculations**: Cálculos de tempo e distância de rotas

### 4. `test_elitism_verification.py` (2 testes)
Testa a implementação do elitismo dinâmico para 1 e 2 veículos:
- **test_elitism_1v**: Verifica elitismo dinâmico para 1 veículo
  - Elite size cresce de 1 para 2 indivíduos (50% das gerações)
  - Validação de progresso e tamanho da elite
- **test_elitism_2v**: Verifica elitismo dinâmico para 2 veículos
  - Elite size cresce de 5 para 10 indivíduos (linearmente)
  - Validação em diferentes estágios (início, meio, fim)
- **Execução**: Pode ser executado diretamente com `python tests/test_elitism_verification.py`

### 5. `test_streamlit_utils.py` (17 testes)
Testa funções utilitárias do [`streamlit/app_streamlit.py`](../streamlit/app_streamlit.py):
- **TestTimeFormatting**: Formatação de minutos para HH:MM
- **TestDayCalculation**: Cálculo de dia a partir de minutos
- **TestServicePointsCreation**: Criação aleatória de pontos de serviço

### 6. `test_integration.py` (8 testes)
Testes de integração end-to-end:
- **TestEndToEndOptimization**: Ciclo completo de otimização
- **TestIntegrationWithConstraints**: Integração com restrições
- **TestRobustness**: Testes de robustez e estabilidade

### 7. `test_restrictions.py` (8 testes)
Testes de restrições e validações:
- **TestPriorityRestrictions**: Validação de prioridades
- **TestTimeWindowRestrictions**: Validação de janelas de tempo
- **TestTemperatureRestrictions**: Validação de controle de temperatura

### 8. `test_api.py` (24 testes)
Testa a API REST ([`api/main.py`](../api/main.py)):
- **TestHealthEndpoint**: Health check da API
- **TestOptimizationEndpoint**: Endpoint de otimização
- **TestErrorHandling**: Tratamento de erros
- **TestValidation**: Validação de dados de entrada

### 9. `test_api_advanced.py` (22 testes)
Testes avançados da API REST:
- **TestAdvancedScenarios**: Cenários complexos
- **TestEdgeCases**: Casos extremos
- **TestPerformance**: Testes de performance

### 10. `test_api_integration.py` (11 testes)
Testes de integração da API:
- **TestAPIIntegration**: Integração completa com algoritmo genético
- **TestMultiVehicleAPI**: Testes com múltiplos veículos

### 11. `test_telegram_bot.py` (32 testes)
Testa o Bot do Telegram ([`telegram_bot/bot.py`](../telegram_bot/bot.py)):
- **TestRouteDataIntegration** (15 testes): Integração de dados de rota
- **TestTelegramBotCommands** (15 testes): Comandos do bot
- **TestRouteDataValidation** (2 testes): Validação de dados

### 12. `test_cloud_deployment.py` (33 testes)
Testa configurações de Cloud/Deploy:
- **TestDockerfile**: Validação do Dockerfile
- **TestCloudBuild**: Configuração do Cloud Build
- **TestTerraform**: Validação de arquivos Terraform
- **TestEnvironmentVariables**: Variáveis de ambiente

### 13. `test_llm/` (55 testes em 5 arquivos)
Testes de integração com LLMs:
- **test_providers.py** (2 testes): Testes de factory e base
- **test_openai_provider.py** (16 testes): Testes OpenAI (básicos + integração)
- **test_ollama_provider.py** (17 testes): Testes Ollama (básicos + integração)
- **test_generators.py** (3 testes): Testes de geradores de conteúdo
- **test_llm_integration.py** (17 testes): Testes de integração completa

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

- **Total de Testes:** 264
- **Total de Arquivos de Teste:** 16
- **Total de Classes de Teste:** 73+
- **Cobertura Geral:** ~55%
- **Cobertura de Módulos Críticos:** ~75%

### Cobertura por Módulo

| Módulo | Cobertura | Testes | Arquivos de Teste | Status |
|:-------|:---------:|:------:|:------------------|:------:|
| **🧬 Core - Algoritmo Genético** | `95%+` | 32 | [`test_genetic_algorithm.py`](../tests/test_genetic_algorithm.py) | 🟢 Excelente |
| **📍 Core - Service Points** | `95%+` | 20 | [`test_service_points.py`](../tests/test_service_points.py) | 🟢 Excelente |
| **🚗 Core - Multi-Vehicle** | `0%` | 0 | ⚠️ Pendente | 🔴 Crítico |
| **🌐 API REST** | `90%+` | 57 | [`test_api.py`](../tests/test_api.py), [`test_api_advanced.py`](../tests/test_api_advanced.py), [`test_api_integration.py`](../tests/test_api_integration.py) | 🟢 Excelente |
| **☁️ Cloud/Deployment** | `85%+` | 33 | [`test_cloud_deployment.py`](../tests/test_cloud_deployment.py) | 🟢 Muito Bom |
| **💬 Telegram Bot** | `75%+` | 32 | [`test_telegram_bot.py`](../tests/test_telegram_bot.py) | 🟢 Muito Bom |
| **🤖 LLM Integration** | `70%+` | 55 | [`test_llm/*`](../tests/test_llm/) (5 arquivos) | 🟢 Bom |
| **🔗 Integração E2E** | `80%+` | 16 | [`test_integration.py`](../tests/test_integration.py), [`test_restrictions.py`](../tests/test_restrictions.py) | 🟢 Muito Bom |
| **🎨 Visualization** | `5%` | 0 | ⚠️ Limitado | 🟠 Baixo |
| **📊 Streamlit** | `30%+` | 17 | [`test_streamlit_utils.py`](../tests/test_streamlit_utils.py) | 🟡 Razoável |
| **⚡ Elitismo Dinâmico** | `100%` | 2 | [`test_elitism_verification.py`](../tests/test_elitism_verification.py) | 🟢 Excelente |

### Testes por Categoria

#### Testes Unitários (54 testes)
- ✅ **Pontos de Serviço** (20 testes): Criação, validação, ordenação por prioridade
- ✅ **Algoritmo Genético** (32 testes):
  - Cálculo de fitness com restrições
  - Geração de população com viés de prioridade
  - Operadores genéticos: crossover e mutação
  - Cálculos de tempo e distância de rotas
  - Edge cases e validações
- ✅ **Elitismo Dinâmico** (2 testes):
  - Verificação de elitismo para 1 veículo
  - Verificação de elitismo para 2 veículos

#### Testes de Interface (17 testes)
- ✅ **Streamlit Utils** (17 testes): Formatação de tempo, cálculo de dias, criação de pontos

#### Testes de Integração (16 testes)
- ✅ **End-to-End** (8 testes): Ciclo completo de otimização, evolução multi-geracional
- ✅ **Restrições** (8 testes): Prioridade, temperatura, janelas de tempo, robustez

#### Testes de API (57 testes)
- ✅ **API Básica** (24 testes): Endpoints, validação, health checks
- ✅ **API Avançada** (22 testes): Casos complexos, edge cases
- ✅ **API Integração** (11 testes): Integração com algoritmo genético

#### Testes de Cloud/Deploy (33 testes)
- ✅ **Dockerfile**: Validação de configuração
- ✅ **Cloud Build**: Configuração de CI/CD
- ✅ **Terraform**: Infraestrutura como código
- ✅ **Variáveis de Ambiente**: Configurações

#### Testes de Telegram Bot (32 testes)
- ✅ **RouteDataIntegration** (15 testes):
  - Salvamento e carregamento de rotas
  - Conversão de resultados de otimização
  - Formatação de dados para 1 e 2 veículos
  - Validação de estrutura de dados
- ✅ **Comandos do Bot** (15 testes):
  - `/start`, `/help`, `/rota`, `/paradas`
  - `/iniciar_rota`, `/proxima`, `/concluido`
  - `/concluir_rota`, `/recarregar`
  - Seleção de veículo (1 ou 2)
  - Teclados interativos (inicial e ativo)
- ✅ **Validação de Dados** (2 testes):
  - Estrutura de dados de rota
  - Mapeamento de tipos de prioridade

#### Testes de LLM (55 testes)
- ✅ **Provedores Base** (2 testes): Testes de factory e base
- ✅ **OpenAI Provider** (16 testes): Testes básicos e de integração
- ✅ **Ollama Provider** (17 testes): Testes básicos e de integração
- ✅ **Geradores** (3 testes): Manual, Roteiro, Q&A
- ✅ **Integração LLM** (17 testes): Testes end-to-end com LLMs

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

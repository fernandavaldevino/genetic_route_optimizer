# Testes do Projeto - Otimizador de Rotas

Este diretório contém os testes automatizados do projeto, organizados de forma modular usando pytest.

## 📁 Estrutura dos Testes

```
tests/
├── conftest.py                 # Configuração e fixtures compartilhadas
├── test_service_points.py      # Testes unitários para pontos de serviço
├── test_genetic_algorithm.py   # Testes para algoritmo genético (unitários + edge cases)
├── test_streamlit_utils.py     # Testes para utilitários do Streamlit
├── test_integration.py         # Testes de integração end-to-end
└── test_restrictions.py        # Testes de integração legados
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

## 🚀 Como Executar os Testes

### Pré-requisitos
```bash
# Instalar pytest (se ainda não estiver instalado)
pip install pytest pytest-cov
```

### Executar Todos os Testes
```bash
# Da raiz do projeto
pytest tests/

# Com saída detalhada
pytest tests/ -v

# Com cobertura de código
pytest tests/ --cov=src --cov-report=html
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

### Testes Unitários (64 testes)
- ✅ **Pontos de Serviço** (25 testes): Criação, validação, ordenação por prioridade
- ✅ **Janelas de Tempo** (4 testes): Validação e penalidades
- ✅ **Controle de Temperatura** (3 testes): Validação de rotas com medicamentos
- ✅ **Cálculo de Distância** (5 testes): Distâncias euclidianas
- ✅ **Algoritmo Genético** (27 testes):
  - Cálculo de fitness com restrições (8 testes + edge cases)
  - Geração de população com viés (4 testes + edge cases)
  - Operadores genéticos: crossover e mutação (10 testes + edge cases)
  - Cálculos de tempo e distância (5 testes + edge cases)

### Testes de Interface (13 testes)
- ✅ **Streamlit Utils**: Formatação de tempo, cálculo de dias, criação de pontos

### Testes de Integração (18 testes)
- ✅ **End-to-End** (2 testes): Ciclo completo de otimização, evolução multi-geracional
- ✅ **Restrições** (3 testes): Prioridade, temperatura, janelas de tempo
- ✅ **Robustez** (3 testes): População grande, muitas gerações, distâncias extremas
- ✅ **Legados** (10 testes): Testes de integração do sistema original

### Estatísticas
- **Total de Testes**: 95 testes
- **Cobertura**: ~74% em `genetic_algorithm.py`, ~80% em `service_points.py`

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

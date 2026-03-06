# Makefile para Sistema de Otimização de Rotas
# Autor: Fernanda Valdevino

# Variáveis
VENV_NAME = .ga_routes
PYTHON = python3
PIP = $(VENV_NAME)/bin/pip
PYTHON_VENV = $(VENV_NAME)/bin/python

# Cores para output
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help setup install run streamlit test test-specific test-cov test-html test-llm test-llm-basic test-llm-integration clean

# Target padrão
help:
	@echo "$(GREEN)Sistema de Otimização de Rotas - Comandos Disponíveis:$(NC)"
	@echo ""
	@echo "$(YELLOW)Início Rápido:$(NC)"
	@echo "  $(YELLOW)make setup$(NC)           - Cria ambiente + Instala dependências (RECOMENDADO)"
	@echo "  $(YELLOW)make app$(NC)             - Setup + Executa Streamlit"
	@echo ""
	@echo "$(YELLOW)Execução:$(NC)"
	@echo "  $(YELLOW)make run$(NC)             - Executa o sistema principal (Pygame)"
	@echo "  $(YELLOW)make streamlit$(NC)       - Executa interface web (Streamlit)"
	@echo ""
	@echo "$(YELLOW)Testes:$(NC)"
	@echo "  $(YELLOW)make test$(NC)            - Executa todos os testes (console)"
	@echo "  $(YELLOW)make test-specific$(NC)   - Executa teste específico (ex: FILE=test_service_points.py)"
	@echo "  $(YELLOW)make test-cov$(NC)        - Mostra cobertura de código"
	@echo "  $(YELLOW)make test-html$(NC)       - Executa testes e gera relatório HTML"
	@echo ""
	@echo "$(YELLOW)Testes LLM:$(NC)"
	@echo "  $(YELLOW)make test-openai$(NC)        - Executa todos os testes LLM (básicos + integração)"
	@echo "  $(YELLOW)make test-openai-basic$(NC)  - Executa apenas testes básicos (sem gastar tokens)"
	@echo "  $(YELLOW)make test-openai-integration$(NC) - Executa testes de integração (gasta tokens)"
	@echo ""
	@echo "$(YELLOW)Utilitários:$(NC)"
	@echo "  $(YELLOW)make clean$(NC)           - Remove ambiente virtual e cache"
	@echo "  $(YELLOW)make info$(NC)            - Mostra informações do ambiente"
	@echo ""

# Cria o ambiente virtual e instala dependências
setup:
	@echo "$(GREEN)Configurando ambiente...$(NC)"
	@if [ -d "$(VENV_NAME)" ]; then \
		echo "$(YELLOW)Ambiente '$(VENV_NAME)' já existe.$(NC)"; \
		echo "$(YELLOW)Verificando dependências...$(NC)"; \
	else \
		echo "$(GREEN)Criando ambiente virtual '$(VENV_NAME)'...$(NC)"; \
		$(PYTHON) -m venv $(VENV_NAME); \
		echo "$(GREEN)✓ Ambiente virtual criado!$(NC)"; \
	fi
	@echo "$(GREEN)Instalando/Atualizando dependências...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Setup concluído com sucesso!$(NC)"

# Alias para setup (compatibilidade)
install: setup

# Executa o sistema principal
run:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando sistema... (pode levar alguns instantes)$(NC)"
	@echo ""
	$(PYTHON_VENV) app/main.py

# Executa a interface web com Streamlit
streamlit:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Iniciando interface web Streamlit...$(NC)"
	@echo "$(YELLOW)A aplicação será aberta no navegador em http://localhost:8501$(NC)"
	@echo ""
	$(VENV_NAME)/bin/streamlit run streamlit/app_streamlit.py

# Executa todos os testes com pytest
test:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando todos os testes...$(NC)"
	@echo ""
	$(VENV_NAME)/bin/pytest tests/ -v

# Executa teste específico
test-specific:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Erro: Especifique o arquivo de teste!$(NC)"; \
		echo "$(YELLOW)Uso: make test-specific FILE=test_service_points.py$(NC)"; \
		echo "$(YELLOW)Ou:  make test-specific FILE=test_service_points.py::TestPriorityOrdering$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando teste específico: $(FILE)$(NC)"
	@echo ""
	@if echo "$(FILE)" | grep -q "^tests/"; then \
		$(VENV_NAME)/bin/pytest $(FILE) -v; \
	else \
		$(VENV_NAME)/bin/pytest tests/$(FILE) -v; \
	fi

# Mostra cobertura de código (sem executar testes)
test-cov:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f ".coverage" ]; then \
		echo "$(YELLOW)Nenhum dado de cobertura encontrado. Executando testes primeiro...$(NC)"; \
		echo ""; \
		$(VENV_NAME)/bin/pytest tests/ --cov=src --cov-report= -q; \
	fi
	@echo "$(GREEN)Relatório de Cobertura de Código:$(NC)"
	@echo ""
	@$(VENV_NAME)/bin/coverage report --include="src/*"

# Executa testes e gera relatório HTML
test-html:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando testes e gerando relatório HTML...$(NC)"
	@echo ""
	$(VENV_NAME)/bin/pytest tests/ --cov=src --cov-report=html --cov-report=term -v
	@echo ""
	@echo "$(GREEN)✓ Relatório HTML gerado em: htmlcov/index.html$(NC)"
	@echo "$(YELLOW)Abra o arquivo no navegador para visualizar a cobertura detalhada.$(NC)"

# Executa todos os testes LLM (básicos + integração)
test-openai:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando todos os testes LLM...$(NC)"
	@echo "$(RED)⚠️  ATENÇÃO: Estes testes consomem tokens da sua conta OpenAI!$(NC)"
	@echo "$(YELLOW)Certifique-se de que OPENAI_API_KEY está configurada no .env$(NC)"
	@echo ""
	@read -p "Deseja continuar? (s/N): " confirm; \
	if [ "$$confirm" = "s" ] || [ "$$confirm" = "S" ]; then \
		$(VENV_NAME)/bin/pytest tests/test_llm/ -v; \
	else \
		echo "$(YELLOW)Testes cancelados.$(NC)"; \
	fi

# Executa apenas testes básicos LLM (sem gastar tokens)
test-openai-basic:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando testes básicos LLM (sem integração)...$(NC)"
	@echo "$(GREEN)✓ Estes testes NÃO consomem tokens da API$(NC)"
	@echo ""
	$(VENV_NAME)/bin/pytest tests/test_llm/ -m "not integration" -v

# Executa apenas testes de integração LLM (gasta tokens)
test-openai-integration:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando testes de integração LLM...$(NC)"
	@echo "$(RED)⚠️  ATENÇÃO: Estes testes consomem tokens da sua conta OpenAI!$(NC)"
	@echo "$(YELLOW)Certifique-se de que OPENAI_API_KEY está configurada no .env$(NC)"
	@echo ""
	@read -p "Deseja continuar? (s/N): " confirm; \
	if [ "$$confirm" = "s" ] || [ "$$confirm" = "S" ]; then \
		$(VENV_NAME)/bin/pytest tests/test_llm/ -m integration -v; \
	else \
		echo "$(YELLOW)Testes cancelados.$(NC)"; \
	fi

# Executa tudo de uma vez
app: setup streamlit

# Limpa ambiente virtual e cache
clean:
	@echo "$(YELLOW)Removendo ambiente virtual e cache...$(NC)"
	rm -rf $(VENV_NAME)
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf src/core/__pycache__
	rm -rf src/visualization/__pycache__
	rm -rf src/utils/__pycache__
	rm -rf tests/__pycache__
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Limpeza concluída!$(NC)"

# Mostra informações do ambiente
info:
	@echo "$(GREEN)Informações do Ambiente:$(NC)"
	@echo ""
	@if [ -d "$(VENV_NAME)" ]; then \
		echo "  Status: $(GREEN)Ativo$(NC)"; \
		echo "  Python: $$($(PYTHON_VENV) --version)"; \
		echo "  Localização: $$(pwd)/$(VENV_NAME)"; \
		echo ""; \
		echo "  Pacotes instalados:"; \
		$(PIP) list; \
	else \
		echo "  Status: $(RED)Não criado$(NC)"; \
		echo "  Execute 'make setup' para criar."; \
	fi

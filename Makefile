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

.PHONY: help setup install run test clean

# Target padrão
help:
	@echo "$(GREEN)Sistema de Otimização de Rotas - Comandos Disponíveis:$(NC)"
	@echo ""
	@echo "  $(YELLOW)make setup$(NC)    - Cria ambiente virtual '.ga_routes'"
	@echo "  $(YELLOW)make install$(NC)  - Instala dependências no ambiente"
	@echo "  $(YELLOW)make run$(NC)      - Executa o sistema principal"
	@echo "  $(YELLOW)make test$(NC)     - Executa os testes"
	@echo "  $(YELLOW)make all$(NC)      - Setup + Install + Run (tudo de uma vez)"
	@echo "  $(YELLOW)make clean$(NC)    - Remove ambiente virtual e cache"
	@echo ""

# Cria o ambiente virtual
setup:
	@echo "$(GREEN)Criando ambiente virtual '$(VENV_NAME)'...$(NC)"
	@if [ -d "$(VENV_NAME)" ]; then \
		echo "$(YELLOW)Ambiente '$(VENV_NAME)' já existe. Removendo...$(NC)"; \
		rm -rf $(VENV_NAME); \
	fi
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "$(GREEN)✓ Ambiente virtual criado com sucesso!$(NC)"

# Instala as dependências
install: setup
	@echo "$(GREEN)Instalando dependências...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependências instaladas com sucesso!$(NC)"

# Executa o sistema principal
run:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make install' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando sistema... (pode levar alguns instantes)$(NC)"
	@echo ""
	$(PYTHON_VENV) main.py

# Executa os testes
test:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make install' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando testes...$(NC)"
	@echo ""
	cd tests && ../$(PYTHON_VENV) test_restrictions.py

# Executa tudo de uma vez
all: install run clean

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
		echo "  Execute 'make install' para criar."; \
	fi

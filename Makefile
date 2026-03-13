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

.PHONY: help setup install run streamlit start-bot stop-bot test test-specific test-cov test-html all-tests test-openai test-openai-basic test-openai-integration test-ollama test-ollama-basic test-ollama-integration test-llm-integration test-telegram clean

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
	@echo "$(YELLOW)Bot do Telegram:$(NC)"
	@echo "  $(YELLOW)make start-bot$(NC)       - Inicia o bot do Telegram"
	@echo "  $(YELLOW)make stop-bot$(NC)        - Para o bot do Telegram"
	@echo ""
	@echo "$(YELLOW)Testes:$(NC)"
	@echo "  $(YELLOW)make test$(NC)            - Executa testes (pergunta se inclui testes pagos)"
	@echo "  $(YELLOW)make all-tests$(NC)       - Executa TODOS os testes (incluindo testes pagos sem perguntar)"
	@echo "  $(YELLOW)make test-specific$(NC)   - Executa teste específico (ex: FILE=test_service_points.py)"
	@echo "  $(YELLOW)make test-telegram$(NC)   - Executa testes do Bot do Telegram"
	@echo "  $(YELLOW)make test-cov$(NC)        - Mostra cobertura de código"
	@echo "  $(YELLOW)make test-html$(NC)       - Executa testes e gera relatório HTML"
	@echo ""
	@echo "$(YELLOW)Testes LLM - OpenAI:$(NC)"
	@echo "  $(YELLOW)make test-openai$(NC)              - Todos os testes OpenAI (básicos + integração)"
	@echo "  $(YELLOW)make test-openai-basic$(NC)        - Testes básicos OpenAI (sem gastar tokens)"
	@echo "  $(YELLOW)make test-openai-integration$(NC)  - Testes de integração OpenAI (gasta tokens)"
	@echo ""
	@echo "$(YELLOW)Testes LLM - Ollama:$(NC)"
	@echo "  $(YELLOW)make test-ollama$(NC)              - Todos os testes Ollama (básicos + integração)"
	@echo "  $(YELLOW)make test-ollama-basic$(NC)        - Testes básicos Ollama (sem conexão)"
	@echo "  $(YELLOW)make test-ollama-integration$(NC)  - Testes de integração Ollama (requer Ollama rodando)"
	@echo ""
	@echo "$(YELLOW)Testes LLM - Integração Completa:$(NC)"
	@echo "  $(YELLOW)make test-llm-integration$(NC)     - Testes de integração completos (usa provedor do .env)"
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
	@echo ""
	@echo "$(GREEN)Verificando Ollama...$(NC)"
	@if command -v ollama >/dev/null 2>&1; then \
		echo "$(GREEN)✓ Ollama instalado$(NC)"; \
		if pgrep -x ollama >/dev/null 2>&1; then \
			echo "$(GREEN)✓ Ollama já está rodando$(NC)"; \
		else \
			echo "$(YELLOW)Iniciando Ollama em background...$(NC)"; \
			nohup ollama serve > /dev/null 2>&1 & \
			sleep 2; \
			echo "$(GREEN)✓ Ollama iniciado$(NC)"; \
		fi; \
		if ollama list | grep -q llama2; then \
			echo "$(GREEN)✓ Modelo llama2 já instalado$(NC)"; \
		else \
			echo "$(YELLOW)Baixando modelo llama2 (pode demorar alguns minutos)...$(NC)"; \
			ollama pull llama2; \
			echo "$(GREEN)✓ Modelo llama2 instalado$(NC)"; \
		fi; \
	else \
		echo "$(YELLOW)⚠️  Ollama não instalado$(NC)"; \
		echo "$(YELLOW)Para usar LLMs locais, instale o Ollama:$(NC)"; \
		echo "$(YELLOW)  macOS: brew install ollama$(NC)"; \
		echo "$(YELLOW)  Linux: curl -fsSL https://ollama.ai/install.sh | sh$(NC)"; \
	fi
	@echo ""
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

# Inicia o bot do Telegram
start-bot:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f ".env" ]; then \
		echo "$(RED)Erro: Arquivo .env não encontrado!$(NC)"; \
		echo "$(YELLOW)Copie .env.example para .env e configure o TELEGRAM_BOT_TOKEN$(NC)"; \
		exit 1; \
	fi
	@if ! grep -q "TELEGRAM_BOT_TOKEN=" .env || grep -q "TELEGRAM_BOT_TOKEN=seu_token_aqui" .env; then \
		echo "$(RED)Erro: TELEGRAM_BOT_TOKEN não configurado no .env!$(NC)"; \
		echo "$(YELLOW)Configure o token do bot no arquivo .env$(NC)"; \
		exit 1; \
	fi
	@if pgrep -f "telegram_bot/bot.py" > /dev/null; then \
		echo "$(YELLOW)Bot do Telegram já está rodando!$(NC)"; \
		echo "$(YELLOW)Use 'make stop-bot' para parar o bot antes de iniciar novamente.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Iniciando bot do Telegram...$(NC)"
	@nohup $(PYTHON_VENV) telegram_bot/bot.py > telegram_bot.log 2>&1 & echo $$! > telegram_bot.pid
	@sleep 2
	@if pgrep -f "telegram_bot/bot.py" > /dev/null; then \
		echo "$(GREEN)✓ Bot do Telegram iniciado com sucesso!$(NC)"; \
		echo "$(YELLOW)PID: $$(cat telegram_bot.pid)$(NC)"; \
		echo "$(YELLOW)Log: telegram_bot.log$(NC)"; \
		echo ""; \
		echo "$(GREEN)Use /start no Telegram para começar!$(NC)"; \
	else \
		echo "$(RED)Erro ao iniciar o bot. Verifique o log: telegram_bot.log$(NC)"; \
		rm -f telegram_bot.pid; \
		exit 1; \
	fi

# Para o bot do Telegram
stop-bot:
	@if [ ! -f "telegram_bot.pid" ]; then \
		echo "$(YELLOW)Nenhum bot em execução (arquivo PID não encontrado).$(NC)"; \
		if pgrep -f "telegram_bot/bot.py" > /dev/null; then \
			echo "$(YELLOW)Mas encontrei um processo do bot rodando. Parando...$(NC)"; \
			pkill -f "telegram_bot/bot.py"; \
			sleep 1; \
			if pgrep -f "telegram_bot/bot.py" > /dev/null; then \
				echo "$(RED)Processo não parou. Forçando...$(NC)"; \
				pkill -9 -f "telegram_bot/bot.py"; \
			fi; \
			echo "$(GREEN)✓ Bot parado!$(NC)"; \
		fi; \
	else \
		PID=$$(cat telegram_bot.pid); \
		if ps -p $$PID > /dev/null 2>&1; then \
			echo "$(YELLOW)Parando bot do Telegram (PID: $$PID)...$(NC)"; \
			kill $$PID; \
			sleep 1; \
			if ps -p $$PID > /dev/null 2>&1; then \
				echo "$(YELLOW)Processo não parou. Forçando...$(NC)"; \
				kill -9 $$PID; \
			fi; \
			echo "$(GREEN)✓ Bot parado!$(NC)"; \
		else \
			echo "$(YELLOW)Processo não está rodando (PID $$PID não existe).$(NC)"; \
		fi; \
		rm -f telegram_bot.pid; \
	fi

# Executa testes com opção de incluir testes de integração
test:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)  EXECUÇÃO DE TESTES$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "$(RED)⚠️  ATENÇÃO: Testes marcados como 'integration' consomem tokens da API OpenAI!$(NC)"
	@echo "$(YELLOW)   Esses testes fazem chamadas reais às APIs de LLM.$(NC)"
	@echo ""
	@read -p "Deseja executar os testes que gastam tokens? (s/N): " confirm; \
	echo ""; \
	if [ "$$confirm" = "s" ] || [ "$$confirm" = "S" ]; then \
		echo "$(GREEN)Executando TODOS os testes (incluindo testes de integração)...$(NC)"; \
		echo "$(YELLOW)Certifique-se de que OPENAI_API_KEY está configurada no .env$(NC)"; \
		echo ""; \
		$(VENV_NAME)/bin/pytest tests/ -v; \
	else \
		echo "$(GREEN)Executando testes EXCETO os de integração (sem gastar tokens)...$(NC)"; \
		echo ""; \
		$(VENV_NAME)/bin/pytest tests/ -v -m "not integration"; \
	fi
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)  ✓ TESTES CONCLUÍDOS!$(NC)"
	@echo "$(GREEN)========================================$(NC)"

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

# Executa TODOS os testes do projeto (incluindo testes de integração que gastam tokens)
all-tests:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)  EXECUÇÃO COMPLETA DE TESTES$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Este comando executará TODOS os 140 testes do projeto.$(NC)"
	@echo "$(RED)⚠️  ATENÇÃO: Inclui 24 testes de integração que consomem tokens da API OpenAI!$(NC)"
	@echo "$(YELLOW)Certifique-se de que OPENAI_API_KEY está configurada no .env$(NC)"
	@echo ""
	$(VENV_NAME)/bin/pytest tests/ -v
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)  ✓ TODOS OS TESTES CONCLUÍDOS!$(NC)"
	@echo "$(GREEN)========================================$(NC)"

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

# Executa todos os testes Ollama (básicos + integração)
test-ollama:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando todos os testes Ollama...$(NC)"
	@echo "$(RED)⚠️  ATENÇÃO: Certifique-se de que o Ollama está rodando!$(NC)"
	@echo "$(YELLOW)Execute 'ollama serve' em outro terminal antes de continuar$(NC)"
	@echo ""
	@read -p "Ollama está rodando? (s/N): " confirm; \
	if [ "$$confirm" = "s" ] || [ "$$confirm" = "S" ]; then \
		$(VENV_NAME)/bin/pytest tests/test_llm/test_ollama_provider.py -v; \
	else \
		echo "$(YELLOW)Testes cancelados.$(NC)"; \
		echo "$(YELLOW)Inicie o Ollama com: ollama serve$(NC)"; \
	fi

# Executa apenas testes básicos Ollama (sem conexão)
test-ollama-basic:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando testes básicos Ollama (sem integração)...$(NC)"
	@echo "$(GREEN)✓ Estes testes NÃO requerem Ollama rodando$(NC)"
	@echo ""
	$(VENV_NAME)/bin/pytest tests/test_llm/test_ollama_provider.py -m "not integration" -v

# Executa apenas testes de integração Ollama (requer Ollama rodando)
test-ollama-integration:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando testes de integração Ollama...$(NC)"
	@echo "$(RED)⚠️  ATENÇÃO: Certifique-se de que o Ollama está rodando!$(NC)"
	@echo "$(YELLOW)Execute 'ollama serve' em outro terminal antes de continuar$(NC)"
	@echo ""
	@read -p "Ollama está rodando? (s/N): " confirm; \
	if [ "$$confirm" = "s" ] || [ "$$confirm" = "S" ]; then \
		$(VENV_NAME)/bin/pytest tests/test_llm/test_ollama_provider.py -m integration -v; \
	else \
		echo "$(YELLOW)Testes cancelados.$(NC)"; \
		echo "$(YELLOW)Inicie o Ollama com: ollama serve$(NC)"; \
	fi

# Executa testes de integração completa (usa provedor configurado no .env)
test-llm-integration:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Executando testes de integração completa LLM...$(NC)"
	@echo "$(YELLOW)Estes testes usam o provedor configurado no .env$(NC)"
	@echo "$(YELLOW)Certifique-se de que o provedor está configurado e disponível$(NC)"
	@echo ""
	@read -p "Deseja continuar? (s/N): " confirm; \
	if [ "$$confirm" = "s" ] || [ "$$confirm" = "S" ]; then \
		$(VENV_NAME)/bin/pytest tests/test_llm/test_llm_integration.py -m integration -v; \
	else \
		echo "$(YELLOW)Testes cancelados.$(NC)"; \
	fi

# Executa testes do Bot do Telegram
test-telegram:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)Erro: Ambiente virtual não encontrado!$(NC)"; \
		echo "$(YELLOW)Execute 'make setup' primeiro.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)  TESTES DO BOT DO TELEGRAM$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "$(GREEN)Executando testes do bot do Telegram e integração de rotas...$(NC)"
	@echo "$(YELLOW)✓ Estes testes NÃO requerem o bot rodando$(NC)"
	@echo "$(YELLOW)✓ Estes testes NÃO consomem tokens de API$(NC)"
	@echo ""
	$(VENV_NAME)/bin/pytest tests/test_telegram_bot.py -v
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)  ✓ TESTES DO TELEGRAM CONCLUÍDOS!$(NC)"
	@echo "$(GREEN)========================================$(NC)"

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

# 🤖 Integração com LLMs - Assistente Inteligente

## Visão Geral

O sistema de otimização de rotas agora conta com um **Assistente Inteligente** baseado em LLMs (Large Language Models) que gera automaticamente:

1. **Manual de Instruções** para equipe de transporte
2. **Roteiro Detalhado** de visitas para motoristas
3. **Sistema de Perguntas e Respostas** em linguagem natural

## 📋 Funcionalidades

### 1. Manual de Instruções para Equipe de Transporte

Gera um manual completo e profissional contendo:

- **Introdução** explicando a importância da missão
- **Sequência de atendimentos** com instruções detalhadas para cada parada
- **Instruções específicas** sensíveis ao contexto de cada tipo de atendimento:
  - Emergências obstétricas (prioridade máxima)
  - Violência doméstica (discrição e protocolos especiais)
  - Medicamentos hormonais (controle de temperatura)
  - Cuidados pós-parto (sensibilidade e paciência)
  - Atendimentos regulares
- **Seção de Prioridades e Alertas** destacando pontos críticos
- **Checklist Pré-Rota** com itens essenciais
- **Orientações para imprevistos**

**Exemplo de uso:**
```python
from src.llm.generators.manual_generator import ManualGenerator
from src.llm.providers.openai_provider import OpenAIProvider

provider = OpenAIProvider(api_key="sua-chave", model="gpt-3.5-turbo")
generator = ManualGenerator(provider)

manual = generator.generate_single_vehicle_manual(
    route=best_route,
    arrival_times=arrival_times,
    total_distance=100.5,
    total_time=480
)
```

### 2. Roteiro Detalhado de Visitas

Gera um roteiro passo a passo para motoristas com:

- **Cabeçalho** com resumo da jornada
- **Detalhes de cada parada**:
  - Número sequencial
  - Horário de chegada previsto
  - Tipo de atendimento
  - Tempo estimado no local
  - Próximo destino e tempo de viagem
  - Observações importantes
- **Destaque visual** para paradas prioritárias
- **Marcos de tempo** importantes
- **Resumo do dia** e pontos de atenção

**Exemplo de uso:**
```python
from src.llm.generators.itinerary_generator import ItineraryGenerator

generator = ItineraryGenerator(provider)

itinerary = generator.generate_detailed_itinerary(
    route=best_route,
    arrival_times=arrival_times,
    total_distance=100.5,
    total_time=480
)
```

### 3. Sistema de Perguntas em Linguagem Natural

Permite fazer perguntas sobre a rota otimizada em linguagem natural:

**Exemplos de perguntas:**
- "Qual é o próximo atendimento prioritário?"
- "Quantas paradas de emergência temos hoje?"
- "Quais pontos têm janelas de tempo restritas?"
- "Como devo transportar os medicamentos hormonais?"
- "Qual é a distância total da rota?"

**Características:**
- Mantém histórico de conversação
- Respostas contextualizadas baseadas na rota
- Sugestões inteligentes de perguntas
- Análise de prioridades e janelas de tempo

**Exemplo de uso:**
```python
from src.llm.generators.qa_generator import QAGenerator

generator = QAGenerator(provider)

answer = generator.answer_question(
    question="Qual o próximo atendimento prioritário?",
    route=best_route,
    arrival_times=arrival_times,
    total_distance=100.5,
    total_time=480
)
```

## ⚙️ Configuração

O sistema suporta dois provedores de LLM:

1. **OpenAI** - Modelos em nuvem (GPT-3.5, GPT-4)
2. **Ollama** - Modelos locais (Llama2, Mistral, CodeLlama)

### Opção 1: OpenAI (Nuvem)

#### 1.1. Configurar API Key

Edite o arquivo `.env` na raiz do projeto:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-sua-chave-aqui
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
```

#### 1.2. Modelos Disponíveis

- `gpt-3.5-turbo` (recomendado para custo-benefício)
- `gpt-4` (maior qualidade, maior custo)
- `gpt-4-turbo` (equilíbrio entre qualidade e velocidade)

#### 1.3. Obter API Key

1. Acesse [OpenAI Platform](https://platform.openai.com)
2. Crie uma conta ou faça login
3. Vá em "API Keys"
4. Clique em "Create new secret key"
5. Copie a chave e adicione no `.env`

### Opção 2: Ollama (Local)

#### 2.1. Instalar Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Baixe o instalador em: https://ollama.ai/download

#### 2.2. Iniciar Serviço

```bash
ollama serve
```

O Ollama iniciará na porta padrão `11434`.

#### 2.3. Baixar Modelo

```bash
# Modelo Llama 2 (padrão, ~3.8GB)
ollama pull llama2

# Modelo Mistral (~4.1GB)
ollama pull mistral

# Modelo CodeLlama para código (~3.8GB)
ollama pull codellama

# Modelo menor para testes (~1.9GB)
ollama pull llama2:7b
```

Para listar modelos disponíveis:
```bash
ollama list
```

#### 2.4. Configurar no .env

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
```

#### 2.5. Vantagens do Ollama

✅ **Gratuito** - Sem custos de API
✅ **Privacidade** - Dados não saem da sua máquina
✅ **Offline** - Funciona sem internet
✅ **Sem limites** - Sem rate limiting

❌ **Desvantagens:**
- Requer hardware adequado (mínimo 8GB RAM)
- Modelos menores podem ter qualidade inferior
- Primeira execução é mais lenta

#### 2.6. Comparação de Modelos Ollama

| Modelo | Tamanho | Uso Recomendado | Velocidade |
|--------|---------|-----------------|------------|
| llama2 | ~3.8GB | Uso geral | Média |
| mistral | ~4.1GB | Tarefas complexas | Média |
| codellama | ~3.8GB | Geração de código | Média |
| llama2:7b | ~1.9GB | Testes rápidos | Rápida |

### Parâmetros de Temperatura

- `0.0` - Mais determinístico e consistente
- `0.7` - Balanceado (padrão)
- `2.0` - Mais criativo e variado

## 🏗️ Arquitetura

### Estrutura de Módulos

```
src/llm/
├── providers/          # Provedores de LLM
│   ├── base.py        # Interface base
│   └── openai_provider.py
├── prompts/           # Templates de prompts
│   └── route_prompts.py
├── generators/        # Geradores de conteúdo
│   ├── manual_generator.py
│   ├── itinerary_generator.py
│   └── qa_generator.py
└── utils/            # Utilitários
    └── streamlit_integration.py
```

### Fluxo de Dados

```
Rota Otimizada
    ↓
Preparação de Dados (streamlit_integration.py)
    ↓
Construção de Prompts (route_prompts.py)
    ↓
Geração via LLM (generators/)
    ↓
Formatação e Exibição (Streamlit)
```

## 🎯 Uso no Streamlit

Após executar a otimização de rotas, a seção **"🤖 Assistente Inteligente com IA"** aparece com três abas:

### Aba 1: 📋 Manual de Instruções
- Botão "Gerar Manual" - Cria manual completo
- Botão "Checklist" - Gera checklist pré-inicialização da rota

### Aba 2: 🗺️ Roteiro Detalhado
- Botão "Gerar Roteiro" - Cria roteiro passo a passo
- Botão "Prioridades" - Analisa e explica prioridades

### Aba 3: 💬 Perguntas & Respostas
- Sugestões de perguntas clicáveis
- Campo de texto para perguntas personalizadas
- Histórico de conversação
- Botão para limpar histórico

## 📊 Contexto de Saúde da Mulher

O sistema é especializado em atendimentos de saúde da mulher, com conhecimento sobre:

### Tipos de Atendimento

1. **Emergência Obstétrica** (Prioridade 1)
   - Risco de vida
   - Atendimento imediato
   - Equipamentos especiais

2. **Violência Doméstica** (Prioridade 2)
   - Discrição absoluta
   - Protocolos de segurança
   - Janelas de tempo específicas

3. **Medicamento Hormonal** (Prioridade 3)
   - Controle de temperatura (2-8°C)
   - Caixa térmica
   - Entrega rápida

4. **Pós-Parto** (Prioridade 4)
   - Sensibilidade
   - Respeito a horários de amamentação
   - Paciência

5. **Regular** (Prioridade 5)
   - Procedimento padrão
   - Profissionalismo

### Restrições Consideradas

- **Horário comercial**: 8h às 18h
- **Medicamentos prioritários**: Até 1º dia (1 veículo) ou até 12:00 (2 veículos)
- **Janelas de tempo**:
  - Violência doméstica: 8h-12h (1v) ou 8h-10h (2v)
  - Pós-parto: 9h-13h (1v) ou 9h-11h (2v)

## 🧪 Testes

### Testes OpenAI

```bash
# Testar provedor OpenAI (básico, sem API)
pytest tests/test_llm/test_openai_provider.py::TestOpenAIProviderBasic -v

# Testar conexão OpenAI (requer API key)
pytest tests/test_llm/test_openai_provider.py -m integration -v

# Todos os testes OpenAI
pytest tests/test_llm/test_openai_provider.py -v
```

### Testes Ollama

**IMPORTANTE:** Certifique-se de que o Ollama está rodando antes de executar testes de integração!

```bash
# Testar provedor Ollama (básico, sem conexão)
pytest tests/test_llm/test_ollama_provider.py::TestOllamaProviderBasic -v

# Testar conexão Ollama (requer Ollama rodando)
pytest tests/test_llm/test_ollama_provider.py -m integration -v

# Todos os testes Ollama
pytest tests/test_llm/test_ollama_provider.py -v

# Pular testes de integração
pytest tests/test_llm/test_ollama_provider.py -m "not integration" -v
```

### Teste Manual Rápido

**OpenAI:**
```python
from src.llm.providers.openai_provider import OpenAIProvider

provider = OpenAIProvider(
    api_key="sua-chave",
    model="gpt-3.5-turbo"
)

if provider.validate_connection():
    print("✅ Conexão com OpenAI OK!")
    response = provider.generate_text("Diga olá em português")
    print(f"Resposta: {response}")
```

**Ollama:**
```python
from src.llm.providers.ollama_provider import OllamaProvider

provider = OllamaProvider(
    model="llama2",
    base_url="http://localhost:11434"
)

if provider.validate_connection():
    print("✅ Conexão com Ollama OK!")
    response = provider.generate_text("Diga olá em português")
    print(f"Resposta: {response}")
```

## 💡 Dicas de Uso

### OpenAI
1. **Custos**: Use `gpt-3.5-turbo` para desenvolvimento e testes
2. **Qualidade**: Use `gpt-4` para produção quando precisar de máxima qualidade
3. **Monitoramento**: Acompanhe uso em https://platform.openai.com/usage

### Ollama
1. **Primeira execução**: Modelos levam tempo para carregar na memória
2. **Performance**: Use GPU se disponível (detectada automaticamente)
3. **Modelos**: Comece com `llama2:7b` para testes rápidos
4. **Cache**: Modelos ficam em cache após primeiro uso

### Geral
1. **Temperatura**: Mantenha em 0.7 para equilíbrio entre consistência e criatividade
2. **Histórico**: Limpe o histórico de Q&A periodicamente para manter contexto relevante
3. **Prompts**: Customize os prompts para seu caso de uso específico

## 🔒 Segurança

- **Nunca** commit o arquivo `.env` com chaves reais
- Use variáveis de ambiente em produção
- Monitore uso da API para evitar custos inesperados
- Implemente rate limiting se necessário

## 📚 Referências

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Python dotenv](https://pypi.org/project/python-dotenv/)

## 🆘 Troubleshooting

### Erro: "LLM não inicializado"

**Causa**: API Key não configurada ou inválida

**Solução**:
1. Verifique se o arquivo `.env` existe
2. Confirme que `OPENAI_API_KEY` está preenchida
3. Teste a chave: `python -c "from openai import OpenAI; OpenAI(api_key='sua-chave').models.list()"`

### Erro: "Rate limit exceeded"

**Causa**: Muitas requisições em curto período

**Solução**:
1. Aguarde alguns minutos
2. Considere upgrade do plano da OpenAI

### Respostas genéricas ou irrelevantes

**Causa**: Prompts não otimizados ou temperatura muito alta

**Solução**:
1. Ajuste a temperatura para 0.5 ou menos
2. Customize os prompts em `route_prompts.py`
3. Forneça mais contexto nos prompts

## 🚀 Próximos Passos

- [ ] Suporte para Ollama (LLMs locais)
- [ ] Cache de respostas frequentes
- [ ] Exportação de documentos em PDF
- [ ] Tradução multilíngue
- [ ] Integração com WhatsApp/Telegram
- [ ] Análise de sentimento em feedback
- [ ] Geração de relatórios automáticos

## 📝 Changelog

### v1.0.0 (2026-03-06)
- ✨ Implementação inicial da integração LLM
- ✨ Gerador de manual de instruções
- ✨ Gerador de roteiro detalhado
- ✨ Sistema de Q&A em linguagem natural
- ✨ Suporte para OpenAI GPT-3.5/GPT-4
- ✨ Interface integrada no Streamlit
- 📚 Documentação completa

---

**Desenvolvido com ❤️ para otimização de rotas em saúde da mulher**

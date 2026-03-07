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

### 1. Configurar API Key

Edite o arquivo `.env` na raiz do projeto:

```bash
# Renomear .env.example para .env
cp .env.example .env
```

Adicione sua chave da OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-sua-chave-aqui
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
```

### 2. Modelos Disponíveis

- `gpt-3.5-turbo` (recomendado para custo-benefício)
- `gpt-4` (maior qualidade, maior custo)
- `gpt-4-turbo` (equilíbrio entre qualidade e velocidade)

### 3. Parâmetros de Temperatura

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

Execute os testes da integração LLM:

```bash
# Testar provedor OpenAI
pytest tests/test_llm/test_openai_provider.py -v

# Testar todos os módulos LLM
pytest tests/test_llm/ -v
```

## 💡 Dicas de Uso

1. **Custos**: Use `gpt-3.5-turbo` para desenvolvimento e testes
2. **Qualidade**: Use `gpt-4` para produção quando precisar de máxima qualidade
3. **Temperatura**: Mantenha em 0.7 para equilíbrio entre consistência e criatividade
4. **Histórico**: Limpe o histórico de Q&A periodicamente para manter contexto relevante
5. **Prompts**: Customize os prompts para seu caso de uso específico

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

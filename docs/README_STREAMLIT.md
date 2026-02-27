# Interface Gráfica com Streamlit

## 📋 Descrição

Interface gráfica web para o Sistema de Otimização de Rotas com Restrições, desenvolvida com Streamlit. Permite executar o algoritmo genético de forma interativa através do navegador.

## 🚀 Como Executar

### 1. Instalar Dependências

Certifique-se de que todas as dependências estão instaladas:

```bash
pip install -r requirements.txt
```

### 2. Executar a Aplicação

Execute o seguinte comando no terminal:

```bash
streamlit run app_streamlit.py
```

Ou usando o Makefile:

```bash
make streamlit
```

### 3. Acessar a Interface

A aplicação será aberta automaticamente no navegador em:
- **URL Local:** http://localhost:8501

## 🎮 Como Usar

### Tela Inicial

1. **Clique em "▶️ Start"** para iniciar o processo de otimização
2. Aguarde enquanto o algoritmo genético processa 200 gerações
3. Uma barra de progresso mostrará o andamento

### Após a Otimização

A interface exibirá:

- **Métricas Principais:**
  - Fitness da melhor solução
  - Número de dias necessários para entrega
  - Horário da última entrega

- **Melhor Solução:** Vetor com a ordem dos pontos de atendimento

- **Ordem de Prioridades:** Agrupamento dos pontos por tipo de atendimento

- **Ordem de Atendimento Detalhada:** Lista completa com horários e dias

### Opções Disponíveis

- **🔄 Reiniciar (R):** Gera novos pontos e reinicia a otimização
- **❌ Encerrar (Q):** Encerra a aplicação

## 📊 Informações Exibidas

### Sidebar

- Parâmetros do algoritmo genético
- Legenda de cores por tipo de atendimento

### Área Principal

- Progresso da otimização em tempo real
- Resultados detalhados da melhor rota encontrada
- Visualização da ordem de atendimento

## 🎨 Legenda de Cores

- 🔴 **Vermelho:** Emergência Obstétrica (prioridade máxima)
- 🟠 **Laranja:** Violência Doméstica (protocolo especial)
- 🔵 **Azul:** Medicamento Hormonal (temperatura controlada)
- 🟣 **Roxo:** Pós-Parto (janela de tempo específica)
- ⚫ **Cinza:** Atendimento Regular

## ⚙️ Parâmetros do Algoritmo

- **Pontos de Atendimento:** 20
- **Tamanho da População:** 100
- **Gerações Máximas:** 200
- **Probabilidade de Mutação:** 30%

## 🔧 Tecnologias Utilizadas

- **Streamlit:** Framework para criação de aplicações web interativas
- **Python 3.12+:** Linguagem de programação
- **NumPy:** Computação científica

## 📝 Notas

- A aplicação roda localmente no seu computador
- Cada execução gera pontos de atendimento aleatórios
- O algoritmo genético busca a melhor rota respeitando todas as restrições
- Os resultados podem variar entre execuções devido à natureza estocástica do algoritmo

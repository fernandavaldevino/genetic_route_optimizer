# Interface Gráfica com Streamlit

## 📑 Índice

- [� Descrição](#-descrição)
- [🚀 Como Executar](#-como-executar)
  - [1. Instalar Dependências](#1-instalar-dependências)
  - [2. Executar a Aplicação](#2-executar-a-aplicação)
  - [3. Acessar a Interface](#3-acessar-a-interface)
- [🎮 Como Usar](#-como-usar)
  - [Tela Inicial](#tela-inicial)
  - [Após a Otimização](#após-a-otimização)
  - [Opções Disponíveis](#opções-disponíveis)
- [📊 Informações Exibidas](#-informações-exibidas)
  - [Sidebar](#sidebar)
  - [Área Principal](#área-principal)
- [🎨 Legenda de Cores](#-legenda-de-cores)
- [⚙️ Parâmetros do Algoritmo](#️-parâmetros-do-algoritmo)
- [🔧 Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [📝 Notas](#-notas)

---

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

1. **Configure os parâmetros** na tela inicial (opcional - todos possuem valores padrão):
   - **Número de Veículos**: Escolha entre 1 ou 2 veículos (padrão: 1)
   - **Número de Gerações**: Defina quantas gerações o algoritmo executará (padrão: 500)
   - **Velocidade Média**: Configure a velocidade média do percurso em km/h (padrão: 80 km/h)

2. Clique no botão **Iniciar Otimização** para iniciar o processo de otimização das rotas

3. Aguarde enquanto o algoritmo genético processa a quantidade de gerações configurada

4. Uma barra de progresso mostrará o andamento em tempo real

### Após a Otimização

A interface exibirá:

- **Métricas Principais:**
  - Fitness total da melhor solução
  - Número de dias necessários para percorrer toda a rota, considerando o tempo de atendimento, a distância e a velocidade média do(s) veículo(s)
  - Horário da última entrega

- **Melhor Solução:** Vetor com a ordem dos pontos de atendimento

- **Ordem de Prioridades:** Agrupamento dos pontos por tipo de atendimento

- **Ordem de Atendimento Detalhada:** Lista completa com horários e dias de atendimento

### Opções Disponíveis
Opções disponíveis apenas durante a execução do arquivo Pygame:
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

### Parâmetros Configuráveis pelo Usuário

- **Número de Veículos:** 1 ou 2 (padrão: 1)
  - 1 veículo: Deadline de prioritários até fim do 1º dia (1440 min)
  - 2 veículos: Deadline de prioritários até 12h (720 min)

- **Número de Gerações:** Quantidade de gerações do algoritmo genético (padrão: 500)
  - Mais gerações = melhor otimização, mas maior tempo de processamento

- **Velocidade Média:** Velocidade média do veículo em km/h (padrão: 80 km/h)
  - Afeta o cálculo de tempo de viagem entre pontos e pode afetar o horário de entrega dos medicamentos, gerando penalidades no fitness total

### Parâmetros Fixos

- **Pontos de Atendimento:** 20
- **Tamanho da População:** 100
- **Probabilidade de Mutação:** 30%
- **Horário de Início:** 7:30h (chegada do(s) veículo(s) no Depósito para pegar os medicamentos)
- **Horário Comercial:** 8h às 18h (saída para entrega e expediente do motorista)

## 🔧 Tecnologias Utilizadas

- **Streamlit:** Framework para criação de aplicações web interativas
- **Python 3.12+:** Linguagem de programação
- **NumPy:** Computação científica

## 📝 Notas

- A aplicação roda localmente no seu computador
- Cada execução gera pontos de atendimento aleatórios, inclusive do Depósito
- O algoritmo genético busca a melhor rota respeitando todas as restrições e prioridades dos atendimentos
- Os resultados podem variar entre execuções devido à natureza estocástica do algoritmo

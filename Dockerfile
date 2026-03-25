# Usa uma imagem oficial do Python
FROM python:3.12-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia requirements primeiro (cache de camadas Docker)
COPY requirements.txt .

# Instala todas as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia os módulos do projeto
COPY main.py .
COPY api/ ./api/
COPY src/ ./src/
COPY telegram_bot/ ./telegram_bot/

# Copia template de variáveis de ambiente
COPY .env.example ./.env

# Expõe a porta que o Cloud Run espera (8080)
EXPOSE 8080

# Define variável de ambiente
ENV PYTHONUNBUFFERED=1

# Comando para rodar a aplicação
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]

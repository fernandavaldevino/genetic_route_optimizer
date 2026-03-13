# Usa uma imagem oficial do Python leve
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código da aplicação
COPY . .

# Expõe a porta que o Cloud Run espera (8080)
EXPOSE 8080

# Comando para rodar a aplicação FastAPI (não o bot em polling)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]

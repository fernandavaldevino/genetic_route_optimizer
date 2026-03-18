# Usa uma imagem oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala apenas as dependências essenciais
RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn[standard]==0.32.0 \
    pydantic==2.9.2

# Copia apenas os arquivos necessários
COPY main.py .

# Expõe a porta que o Cloud Run espera (8080)
EXPOSE 8080

# Define variável de ambiente
ENV PYTHONUNBUFFERED=1

# Comando para rodar a aplicação
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

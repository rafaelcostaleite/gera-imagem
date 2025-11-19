# Use uma imagem Python oficial como base
FROM python:3.11-slim

# Definir o diretório de trabalho no container
WORKDIR /app

# Instalar dependências do sistema necessárias para Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de requisitos
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p uploads output

# Expor a porta 5000
EXPOSE 5000

# Variáveis de ambiente
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Comando para executar a aplicação
CMD ["python", "app.py"]

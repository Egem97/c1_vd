FROM python:3.10-slim

# Establece directorio de trabajo
WORKDIR /app

# Copia requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python sin cache
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Expone el puerto de Streamlit
EXPOSE 8000

# Comando de entrada
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8000", "--server.address=0.0.0.0"]
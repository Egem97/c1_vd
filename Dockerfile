FROM python:3.10-slim

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y apt-transport-https\
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000


ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8000", "--server.address=0.0.0.0"]
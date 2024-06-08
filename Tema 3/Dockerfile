FROM python:3.8

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY ./adapter/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY ./adapter/adapter.py ./adapter/start.sh ./
RUN chmod +x start.sh

CMD ["./start.sh"]

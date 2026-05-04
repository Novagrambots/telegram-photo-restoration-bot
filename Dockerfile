FROM python:3.12-slim

# системные зависимости: только ca-certificates для https к HuggingFace Spaces
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# сначала зависимости (кэшируется Docker слоем)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# потом код
COPY bot/ bot/

CMD ["python", "-m", "bot.main"]

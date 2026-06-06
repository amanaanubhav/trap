FROM python:3.11-slim

WORKDIR /app

# install system dependencies required for building python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh
# use our wrapper script to handle process crashes and serve fallback
CMD ["./start.sh"]

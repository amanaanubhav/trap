FROM python:3.11-slim

WORKDIR /app

# only the fallback page, no pip deps
COPY index.html .
COPY server.py .

CMD ["python", "server.py"]

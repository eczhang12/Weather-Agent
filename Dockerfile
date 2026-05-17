FROM python:3.12-slim AS final

WORKDIR /app

# Install dependencies first so Docker can reuse this layer between code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]

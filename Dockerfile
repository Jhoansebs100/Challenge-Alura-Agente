# Imagen liviana de Python
FROM python:3.12-slim

WORKDIR /app

# Instalamos dependencias primero (aprovecha la caché de Docker si no cambian)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del proyecto
COPY . .

# Aseguramos que los chunks existan (si no, se generan a partir del PDF versionado)
RUN test -f data/chunks.json || python src/ingest.py --pdf docs/politicas_clinica_vitalis.pdf --salida data/chunks.json

EXPOSE 8000

# LLM_BACKEND se puede sobreescribir con `docker run -e LLM_BACKEND=anthropic ...`
ENV LLM_BACKEND=mock
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]

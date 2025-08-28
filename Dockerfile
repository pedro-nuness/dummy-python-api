FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir uvicorn[standard]

COPY pyproject.toml poetry.lock* ./
COPY app/ ./app/

RUN echo "# Default environment vars\nEXTERNAL_API_BASE_URL=https://index.coindesk.com\nLOG_LEVEL=INFO\nCIRCUIT_BREAKER_FAIL_MAX=5\nCIRCUIT_BREAKER_RESET_TIMEOUT=30" > .env

RUN pip install --no-cache-dir \
    fastapi==0.111.0 \
    httpx==0.27.0 \
    prometheus-fastapi-instrumentator==7.1.0 \
    pybreaker==1.1.0 \
    pydantic-settings==2.3.4 \
    slowapi==0.1.9 \
    tenacity==8.5.0

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

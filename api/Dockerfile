# Build from the repository root: docker build -f api/Dockerfile .
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY core /srv/core
COPY api /srv/api
RUN pip install --no-cache-dir /srv/core /srv/api

RUN useradd --create-home app
USER app
WORKDIR /srv/api
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

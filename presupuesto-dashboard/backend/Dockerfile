FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace/backend

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY backend /workspace/backend
COPY deploy/backend-entrypoint.sh /workspace/deploy/backend-entrypoint.sh

RUN chmod +x /workspace/deploy/backend-entrypoint.sh \
    && mkdir -p /workspace/data

EXPOSE 8000

CMD ["/workspace/deploy/backend-entrypoint.sh"]
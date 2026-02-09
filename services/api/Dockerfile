# Builder (installs deps)
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
  && rm -rf /var/lib/apt/lists/*

COPY services/api/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
 && pip install -r /app/requirements.txt

# Runtime (small image)
FROM python:3.13-slim AS runtime

RUN useradd -m -u 10001 appuser
WORKDIR /app

COPY --from=builder /usr/local /usr/local

COPY services/api/src /app/src

ENV PORT=8080
USER 10001

CMD ["python", "-m", "uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8080", "--workers", "2", "--proxy-headers"]

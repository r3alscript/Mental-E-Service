FROM python:3.13-alpine

RUN apk add --no-cache \
    postgresql-libs \
    postgresql-dev \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "core.asgi:application", "--host", "0.0.0.0", "--port", "8000"]

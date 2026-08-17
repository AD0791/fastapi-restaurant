# fastapi-restaurant

FastAPI backend for the restaurant platform.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Docker and Docker Compose

## Install dependencies

```bash
uv sync
```

## Run locally

```bash
uv run uvicorn main:app --reload
```

Serves on `http://localhost:8000`.

## Run with Docker

```bash
docker compose up --build
```

Serves on `http://localhost:8000`. Stop with `docker compose down`.

## Configuration

Copy `.env.example` to `.env` and adjust as needed.

## Health check

```bash
curl localhost:8000/health
```

Returns `{"status":"ok"}` once the service is up.

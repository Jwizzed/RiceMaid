# RiceMade

Ideathon

## Installation

```bash
poetry install
docker-compose up -d
alembic upgrade head
uvicorn app.main:app --reload
```

ngrok
```bash
ngrok http 8000 --host-header="127.0.0.1:8000"
```


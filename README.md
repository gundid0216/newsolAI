# newsolAI

Initial project structure for the newsolAI application.

## Stack

- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- PyTorch (CPU)
- Alembic
- pytest
- Docker

## Project Layout

```
app/          Application source code
tests/        Test suite
docs/         Documentation
scripts/      Utility scripts
docker/       Docker-related assets
model/        Trained model artifacts
data/         Data files
logs/         Application logs
```

## Getting Started

1. Copy `.env.example` to `.env` and adjust values.
2. Install dependencies: `pip install -r requirements.txt`
3. Start services: `docker-compose up --build`

## Entry Points

- `run_api.py` — Start the FastAPI server
- `train.py` — Model training
- `predict.py` — Model inference
- `simulate.py` — Simulation runner

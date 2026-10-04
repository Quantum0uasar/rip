# RIP: Regulatory Intelligence Pipeline

Downloads Alberta energy regulator data, checks it, tracks changes, and makes it searchable.

## What it does
- `run_daily.py` downloads the AER well licence list with retries and a format check, archives the raw file, and loads it into Postgres.
- Each load is compared with the previous state. New licences, status changes, and operator changes are logged as events.
- A FastAPI backend and a small web page search the licences and show the change log.

## Run it

    docker compose up -d
    python -m pip install -r requirements.txt
    docker exec -i rip-db-1 psql -U rip -d rip < db/schema.sql
    python run_daily.py
    uvicorn api.main:app --reload

Open http://127.0.0.1:8000

## Tests

    python -m pytest -q

Tests use sample data in tests/fixtures and a separate rip_test database. They never call live sites.

## Data source
Alberta Energy Regulator public well licence list. TODO: confirm and link the AER terms of use before sharing publicly.

Independent prototype, not affiliated with the data providers.

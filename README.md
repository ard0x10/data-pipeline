# data-pipeline

Nightly ETL jobs that load operational data into the reporting warehouse.

## Stages

| Stage | Module | Notes |
|---|---|---|
| Extract | `pipeline/extract.py` | Pulls from the source API in pages |
| Transform | `pipeline/transform.py` | Normalizes column names and types |
| Load | `pipeline/load.py` | Bulk inserts into the warehouse |

## Local setup

    python -m venv .venv
    . .venv/bin/activate          # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env

Fill in `.env`, then export it into the shell before running anything:

    set -a && . ./.env && set +a

### Environment variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `SOURCE_API_URL` | no | `https://api.internal/v1` | Base URL; job `path` values are appended to it |
| `WAREHOUSE_DSN` | **yes** | — | libpq connection string for the target warehouse |
| `LOG_LEVEL` | no | `INFO` | `DEBUG` also logs one line per inserted batch |

## Running

    python -m pipeline.run --date 2026-07-27

Without `--date` the run covers today. `--job` limits the run to named jobs and
can be repeated:

    python -m pipeline.run --job orders --job refunds

The job schedule lives in `config/schedule.yaml`. Every entry needs a `name`,
`path` and `table`; `pipeline/config.py` validates this before the warehouse
connection is opened, so a bad schedule fails immediately instead of halfway
through a load.

## Backfilling a date range

There is no `--until` flag: a run loads everything changed on or after
`--date`. To rebuild a closed range, walk it one day at a time and let the
`source_id` dedupe in `pipeline/transform.py` absorb the overlap.

    for day in $(seq 0 13); do
      python -m pipeline.run --date "$(date -d "2026-07-01 +$day day" +%F)" --job orders
    done

Re-running a day is safe: the load upserts on `source_id`, so rows that already
exist are updated in place rather than duplicated. Apply
`schema/0001_unique_source_id.sql` to the warehouse first — the upsert needs that
unique constraint. Keep the range short anyway; each day replays every page the
source API returns for that job.

## Tests

    python -m pytest -q

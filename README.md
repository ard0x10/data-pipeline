# data-pipeline

Nightly ETL jobs that load operational data into the reporting warehouse.

## Stages

| Stage | Module | Notes |
|---|---|---|
| Extract | `pipeline/extract.py` | Pulls from the source API in pages |
| Transform | `pipeline/transform.py` | Normalizes column names and types |
| Load | `pipeline/load.py` | Bulk inserts into the warehouse |

## Running

    python -m pipeline.run --date 2026-07-27

The job schedule lives in `config/schedule.yaml`.

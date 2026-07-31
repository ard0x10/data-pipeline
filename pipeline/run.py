"""Command line entrypoint for a single pipeline run."""

import argparse
import logging
import os
import sys
from datetime import date, datetime

from .config import ConfigError, read_jobs
from .extract import extract
from .load import load
from .transform import transform

logger = logging.getLogger(__name__)


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {value!r}")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog="pipeline.run")
    parser.add_argument(
        "--date",
        type=parse_date,
        default=date.today(),
        help="only load records updated on or after this date (default: today)",
    )
    parser.add_argument(
        "--job",
        action="append",
        dest="jobs",
        help="job name from config/schedule.yaml; repeat to run several (default: all)",
    )
    return parser.parse_args(argv)


def select_jobs(jobs, names):
    if not names:
        return jobs
    by_name = {job["name"]: job for job in jobs}
    unknown = [name for name in names if name not in by_name]
    if unknown:
        raise SystemExit(f"unknown job(s): {', '.join(unknown)}")
    return [by_name[name] for name in names]


def run_job(connection, job, since):
    rows = (transform(record) for record in extract(job["path"], since.isoformat()))
    return load(connection, job["table"], rows)


def main(argv=None):
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    args = parse_args(argv)
    try:
        jobs = select_jobs(read_jobs(), args.jobs)
    except ConfigError as exc:
        raise SystemExit(f"invalid schedule: {exc}")

    # Imported once the arguments validate so `--help` and job selection stay
    # usable without the warehouse driver installed.
    import psycopg2

    connection = psycopg2.connect(os.environ["WAREHOUSE_DSN"])
    try:
        for job in jobs:
            total = run_job(connection, job, args.date)
            logger.info("%s: loaded %s rows since %s", job["name"], total, args.date)
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

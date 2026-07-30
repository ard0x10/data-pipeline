from datetime import date

import pytest

from pipeline.run import parse_args, read_jobs, select_jobs

JOBS = [{"name": "orders"}, {"name": "refunds"}]


def test_parse_args_reads_iso_date():
    args = parse_args(["--date", "2026-07-27"])
    assert args.date == date(2026, 7, 27)


def test_parse_args_rejects_other_date_formats():
    with pytest.raises(SystemExit):
        parse_args(["--date", "27/07/2026"])


def test_parse_args_collects_repeated_jobs():
    args = parse_args(["--job", "orders", "--job", "refunds"])
    assert args.jobs == ["orders", "refunds"]


def test_select_jobs_defaults_to_every_job():
    assert select_jobs(JOBS, None) == JOBS


def test_select_jobs_rejects_unknown_names():
    with pytest.raises(SystemExit):
        select_jobs(JOBS, ["orders", "invoices"])


def test_read_jobs_returns_the_scheduled_jobs():
    names = [job["name"] for job in read_jobs()]
    assert names == ["orders", "refunds"]

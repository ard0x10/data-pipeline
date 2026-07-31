import pytest

from pipeline.config import ConfigError, read_jobs, validate_jobs


def job(**overrides):
    base = {"name": "orders", "path": "orders", "table": "warehouse.orders"}
    base.update(overrides)
    return base


def test_read_jobs_returns_the_scheduled_jobs():
    names = [entry["name"] for entry in read_jobs()]
    assert names == ["orders", "refunds"]


def test_read_jobs_reports_a_missing_file(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        read_jobs(tmp_path / "absent.yaml")


def test_read_jobs_reports_a_broken_file(tmp_path):
    path = tmp_path / "schedule.yaml"
    path.write_text("jobs: [\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="could not parse"):
        read_jobs(path)


def test_validate_jobs_accepts_a_complete_job():
    jobs = [job()]
    assert validate_jobs(jobs) is jobs


def test_validate_jobs_rejects_an_empty_schedule():
    with pytest.raises(ConfigError, match="non-empty"):
        validate_jobs([])


def test_validate_jobs_lists_every_missing_field():
    with pytest.raises(ConfigError, match="path, table"):
        validate_jobs([{"name": "orders"}])


def test_validate_jobs_rejects_a_blank_field():
    with pytest.raises(ConfigError, match="table"):
        validate_jobs([job(table="")])


def test_validate_jobs_rejects_duplicate_names():
    with pytest.raises(ConfigError, match="duplicate"):
        validate_jobs([job(), job(table="warehouse.orders_copy")])

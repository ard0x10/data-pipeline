"""Read and validate job definitions from the schedule file."""

import os

import yaml

SCHEDULE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "schedule.yaml",
)

REQUIRED_FIELDS = ("name", "path", "table")


class ConfigError(ValueError):
    """Raised when the schedule file cannot be used as-is."""


def validate_jobs(jobs):
    """Return `jobs` unchanged, or raise ConfigError describing the problem."""
    if not isinstance(jobs, list) or not jobs:
        raise ConfigError("schedule must define a non-empty 'jobs' list")

    seen = set()
    for position, job in enumerate(jobs, start=1):
        if not isinstance(job, dict):
            raise ConfigError(f"job #{position} must be a mapping")

        missing = [field for field in REQUIRED_FIELDS if not job.get(field)]
        if missing:
            label = job.get("name") or f"#{position}"
            raise ConfigError(f"job {label} is missing: {', '.join(missing)}")

        if job["name"] in seen:
            raise ConfigError(f"duplicate job name: {job['name']}")
        seen.add(job["name"])

    return jobs


def read_jobs(path=SCHEDULE):
    try:
        with open(path, encoding="utf-8") as handle:
            document = yaml.safe_load(handle) or {}
    except FileNotFoundError:
        raise ConfigError(f"schedule file not found: {path}")
    except yaml.YAMLError as exc:
        raise ConfigError(f"could not parse {path}: {exc}")

    if not isinstance(document, dict):
        raise ConfigError(f"{path} must contain a mapping at the top level")

    return validate_jobs(document.get("jobs"))

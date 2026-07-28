"""Normalize raw records into warehouse rows."""

from datetime import datetime

COLUMN_MAP = {
    "id": "source_id",
    "created_at": "created_at",
    "updated_at": "updated_at",
    "amount_cents": "amount_cents",
    "currency": "currency",
}


def parse_timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def transform(record):
    row = {target: record.get(source) for source, target in COLUMN_MAP.items()}
    row["created_at"] = parse_timestamp(row["created_at"])
    row["updated_at"] = parse_timestamp(row["updated_at"])
    return row

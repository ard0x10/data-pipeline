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
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def dedupe(rows):
    """Yield rows with a unique `source_id`, keeping the first occurrence."""
    seen = set()
    for row in rows:
        source_id = row["source_id"]
        if source_id in seen:
            continue
        seen.add(source_id)
        yield row


def transform(record):
    row = {target: record.get(source) for source, target in COLUMN_MAP.items()}
    row["created_at"] = parse_timestamp(row["created_at"])
    row["updated_at"] = parse_timestamp(row["updated_at"])
    return row

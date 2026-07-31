"""Normalize raw records into warehouse rows."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

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


def normalize_currency(value):
    """Return `value` as an ISO 4217 alphabetic code, or None when unset."""
    if value is None:
        return None
    code = value.strip().upper()
    return code or None


def warn_unmapped(record, _seen=None):
    """Log field names the source sent that COLUMN_MAP drops, once per process.

    A silently ignored column is how schema drift stays invisible until someone
    notices the warehouse is missing data, so the first sighting is worth a line
    in the log. Subsequent records with the same field stay quiet.
    """
    if _seen is None:
        _seen = _UNMAPPED_SEEN
    unmapped = sorted(set(record) - set(COLUMN_MAP) - _seen)
    if unmapped:
        _seen.update(unmapped)
        logger.warning("ignoring unmapped source field(s): %s", ", ".join(unmapped))
    return unmapped


_UNMAPPED_SEEN = set()


def transform(record):
    warn_unmapped(record)
    row = {target: record.get(source) for source, target in COLUMN_MAP.items()}
    row["created_at"] = parse_timestamp(row["created_at"])
    row["updated_at"] = parse_timestamp(row["updated_at"])
    row["currency"] = normalize_currency(row["currency"])
    return row

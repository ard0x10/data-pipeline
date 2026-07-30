from datetime import datetime, timedelta, timezone

from pipeline.transform import COLUMN_MAP, dedupe, parse_timestamp, transform


def test_parse_timestamp_returns_none_for_null():
    assert parse_timestamp(None) is None


def test_parse_timestamp_handles_z_suffix():
    parsed = parse_timestamp("2026-07-28T16:46:17Z")
    assert parsed == datetime(2026, 7, 28, 16, 46, 17, tzinfo=timezone.utc)


def test_parse_timestamp_keeps_explicit_offset():
    parsed = parse_timestamp("2026-07-28T18:46:17+02:00")
    assert parsed.utcoffset() == timedelta(hours=2)


def test_transform_maps_source_columns():
    record = {
        "id": "ord_1",
        "created_at": "2026-07-28T00:00:00Z",
        "updated_at": "2026-07-28T01:00:00Z",
        "amount_cents": 1250,
        "currency": "eur",
        "internal_note": "ignored",
    }
    row = transform(record)
    assert set(row) == set(COLUMN_MAP.values())
    assert row["source_id"] == "ord_1"
    assert row["amount_cents"] == 1250
    assert row["created_at"] == datetime(2026, 7, 28, 0, 0, tzinfo=timezone.utc)


def test_transform_fills_missing_fields_with_none():
    row = transform({"id": "ord_2"})
    assert row["amount_cents"] is None
    assert row["created_at"] is None


def test_dedupe_keeps_first_occurrence():
    rows = [
        {"source_id": "ord_1", "amount_cents": 100},
        {"source_id": "ord_2", "amount_cents": 200},
        {"source_id": "ord_1", "amount_cents": 999},
    ]
    assert [row["amount_cents"] for row in dedupe(rows)] == [100, 200]

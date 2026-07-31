"""Write transformed rows into the warehouse."""

import logging
from itertools import chain

from .transform import dedupe

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000

# `created_at` is deliberately left out of the update: the source sets it once and a
# re-run should not move it. The unique index this relies on lives in
# schema/0001_unique_source_id.sql.
UPSERT = (
    "INSERT INTO {table} (source_id, created_at, updated_at, amount_cents, currency) "
    "VALUES (%(source_id)s, %(created_at)s, %(updated_at)s, %(amount_cents)s, %(currency)s) "
    "ON CONFLICT (source_id) DO UPDATE SET "
    "updated_at = EXCLUDED.updated_at, "
    "amount_cents = EXCLUDED.amount_cents, "
    "currency = EXCLUDED.currency"
)


def batched(rows, size=BATCH_SIZE):
    batch = []
    for row in rows:
        batch.append(row)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def load(connection, table, rows):
    batches = batched(dedupe(rows))
    try:
        first = next(batches)
    except StopIteration:
        logger.info("nothing to load into %s, skipping", table)
        return 0

    total = 0
    with connection.cursor() as cursor:
        for batch in chain([first], batches):
            cursor.executemany(UPSERT.format(table=table), batch)
            total += len(batch)
            logger.debug("upserted batch of %s into %s", len(batch), table)
    connection.commit()
    logger.info("loaded %s rows into %s", total, table)
    return total

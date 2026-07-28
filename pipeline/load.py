"""Write transformed rows into the warehouse."""

BATCH_SIZE = 1000

INSERT = (
    "INSERT INTO {table} (source_id, created_at, updated_at, amount_cents, currency) "
    "VALUES (%(source_id)s, %(created_at)s, %(updated_at)s, %(amount_cents)s, %(currency)s)"
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
    total = 0
    with connection.cursor() as cursor:
        for batch in batched(rows):
            cursor.executemany(INSERT.format(table=table), batch)
            total += len(batch)
    connection.commit()
    return total

from pipeline.load import load


class FakeCursor:
    def __init__(self, calls, statements):
        self.calls = calls
        self.statements = statements

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def executemany(self, statement, rows):
        self.statements.append(statement)
        self.calls.append(list(rows))


class FakeConnection:
    def __init__(self):
        self.calls = []
        self.statements = []
        self.cursors = 0
        self.commits = 0

    def cursor(self):
        self.cursors += 1
        return FakeCursor(self.calls, self.statements)

    def commit(self):
        self.commits += 1


def test_load_skips_transaction_when_there_are_no_rows():
    connection = FakeConnection()
    assert load(connection, "orders", []) == 0
    assert connection.cursors == 0
    assert connection.commits == 0


def test_load_inserts_deduplicated_rows():
    connection = FakeConnection()
    rows = [
        {"source_id": "ord_1", "amount_cents": 100},
        {"source_id": "ord_1", "amount_cents": 999},
        {"source_id": "ord_2", "amount_cents": 200},
    ]
    assert load(connection, "orders", rows) == 2
    assert connection.cursors == 1
    assert connection.commits == 1
    assert [row["source_id"] for row in connection.calls[0]] == ["ord_1", "ord_2"]


def test_load_upserts_on_source_id():
    connection = FakeConnection()
    load(connection, "warehouse.orders", [{"source_id": "ord_1", "amount_cents": 100}])
    statement = connection.statements[0]
    assert "INSERT INTO warehouse.orders" in statement
    assert "ON CONFLICT (source_id) DO UPDATE" in statement


def test_load_never_overwrites_created_at():
    connection = FakeConnection()
    load(connection, "warehouse.orders", [{"source_id": "ord_1", "amount_cents": 100}])
    update = connection.statements[0].split("DO UPDATE SET", 1)[1]
    assert "created_at" not in update
    assert "updated_at = EXCLUDED.updated_at" in update

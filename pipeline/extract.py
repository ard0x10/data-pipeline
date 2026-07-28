"""Pull raw records from the source API."""

import os

import requests

BASE_URL = os.environ.get("SOURCE_API_URL", "https://api.internal/v1")
PAGE_SIZE = 500


def fetch_page(session, path, page):
    response = session.get(
        f"{BASE_URL}/{path}",
        params={"page": page, "per_page": PAGE_SIZE},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def extract(path, since):
    """Yield every record in `path` changed since `since`."""
    session = requests.Session()
    page = 1
    while True:
        payload = fetch_page(session, path, page)
        records = payload.get("data", [])
        if not records:
            return
        for record in records:
            if record["updated_at"] >= since:
                yield record
        page += 1

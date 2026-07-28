"""Pull raw records from the source API."""

import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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


def build_session():
    retry = Retry(
        total=4,
        backoff_factor=0.5,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def extract(path, since):
    """Yield every record in `path` changed since `since`."""
    session = build_session()
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

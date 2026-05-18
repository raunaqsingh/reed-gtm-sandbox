#!/usr/bin/env python3
import csv
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO.parent
OUTPUT = ROOT / "demand_agents" / "output"
LEDGER = OUTPUT / "reed_owned_deal_check_pages_ledger.csv"
LOG = OUTPUT / "reed_indexnow_submission_log.csv"
KEY = "6143ae831f600e5d0659d088edcf18ea"
KEY_LOCATION = f"https://raunaqsingh.github.io/reed-gtm-sandbox/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"


def read_urls():
    with LEDGER.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [row["public_url"] for row in rows if row.get("public_url")]


def submit(urls):
    payload = {
        "host": "raunaqsingh.github.io",
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def append_log(status, response_body, count):
    exists = LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as f:
        fields = [
            "submitted_at",
            "rail",
            "endpoint",
            "key_location",
            "url_count",
            "http_status",
            "response_body",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow(
            {
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "rail": "indexnow_crawl_discovery",
                "endpoint": ENDPOINT,
                "key_location": KEY_LOCATION,
                "url_count": count,
                "http_status": status,
                "response_body": response_body[:500],
            }
        )


def main():
    urls = read_urls()
    status, body = submit(urls)
    append_log(status, body, len(urls))
    print({"status": status, "url_count": len(urls), "log": str(LOG)})


if __name__ == "__main__":
    main()

import sys
import time
from datetime import date
from pathlib import Path

import httpx

from db.loader import load

URL = "https://www2.aer.ca/t/Production/views/COM-WellLicenceAllList/WellLicenceAllAB.csv"
SOURCE = "well_licences"
HEADER_START = "01.Licence Number"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; rip-pipeline/0.1; personal project)"}
TIMEOUT = httpx.Timeout(300, connect=30)


def fetch(dest: Path, attempts: int = 5, wait: int = 60) -> bool:
    for i in range(1, attempts + 1):
        print(f"Download attempt {i}/{attempts}")
        try:
            with httpx.stream("GET", URL, headers=HEADERS, timeout=TIMEOUT,
                              follow_redirects=True) as r:
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_bytes(1 << 20):
                        f.write(chunk)
        except httpx.HTTPError as e:
            print(f"Request failed: {e}")
        else:
            with open(dest, "r", encoding="utf-8-sig", errors="ignore") as f:
                first = f.readline()
            if first.startswith(HEADER_START):
                return True
            print("Got an error page or changed format, not the CSV")
            print(f"First line was: {first[:120]!r}")
        if i < attempts:
            print(f"Waiting {wait}s")
            time.sleep(wait)
    return False


def main() -> int:
    out_dir = Path("raw") / SOURCE
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{date.today().isoformat()}_WellLicenceAllAB.csv"

    if not fetch(dest):
        dest.unlink(missing_ok=True)
        print("FAILED: could not get a valid file")
        return 1

    count = load(dest)
    if count == 0:
        dest.unlink(missing_ok=True)
        print("No new data (file identical to a previous run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

import os
import hashlib
import sys
from pathlib import Path
import psycopg
from parse.structured.licence_parser import parse_licences

DSN = os.environ.get("RIP_DSN", "postgresql://rip:rip@localhost:5432/rip")

COLS = ("licence_no, company_name, latitude, longitude, surface_location, "
        "category_type, rating_level, status, status_date, non_routine, "
        "non_routine_status, raw_file_id")

EVENTS = [
    ("new_licence", """
        INSERT INTO licence_events (licence_no, event_type, new_value, raw_file_id)
        SELECT s.licence_no, 'new_licence', s.status, s.raw_file_id
        FROM staging s LEFT JOIN licences l ON l.licence_no = s.licence_no
        WHERE l.licence_no IS NULL"""),
    ("status_change", """
        INSERT INTO licence_events (licence_no, event_type, old_value, new_value, raw_file_id)
        SELECT s.licence_no, 'status_change', l.status, s.status, s.raw_file_id
        FROM staging s JOIN licences l ON l.licence_no = s.licence_no
        WHERE s.status IS DISTINCT FROM l.status"""),
    ("operator_change", """
        INSERT INTO licence_events (licence_no, event_type, old_value, new_value, raw_file_id)
        SELECT s.licence_no, 'operator_change', l.company_name, s.company_name, s.raw_file_id
        FROM staging s JOIN licences l ON l.licence_no = s.licence_no
        WHERE s.company_name IS DISTINCT FROM l.company_name"""),
]

UPSERT = f"""
INSERT INTO licences ({COLS})
SELECT DISTINCT ON (licence_no) {COLS} FROM staging
ON CONFLICT (licence_no) DO UPDATE SET
  company_name=EXCLUDED.company_name, latitude=EXCLUDED.latitude,
  longitude=EXCLUDED.longitude, surface_location=EXCLUDED.surface_location,
  category_type=EXCLUDED.category_type, rating_level=EXCLUDED.rating_level,
  status=EXCLUDED.status, status_date=EXCLUDED.status_date,
  non_routine=EXCLUDED.non_routine, non_routine_status=EXCLUDED.non_routine_status,
  raw_file_id=EXCLUDED.raw_file_id, updated_at=CURRENT_TIMESTAMP
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path, source: str = "well_licences") -> int:
    checksum = sha256(path)
    with psycopg.connect(DSN) as conn:
        row = conn.execute(
            "INSERT INTO raw_files (source, filename, checksum) VALUES (%s,%s,%s) "
            "ON CONFLICT (source, checksum) DO NOTHING RETURNING id",
            (source, path.name, checksum),
        ).fetchone()
        if row is None:
            print("File already processed")
            return 0
        raw_id = row[0]
        had_data = conn.execute("SELECT EXISTS (SELECT 1 FROM licences)").fetchone()[0]

        conn.execute("CREATE TEMP TABLE staging (LIKE licences) ON COMMIT DROP")
        total = 0
        with conn.cursor() as cur:
            with cur.copy(f"COPY staging ({COLS}) FROM STDIN") as cp:
                for l in parse_licences(path):
                    cp.write_row((l.licence_no, l.company_name, l.latitude,
                                  l.longitude, l.surface_location, l.category_type,
                                  l.rating_level, l.status, l.status_date,
                                  l.non_routine, l.non_routine_status, raw_id))
                    total += 1

        if had_data:
            for name, sql in EVENTS:
                n = conn.execute(sql).rowcount
                print(f"{name}: {n}")
        else:
            print("First load, no events emitted")

        conn.execute(UPSERT)
        print(f"Loaded {total} licences")
        return total


if __name__ == "__main__":
    load(Path(sys.argv[1]))

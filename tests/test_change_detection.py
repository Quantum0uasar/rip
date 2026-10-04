import os
from pathlib import Path

import psycopg
import pytest

from db import loader

TEST_DSN = os.environ.get("TEST_DSN", "postgresql://rip:rip@localhost:5432/rip_test")
SAMPLE = Path("tests/fixtures/licences_sample.csv")


@pytest.fixture
def db(monkeypatch):
    try:
        conn = psycopg.connect(TEST_DSN, autocommit=True)
    except psycopg.OperationalError:
        pytest.skip("test database not available")
    conn.execute("DROP TABLE IF EXISTS licence_events, licences, raw_files CASCADE")
    conn.execute(Path("db/schema.sql").read_text())
    monkeypatch.setattr(loader, "DSN", TEST_DSN)
    yield conn
    conn.close()


def count(db, table):
    return db.execute(f"select count(*) from {table}").fetchone()[0]


def test_first_load_emits_no_events(db):
    assert loader.load(SAMPLE) == 50
    assert count(db, "licences") == 50
    assert count(db, "licence_events") == 0


def test_same_file_is_skipped(db):
    loader.load(SAMPLE)
    assert loader.load(SAMPLE) == 0
    assert count(db, "raw_files") == 1


def test_detects_all_three_event_types(db, tmp_path):
    loader.load(SAMPLE)
    lines = SAMPLE.read_text().splitlines()
    lines[1] = lines[1].replace("Abandoned", "Cancelled")
    lines[2] = lines[2].replace("439 Oil Corp.(A098)", "Test Energy Ltd.(T001)")
    lines.append("W 9999999,Test Energy Ltd.(T001),51.0,-114.0,01-01-001-01W4,140,J,Issued,01 Oct 2026,N,")
    changed = tmp_path / "changed.csv"
    changed.write_text("\n".join(lines) + "\n")

    loader.load(changed)

    events = dict(db.execute(
        "select event_type, count(*) from licence_events group by 1").fetchall())
    assert events == {"new_licence": 1, "status_change": 1, "operator_change": 1}

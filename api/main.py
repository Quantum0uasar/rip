from datetime import timezone
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles

DSN = "postgresql://rip:rip@localhost:5432/rip"
app = FastAPI(title="RIP API")


def run(sql, params=()):
    with psycopg.connect(DSN, row_factory=dict_row) as conn:
        return conn.execute(sql, params).fetchall()


@app.get("/api/stats")
def stats():
    total = run("SELECT count(*) AS n FROM licences")[0]["n"]
    events = run("SELECT count(*) AS n FROM licence_events")[0]["n"]
    last = run("SELECT max(download_date) AS d FROM raw_files")[0]["d"]
    by_status = run("SELECT status, count(*) AS n FROM licences GROUP BY 1 ORDER BY 2 DESC")
    return {
        "licences": total,
        "events": events,
        "last_load": last.replace(tzinfo=timezone.utc).isoformat() if last else None,
        "by_status": by_status,
    }


@app.get("/api/licences")
def licences(q: str = "", status: str = "",
             limit: int = Query(25, le=100), offset: int = 0):
    where, params = [], []
    if q:
        where.append("(company_name ILIKE %s OR licence_no ILIKE %s OR surface_location ILIKE %s)")
        params += [f"%{q}%"] * 3
    if status:
        where.append("lower(status) = lower(%s)")
        params.append(status)
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    total = run(f"SELECT count(*) AS n FROM licences {clause}", params)[0]["n"]
    rows = run(
        f"""SELECT licence_no, company_name, surface_location, status, status_date,
                   category_type, rating_level
            FROM licences {clause}
            ORDER BY status_date DESC NULLS LAST, licence_no
            LIMIT %s OFFSET %s""",
        params + [limit, offset],
    )
    return {"total": total, "rows": rows}


@app.get("/api/events")
def events(type: str = "", limit: int = Query(50, le=200)):
    params, clause = [], ""
    if type:
        clause = "WHERE e.event_type = %s"
        params.append(type)
    rows = run(
        f"""SELECT e.id, e.licence_no, e.event_type, e.old_value, e.new_value,
                   e.detected_at, l.company_name
            FROM licence_events e
            LEFT JOIN licences l ON l.licence_no = e.licence_no
            {clause}
            ORDER BY e.id DESC LIMIT %s""",
        params + [limit],
    )
    for r in rows:
        r["detected_at"] = r["detected_at"].replace(tzinfo=timezone.utc).isoformat()
    return {"rows": rows}


app.mount("/", StaticFiles(directory="web", html=True), name="web")

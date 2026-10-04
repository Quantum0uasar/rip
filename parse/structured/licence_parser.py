import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional
from pydantic import BaseModel


class Licence(BaseModel):
    licence_no: str
    company_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    surface_location: Optional[str] = None
    category_type: Optional[str] = None
    rating_level: Optional[str] = None
    status: Optional[str] = None
    status_date: Optional[datetime] = None
    non_routine: Optional[bool] = None
    non_routine_status: Optional[str] = None


def _clean(header: str) -> str:
    return re.sub(r"^\d+\.", "", header).strip()


def _num(v: str) -> Optional[float]:
    return float(v) if v and v.strip() else None


def _date(v: str):
    return datetime.strptime(v.strip(), "%d %b %Y") if v and v.strip() else None


def parse_licences(path: Path) -> Iterator[Licence]:
    bad = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        headers = [_clean(h) for h in next(reader)]
        for values in reader:
            row = dict(zip(headers, values))
            try:
                yield Licence(
                    licence_no=row["Licence Number"].strip(),
                    company_name=row.get("Company Name") or None,
                    latitude=_num(row.get("Latitude", "")),
                    longitude=_num(row.get("Longitude", "")),
                    surface_location=row.get("Surface Location") or None,
                    category_type=row.get("Energy Development Category Type") or None,
                    rating_level=row.get("Rating Level") or None,
                    status=row.get("Licence Status") or None,
                    status_date=_date(row.get("Licence Status Date", "")),
                    non_routine=(row.get("Non-Routine Licence (Y or N)") == "Y"),
                    non_routine_status=row.get("Non-Routine Status") or None,
                )
            except Exception as e:
                bad += 1
                print(f"Bad row skipped: {e}")
    print(f"Skipped {bad} bad rows")

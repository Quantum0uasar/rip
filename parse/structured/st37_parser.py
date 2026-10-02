import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WellLicence(BaseModel):
    licence_no: str
    status: str
    uwi: str
    well_name: str
    operator: str
    licence_date: datetime
    spud_date: Optional[datetime] = None
    rig_release_date: Optional[datetime] = None
    well_type: str
    field: str
    pool: str
    latitude: float
    longitude: float
    ground_elevation: float
    kb_elevation: float
    td_depth: float
    td_formation: str

def parse_st37(filepath: Path) -> List[WellLicence]:
    """Parse the ST37 well licence CSV file"""
    df = pd.read_csv(filepath)
    
    # Convert date columns
    date_columns = ['Licence Date', 'Spud Date', 'Rig Release Date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Convert to WellLicence objects
    well_licences = []
    for _, row in df.iterrows():
        try:
            licence = WellLicence(
                licence_no=str(row.get('Licence No', '')),
                status=str(row.get('Status', '')),
                uwi=str(row.get('UWI', '')),
                well_name=str(row.get('Well Name', '')),
                operator=str(row.get('Operator', '')),
                licence_date=row.get('Licence Date', datetime.now()),
                spud_date=row.get('Spud Date'),
                rig_release_date=row.get('Rig Release Date'),
                well_type=str(row.get('Well Type', '')),
                field=str(row.get('Field', '')),
                pool=str(row.get('Pool', '')),
                latitude=float(row.get('Latitude', 0)),
                longitude=float(row.get('Longitude', 0)),
                ground_elevation=float(row.get('Ground Elevation', 0)),
                kb_elevation=float(row.get('KB Elevation', 0)),
                td_depth=float(row.get('TD Depth', 0)),
                td_formation=str(row.get('TD Formation', ''))
            )
            well_licences.append(licence)
        except Exception as e:
            print(f"Error parsing row: {e}")
            continue
    
    return well_licences

if __name__ == "__main__":
    licences = parse_st37(Path("raw/st37/sample_well_licences.csv"))
    print(f"Parsed {len(licences)} well licences")
    for licence in licences[:3]:
        print(f"Licence {licence.licence_no}: {licence.well_name} ({licence.well_type})")

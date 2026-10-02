import psycopg2
from pathlib import Path
from parse.structured.st37_parser import parse_st37, WellLicence

def load_well_licences(filepath: Path, checksum: str) -> int:
    """Load well licences into the database"""
    # Parse the file
    licences = parse_st37(filepath)
    
    # Connect to database
    conn = psycopg2.connect(
        host="localhost",
        user="rip",
        password="rip",
        database="rip"
    )
    cursor = conn.cursor()
    
    # Insert raw file record
    cursor.execute("""
        INSERT INTO raw_files (source, filename, checksum)
        VALUES (%s, %s, %s)
        ON CONFLICT (source, checksum) DO NOTHING
        RETURNING id
    """, ("st37", filepath.name, checksum))
    
    result = cursor.fetchone()
    if result:
        raw_file_id = result[0]
        
        # Insert well licences
        for licence in licences:
            cursor.execute("""
                INSERT INTO wells (
                    licence_no, status, uwi, well_name, operator,
                    licence_date, spud_date, rig_release_date, well_type,
                    field, pool, latitude, longitude, ground_elevation,
                    kb_elevation, td_depth, td_formation, raw_file_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (licence_no) DO UPDATE
                SET status = EXCLUDED.status,
                    uwi = EXCLUDED.uwi,
                    well_name = EXCLUDED.well_name,
                    operator = EXCLUDED.operator,
                    spud_date = EXCLUDED.spud_date,
                    rig_release_date = EXCLUDED.rig_release_date,
                    well_type = EXCLUDED.well_type,
                    field = EXCLUDED.field,
                    pool = EXCLUDED.pool,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    ground_elevation = EXCLUDED.ground_elevation,
                    kb_elevation = EXCLUDED.kb_elevation,
                    td_depth = EXCLUDED.td_depth,
                    td_formation = EXCLUDED.td_formation,
                    raw_file_id = EXCLUDED.raw_file_id,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                licence.licence_no, licence.status, licence.uwi, licence.well_name,
                licence.operator, licence.licence_date, licence.spud_date,
                licence.rig_release_date, licence.well_type, licence.field,
                licence.pool, licence.latitude, licence.longitude,
                licence.ground_elevation, licence.kb_elevation,
                licence.td_depth, licence.td_formation, raw_file_id
            ))
        
        conn.commit()
        print(f"Loaded {len(licences)} well licences into database")
    else:
        print("File already processed")
    
    conn.close()
    return len(licences) if result else 0

if __name__ == "__main__":
    from pathlib import Path
    filepath = Path("raw/st37/sample_well_licences.csv")
    checksum = "sample_checksum"
    count = load_well_licences(filepath, checksum)
    print(f"Processed {count} records")

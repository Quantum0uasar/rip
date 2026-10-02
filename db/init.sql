-- Raw files table
CREATE TABLE IF NOT EXISTS raw_files (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, checksum)
);

-- Wells table
CREATE TABLE IF NOT EXISTS wells (
    id SERIAL PRIMARY KEY,
    licence_no VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(10) NOT NULL,
    uwi VARCHAR(50) NOT NULL,
    well_name VARCHAR(255) NOT NULL,
    operator VARCHAR(255) NOT NULL,
    licence_date DATE NOT NULL,
    spud_date DATE,
    rig_release_date DATE,
    well_type VARCHAR(50) NOT NULL,
    field VARCHAR(255) NOT NULL,
    pool VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    ground_elevation DECIMAL(10, 2) NOT NULL,
    kb_elevation DECIMAL(10, 2) NOT NULL,
    td_depth DECIMAL(10, 2) NOT NULL,
    td_formation VARCHAR(255) NOT NULL,
    raw_file_id INTEGER REFERENCES raw_files(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

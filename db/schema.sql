DROP TABLE IF EXISTS wells;
CREATE TABLE IF NOT EXISTS raw_files (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, checksum)
);
CREATE TABLE IF NOT EXISTS licences (
    licence_no TEXT PRIMARY KEY,
    company_name TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    surface_location TEXT,
    category_type TEXT,
    rating_level TEXT,
    status TEXT,
    status_date DATE,
    non_routine BOOLEAN,
    non_routine_status TEXT,
    raw_file_id INTEGER REFERENCES raw_files(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS licence_events (
    id SERIAL PRIMARY KEY,
    licence_no TEXT NOT NULL,
    event_type TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    raw_file_id INTEGER REFERENCES raw_files(id),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_lic_company ON licences USING gin (company_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_lic_no ON licences USING gin (licence_no gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_lic_loc ON licences USING gin (surface_location gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_lic_status ON licences (lower(status));
CREATE INDEX IF NOT EXISTS idx_lic_sort ON licences (status_date DESC NULLS LAST, licence_no);

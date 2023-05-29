
CREATE TABLE scan
(
    scan_id SERIAL PRIMARY KEY,
    fullpath VARCHAR(512) NOT NULL,
    provider VARCHAR(512) NOT NULL,
    patient_id VARCHAR(64),
    health_status VARCHAR(3),
    axis jsonb NOT NULL,
    rotation jsonb NOT NULL
);


CREATE TABLE scan_features
(
    feature_id SERIAL PRIMARY KEY,
    scan_id INTEGER,
    features jsonb
);




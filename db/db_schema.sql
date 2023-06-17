
CREATE TABLE scan
(
    scan_id SERIAL PRIMARY KEY,
    fullpath VARCHAR(512) NOT NULL,
    days int NOT NULL,
    patiend_id VARCHAR(512) NOT NULL,
    origin VARCHAR(512) NOT NULL, -- oasis2, oasis3, adni etc
    skipit int default 0, -- if 1 then it should be skipped for training.
    health_status int default 0,  -- 0: healthy, 1: Mild 2: Demented
    axis jsonb NOT NULL,
    rotation jsonb NOT NULL,
    UNIQUE(fullpath)
);


CREATE TABLE diagnosis
(
    diagnosis_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(512) NOT NULL,
    days int NOT NULL,
    origin VARCHAR(512) NOT NULL, -- oasis2, oasis3, adni etc
    health_status int default 0,  -- 0: healthy, 1: Mild 2: Demented
    UNIQUE(patient_id, days)
);

-- stores VGG16 generated feautures
CREATE TABLE scan_features
(
    feature_id SERIAL PRIMARY KEY,
    scan_id INTEGER,
    features_slice11 jsonb,
    features_slice12 jsonb,
    features_slice13 jsonb,
    features_slice21 jsonb,
    features_slice22 jsonb,
    features_slice23 jsonb,
    features_slice31 jsonb,
    features_slice32 jsonb,
    features_slice33 jsonb,
    UNIQUE(scan_id)
);


\COPY diagnosis   (patient_id, days, origin, health_status)  FROM '/home/john/repos/cogni_scan/db/oasis3_diagnosis.csv' DELIMITER ',' CSV HEADER;


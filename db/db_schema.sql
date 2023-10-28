CREATE TABLE scan
(
    scan_id       SERIAL PRIMARY KEY,
    patient_id    VARCHAR(512) NOT NULL,
    fullpath      VARCHAR(512) NOT NULL,
    days          int NOT NULL,
    health_status int NOT NULL,       -- 0: healthy, 1: Mild 2: Demented
    origin        VARCHAR(512) NOT NULL, -- oasis2, oasis3, adni etc
    axis          jsonb default '{"0": 0, "1": 1, "2": 2}' NOT NULL,
    rotation      jsonb default '[0, 0, 0]' NOT NULL,
    sd0           FLOAT default 0.2,     -- Slice Distance for first axis.
    sd1           FLOAT default 0.2,     -- Slice Distance for middle axis.
    sd2           FLOAT default 0.2,     -- Slice Distance for third axis.
    validation_status  int   default 0,       -- 0: undefined, 1: invalid,  2: valid
    UNIQUE (fullpath)
);

\COPY scan (fullpath,days,patient_id,origin,health_status,axis,rotation,sd0,sd1,sd2,validation_status ) FROM '/home/john/repos/cogni_scan/db/scan.csv' DELIMITER ',' CSV HEADER;


CREATE TABLE patient
(
    patient_id VARCHAR(512) PRIMARY KEY,
    label      VARCHAR(2) NOT NULL
);

CREATE TABLE diagnosis
(
    diagnosis_id  SERIAL PRIMARY KEY,
    patient_id    VARCHAR(512) NOT NULL,
    days          int          NOT NULL,
    origin        VARCHAR(512) NOT NULL, -- oasis2, oasis3, adni etc
    health_status int default 0,         -- 0: healthy, 1: Mild 2: Demented
    UNIQUE (patient_id, days)
);



\COPY diagnosis (patient_id, days, origin, health_status) FROM '/home/john/repos/cogni_scan/db/oasis3_diagnosis.csv' DELIMITER ',' CSV HEADER;

-- stores VGG16 generated feautures
CREATE TABLE scan_features
(
    feature_id       SERIAL PRIMARY KEY,
    scan_id          INTEGER,
    distance_0 FLOAT,
    distance_1 FLOAT,
    distance_2 FLOAT,
    features_slice01 jsonb,
    features_slice02 jsonb,
    features_slice03 jsonb,
    features_slice11 jsonb,
    features_slice12 jsonb,
    features_slice13 jsonb,
    features_slice21 jsonb,
    features_slice22 jsonb,
    features_slice23 jsonb,
    patient_id VARCHAR(512),
    label VARCHAR(2),
    UNIQUE (scan_id)
);

create table datasets
(
    dataset_id uuid primary key,
    description VARCHAR(2048),
    training_scan_ids jsonb,
    validation_scan_ids jsonb,
    testing_scan_ids jsonb,
    created_at TIMESTAMP default NOW()
);


create table models
(
    model_id uuid PRIMARY KEY,
    model_name VARCHAR(128),
    dataset_id uuid,
    slices jsonb,
    descriptive_data jsonb,
    created_at TIMESTAMP default NOW()
);

-- To back the database:

--  create database backupscans with template scans;


-- \copy (SELECT * FROM scan_features) TO '/home/john/nifti-samples/scan_features.csv' DELIMITER ',' CSV HEADER;
-- \copy (SELECT * FROM datasets) TO '/home/john/nifti-samples/datasets.csv' DELIMITER ',' CSV HEADER;
-- \copy models TO '/home/john/models.csv' DELIMITER ',' CSV HEADER;

-- \copy (SELECT fullpath,days,patient_id,origin,health_status,axis,rotation,sd0,sd1,sd2,validation_status  FROM scan) TO '/home/john/repos/cogni_scan/db/scan.csv' DELIMITER ',' CSV HEADER;
-- \copy (SELECT * FROM diagnosis) TO '/diagnosis.csv' DELIMITER ',' CSV HEADER;
-- \copy (SELECT * FROM patient) TO '/patient.csv' DELIMITER ',' CSV HEADER;
-- \copy (SELECT fullpath, validation_status FROM scan) TO '/cogni_scan/db/validation_status.csv' DELIMITER ',' CSV HEADER;

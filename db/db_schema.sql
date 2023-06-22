CREATE TABLE scan
(
    scan_id       SERIAL PRIMARY KEY,
    fullpath      VARCHAR(512) NOT NULL,
    days          int          NOT NULL,
    patiend_id    VARCHAR(512) NOT NULL,
    origin        VARCHAR(512) NOT NULL, -- oasis2, oasis3, adni etc
    skipit        int   default 0,       -- if 1 then it should be skipped for training.
    health_status int   default 0,       -- 0: healthy, 1: Mild 2: Demented
    axis          jsonb        NOT NULL,
    rotation      jsonb        NOT NULL,
    sd0           FLOAT default 0.2,     -- Slice Distance for first axis.
    sd1           FLOAT default 0.2,     -- Slice Distance for middle axis.
    sd2           FLOAT default 0.2,     -- Slice Distance for third axis.
    validation_status  int   default 0,       -- 0: undefined, 1: invalid,  2: valid
    UNIQUE (fullpath)
);

-- update scan set skipit=1 where fullpath like ('%TSE%');

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
    dataset_id serial primary key,
    name VARCHAR(512),
    created_at TIMESTAMP,
    training_scan_ids jsonb,
    validation_scan_ids jsonb,
    testing_scan_ids jsonb,
    UNIQUE (name)
);

\COPY diagnosis (patient_id, days, origin, health_status) FROM '/home/john/repos/cogni_scan/db/oasis3_diagnosis.csv' DELIMITER ',' CSV HEADER;


-- To back the database:
-- \copy (SELECT * FROM scan) TO '/home/john/repos/cogni_scan/db/scan.csv' DELIMITER ',' CSV HEADER;
-- \copy (SELECT * FROM diagnosis) TO '/home/john/repos/cogni_scan/db/diagnosis.csv' DELIMITER ',' CSV HEADER;
-- \copy (SELECT * FROM patient) TO '/home/john/repos/cogni_scan/db/patient.csv' DELIMITER ',' CSV HEADER;
-- \copy (SELECT skipit, is_valid FROM scan) TO '/home/john/repos/cogni_scan/db/valids.csv' DELIMITER ',' CSV HEADER;

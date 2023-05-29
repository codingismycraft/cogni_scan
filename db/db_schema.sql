
CREATE TABLE scan
(
    scan_id SERIAL PRIMARY KEY,
    fullpath VARCHAR(512) NOT NULL,
    axis jsonb NOT NULL,
    rotation jsonb NOT NULL,
    UNIQUE(fullpath)
);


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



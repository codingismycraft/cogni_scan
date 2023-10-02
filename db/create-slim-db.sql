--------------------------------------------------------------------------------
--
-- Creates a slim version of the db meant to be used only inside docker.
--
-- The models.csv should already be copied to the docker container so it will
-- be imported to the database.  Each model is identified by its model_id and 
-- its weights must be placed under the ~/.cogni_scan directory.
--
--------------------------------------------------------------------------------

create table models
(
    model_id uuid PRIMARY KEY,
    dataset_id uuid,
    slices jsonb,
    descriptive_data jsonb,
    created_at TIMESTAMP default NOW()
);


-- \COPY models FROM '/models.csv' DELIMITER ',' CSV HEADER;

-- To back the database:
-- \copy models TO '/home/john/models.csv' DELIMITER ',' CSV HEADER;


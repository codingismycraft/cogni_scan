#!/usr/bin/bash

# Get the models from the storage site.
wget https://neuproscan-storage.us-east-1.linodeobjects.com/models.csv 

# Copy it to the docker instance of psql.
docker cp models.csv mydb:/models.csv

# Create a slim version of the db holding only models.
docker cp create-slim-db.sql mydb:/create-slim-db.sql
docker exec mydb dropdb -U postgres scans
docker exec mydb createdb -U postgres scans
docker exec mydb psql -U postgres scans -f create-slim-db.sql

# Synchronize the weights if needed
./sync_model_weights.py

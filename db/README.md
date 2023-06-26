### Summary
The scripts in this directory are used to create the database used for the
cogni_scan application.

### Instructions
To create a database, follow the steps below:

1. Run the `create_db.sh` script. This script hard-codes the name of the
   database that will be created.

```
./create_db.sh
```

The common database names used are:

- scans (for production)
- dummyscans (for testing)

Note: The `create_db.sh` script creates the database, schema, and populates it
with the Oasis3 data.

2. After running the `create_db.sh` script, the `validation_status` that is
   created may not be the most up to date. To ensure you have the most current
   data, you should consider exporting them by running the following command:

```
\copy (SELECT fullpath, days, patient_id, origin, health_status, axis, rotation, sd0, sd1, sd2, validation_status FROM scan) TO './cogni_scan/db/scan.csv' DELIMITER ',' CSV HEADER;
```

This command exports the data to a CSV file named `scan.csv` located in the `./cogni_scan/db/ directory.`

### Saving the VGG16 Features

To bring the database up to date with the valid scans is to spawn the related
process from the CogniScan front end.  This process will automatically discover
all the valid scans that are missing VGG16 features.  The process will
calculate and save the missing VGG16 features automatically.

### Datasets

To create a dataset that will be used for model creation (having training, 
validation, and testing data) you should run the `create_dataset.py` passing 
the name of the database you need to use.
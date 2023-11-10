# Detecting Dementia

In this directory we develop a model to detect (not predict) dementia from
Nifti files.

we use the OASIS3 files which must already be pre-processed and having their
metadata stored in the postgres database.


### The applicable datasets

The table to use is scan and the important fields are health_status, 
validation_status and fullpath. 

See the following for the possible values that these fields might take:

### health_status
- 0: healthy
- 1: Mild 
- 2: Demented

### validation_status
- 0: undefined
- 1: invalid
- 2: valid

Using the above mentioned data we can find out the available scans:

```
Select health_status, count(*) from scan 
where validation_status = 2 group by health_status
```


| Status   | Count |
|----------|-------|
| Healthy  | 3650  |
| Mild     | 295   |
| Demented | 651   |


To avoid data leaks as much as possible we will not reuse the patient more
than once in the same dataset.


### Finding Demented Scans

The number of unique patients that are not healthy can be found using the 
following query:

```
select count(*) from (select distinct patient_id
                      from scan
                      where validation_status = 2
                        and (health_status = 1 or health_status = 2)) as junk
```

which is 350

### Finding healthy Scans

For the healthy patients we will do the same but we will also exclude those 
who changed from healthy to demented (to avoid data leaks again):


```
select count(*) from (select distinct patient_id
                      from scan
                      where validation_status = 2
                        and health_status = 0
                        and patient_id not in (select patient_id
                                               from scan
                                               where validation_status = 2
                                                 and (health_status = 1 or health_status = 2))) as junk

```

which is 702

### Picking the MRIs

We will use exaclty one MRI from each of the unique subjects (as they are
defined above).  

This MRI will be selected randomly: Since a subject might have multiple MRIs
we will pick a random one for each of them.

### Training the model

The model will be trained using the same exact pre-calculated features that 
are using VGG16 for knowledge transfering and are stored in the database (the
same pre-calculated features are used for all the other models as well).



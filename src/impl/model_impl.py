import cogni_scan.src.dbutil as dbutil
import cogni_scan.src.impl.dataset_impl as dataset_impl

_SQL_LOAD_DATASETS = """
Select 
    name, created_at, training_scan_ids, validation_scan_ids, testing_scan_ids 
from datasets 
"""


def getDatasets():
    """Returns a list of all the databases from the database."""
    Dateaset = dataset_impl.Dataset
    dbo = dbutil.SimpleSQL()
    with dbo as db:
        return [Dateaset(*row) for row in db.execute_query(_SQL_LOAD_DATASETS)]


if __name__ == '__main__':
    for ds in getDatasets():
        print(ds)
        for k, v in ds.getStats().items():
            print(k, v)
        print(ds.getFeatures(['01']))
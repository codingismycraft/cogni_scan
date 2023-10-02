#!/usr/bin/env python3
"""Downloads the models weights from the external storage."""

import os

import cogni_scan.src.dbutil as dbutil

_SQL_SELECT_MODELS = "select model_id from models;"
_WEIGHTS_DIR = "/home/vagrant/.cogni_scan"

def weights_already_available(model_id):
    if not os.path.isdir(_WEIGHTS_DIR):
        return False
    filename = os.path.join(_WEIGHTS_DIR, f"{model_id}.h5")
    return os.path.exists(filename)

def download_weights(model_id):
    if not os.path.isdir(_WEIGHTS_DIR):
        os.makedirs(_WEIGHTS_DIR)

    filename = os.path.join(_WEIGHTS_DIR, f"{model_id}.h5")
    url = f"https://neuproscan-storage.us-east-1.linodeobjects.com/{model_id}.h5"
    print(f"Downloading weights for {model_id}")
    os.system(f"wget {url}")
    os.system(f"mv {model_id}.h5 {_WEIGHTS_DIR}")
    os.system(f"rm {model_id}.h5")
    print(f"Done with {model_id}")

def main():
    with dbutil.SimpleSQL() as db:
        for row in db.execute_query(_SQL_SELECT_MODELS):
            model_id = row[0]
            if not weights_already_available(model_id):
                download_weights(model_id)
            else:
                print(f"{model_id} already exists.")


if __name__ == '__main__':
    main()

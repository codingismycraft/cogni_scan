"""Exports the models details to files that can be uploaded to Sibyl."""

import os
import pathlib
import json

import cogni_scan.src.modeler.model as model

_OUTPUT_FILE = "models-info.json"
_REMOTE_USER = "root"
_REMOTE_IP = "88.80.184.217"
_REMOTE_DRIVE = "/mnt/sibyl_drive"
_SCP_CMD = "rsync -v {files} {remote_user}@{remote_ip}:{remote_drive}"


def main(sync_files):
    filepaths = [_OUTPUT_FILE]
    with open(_OUTPUT_FILE, 'w') as fout:
        info = model.getAllModelsAsJson()
        for m in info["models"]:
            filepaths.append(m["weights_path"])
            del m["weights_path"]
        fout.write(json.dumps(info, indent=4))
    files = ' '.join(filepaths)

    if sync_files:
        cmd = _SCP_CMD.format(
            files=files,
            remote_user=_REMOTE_USER,
            remote_ip=_REMOTE_IP,
            remote_drive=_REMOTE_DRIVE
        )
        print(cmd)
        os.system(cmd)

        # Move the models-info.json under the well known ~/.cogni_scan directory.
        home_dir = pathlib.Path.home()
        dest = os.path.join(home_dir, '.cogni_scan', _OUTPUT_FILE)
        cmd = f'mv {_OUTPUT_FILE} {dest}'
        print(cmd)
        os.system(cmd)


if __name__ == '__main__':
    main(True)

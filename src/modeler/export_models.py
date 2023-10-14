"""Exports the models details to files that can be uploaded to Sibyl."""

import os
import json

import cogni_scan.src.modeler.model as model

_OUTPUT_FILE = "models-info.json"
_REMOTE_USER = "root"
_REMOTE_IP = "88.80.184.217"
_REMOTE_DRIVE = "/mnt/sibyl_drive"
_SCP_CMD = "rsync -v {files} {remote_user}@{remote_ip}:{remote_drive}"


def main():
    filepaths = [_OUTPUT_FILE]
    with open(_OUTPUT_FILE, 'w') as fout:
        info = model.getAllModelsAsJson()
        for m in info["models"]:
            filepaths.append(m["weights_path"])
            del m["weights_path"]
        fout.write(json.dumps(info, indent=4))
    files = ' '.join(filepaths)
    cmd = _SCP_CMD.format(
        files=files,
        remote_user=_REMOTE_USER,
        remote_ip=_REMOTE_IP,
        remote_drive=_REMOTE_DRIVE
    )
    os.system(cmd)


if __name__ == '__main__':
    main()

import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
COGNI_DB = os.path.join(CURRENT_DIR, "cogni.db")

# Flags for the validation status of a scan.
UNDEFINED_SCAN = 0 # Not assigned yet.
INVALID_SCAN = 1 # Scan is invalid (does not contain enough information).
VALID_SCAN = 2 # Scan is valid (can be used for modeling)
ALL_SCANS = -1

filename = "/src/impl/tests/testing_data"

DIR_TESTING_DATA = os.path.join(
    CURRENT_DIR, "src", "impl", "tests", "testing_data"
)

import os

# give every pytest-xdist worker its own database,
# otherwise parallel workers flush and drop each other's data
xdist_worker = os.environ.get("PYTEST_XDIST_WORKER")
if xdist_worker:
    original_db_name = os.environ.get("DB_NAME", "test")
    os.environ["DB_NAME"] = "{}_{}".format(original_db_name, xdist_worker)

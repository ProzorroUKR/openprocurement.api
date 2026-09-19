import os

# tests run against a single-node replica set: w=1 without waiting for the journal
# and local reads give the same visibility as majority, but every write is faster
os.environ.setdefault("WRITE_CONCERN", "1")
os.environ.setdefault("READ_CONCERN", "local")

# give every pytest-xdist worker its own database,
# otherwise parallel workers flush and drop each other's data
xdist_worker = os.environ.get("PYTEST_XDIST_WORKER")
if xdist_worker:
    original_db_name = os.environ.get("DB_NAME", "test")
    os.environ["DB_NAME"] = "{}_{}".format(original_db_name, xdist_worker)

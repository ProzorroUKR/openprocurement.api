# -*- coding: utf-8 -*-
import logging

LOGGER = logging.getLogger(__name__)
SCHEMA_VERSION = 1
SCHEMA_DOC = "openprocurement_frameworks_schema"


def get_db_schema_version(db):
    schema_doc = db.get(SCHEMA_DOC, {"_id": SCHEMA_DOC})
    return schema_doc.get("version", SCHEMA_VERSION - 1)


def set_db_schema_version(db, version):
    schema_doc = db.get(SCHEMA_DOC, {"_id": SCHEMA_DOC})
    schema_doc["version"] = version
    db.save(schema_doc)


def migrate_data(registry, destination=None):
    cur_version = get_db_schema_version(registry.databases.migrations)
    if cur_version == SCHEMA_VERSION:
        return cur_version
    for step in range(cur_version, destination or SCHEMA_VERSION):
        LOGGER.info(
            "Migrate openprocurement schema from {} to {}".format(step, step + 1), extra={"MESSAGE_ID": "migrate_data"}
        )
        migration_func = globals().get("from{}to{}".format(step, step + 1))
        if migration_func:
            migration_func(registry)
        set_db_schema_version(registry.databases.migrations, step + 1)

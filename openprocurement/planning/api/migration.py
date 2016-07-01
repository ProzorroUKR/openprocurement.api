# -*- coding: utf-8 -*-
import logging
from openprocurement.planning.api.traversal import Root
from openprocurement.planning.api.models import Plan

LOGGER = logging.getLogger(__name__)
SCHEMA_VERSION = 1
SCHEMA_DOC = 'openprocurement_plans_schema'


def get_db_schema_version(db):
    schema_doc = db.get(SCHEMA_DOC, {"_id": SCHEMA_DOC})
    return schema_doc.get("version", SCHEMA_VERSION - 1)


def set_db_schema_version(db, version):
    schema_doc = db.get(SCHEMA_DOC, {"_id": SCHEMA_DOC})
    schema_doc["version"] = version
    db.save(schema_doc)


def migrate_data(registry, destination=None):
    if registry.settings.get('plugins') and 'planning' not in registry.settings['plugins'].split(','):
        return
    cur_version = get_db_schema_version(registry.db)
    if cur_version == SCHEMA_VERSION:
        return cur_version
    for step in xrange(cur_version, destination or SCHEMA_VERSION):
        LOGGER.info("Migrate openprocurement plans schema from {} to {}".format(step, step + 1), extra={'MESSAGE_ID': 'migrate_data'})
        migration_func = globals().get('from{}to{}'.format(step, step + 1))
        if migration_func:
            migration_func(registry)
        set_db_schema_version(registry.db, step + 1)


def from0to1(registry):
    class Request(object):
        def __init__(self, registry):
            self.registry = registry
    results = registry.db.iterview('plans/all', 2 ** 10, include_docs=True)
    docs = []
    request = Request(registry)
    root = Root(request)
    for i in results:
        doc = i.doc
        if doc.get('documents'):
            plan = Plan(doc)
            plan.__parent__ = root
            doc = plan.to_primitive()
            docs.append(doc)
        if len(docs) >= 2 ** 7:
            registry.db.update(docs)
            docs = []
    if docs:
        registry.db.update(docs)

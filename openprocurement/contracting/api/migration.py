# -*- coding: utf-8 -*-
import logging
from openprocurement.api.models import get_now
from openprocurement.contracting.api.traversal import Root
from openprocurement.contracting.api.models import Contract

LOGGER = logging.getLogger(__name__)
SCHEMA_VERSION = 2
SCHEMA_DOC = 'openprocurement_contracts_schema'


def get_db_schema_version(db):
    schema_doc = db.get(SCHEMA_DOC, {"_id": SCHEMA_DOC})
    return schema_doc.get("version", SCHEMA_VERSION - 1)


def set_db_schema_version(db, version):
    schema_doc = db.get(SCHEMA_DOC, {"_id": SCHEMA_DOC})
    schema_doc["version"] = version
    db.save(schema_doc)


def migrate_data(registry, destination=None):
    if registry.settings.get('plugins') and 'contracting' not in registry.settings['plugins'].split(','):
        return
    cur_version = get_db_schema_version(registry.db)
    if cur_version == SCHEMA_VERSION:
        return cur_version
    for step in xrange(cur_version, destination or SCHEMA_VERSION):
        LOGGER.info("Migrate openprocurement contracts schema from {} to {}".format(step, step + 1), extra={'MESSAGE_ID': 'migrate_data'})
        migration_func = globals().get('from{}to{}'.format(step, step + 1))
        if migration_func:
            migration_func(registry)
        set_db_schema_version(registry.db, step + 1)


def from0to1(registry):
    LOGGER.info("Start contracts migration.", extra={'MESSAGE_ID': 'migrate_data'})
    results = registry.db.iterview('contracts/all', 2 ** 10, include_docs=True)
    docs = []
    for i in results:
        doc = i.doc

        if "suppliers" not in doc:
            tender_id = doc['tender_id']
            rel_award = doc['awardID']
            tender_doc = registry.db.get(tender_id)

            rel_award = [aw for aw in tender_doc['awards'] if aw['id'] == doc['awardID']]
            if not rel_award:
                LOGGER.warn("Related award {} for contract {} not found!".format(doc['awardID'], doc['id']), extra={'MESSAGE_ID': 'migrate_data'})
                continue
            rel_award = rel_award[0]

            doc['suppliers'] = rel_award['suppliers']
            if "value" not in doc:
                doc['value'] = rel_award['value']

            doc['dateModified'] = get_now().isoformat()

            docs.append(doc)
        if len(docs) >= 2 ** 7:
            registry.db.update(docs)
            docs = []
    if docs:
        registry.db.update(docs)
    LOGGER.info("Contracts migration is finished.", extra={'MESSAGE_ID': 'migrate_data'})


def from1to2(registry):
    class Request(object):
        def __init__(self, registry):
            self.registry = registry
    len(registry.db.view('contracts/all', limit=1))
    results = registry.db.iterview('contracts/all', 2 ** 10, include_docs=True, stale='update_after')
    docs = []
    request = Request(registry)
    root = Root(request)
    for i in results:
        doc = i.doc
        if not all([i.get('url', '').startswith(registry.docservice_url) for i in doc.get('documents', [])]):
            contract = Contract(doc)
            contract.__parent__ = root
            doc = contract.to_primitive()
            doc['dateModified'] = get_now().isoformat()
            docs.append(doc)
        if len(docs) >= 2 ** 7:
            registry.db.update(docs)
            docs = []
    if docs:
        registry.db.update(docs)

import math
from argparse import Namespace
from copy import deepcopy

import pytest
from pymongo.errors import BulkWriteError
from pyramid.scripting import prepare

from openprocurement.api.migrations.base import CollectionMigration
from openprocurement.api.tests.base import (  # pylint: disable=unused-import
    app,
    singleton_app,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_config,
    test_tender_below_data,
)
from openprocurement.tender.cfaselectionua.tests.base import (
    test_tender_cfaselectionua_config,
)
from openprocurement.tender.cfaselectionua.tests.tender import (
    test_tender_cfaselectionua_data,
)
from openprocurement.tender.cfaua.tests.base import (
    test_tender_cfaua_config,
    test_tender_cfaua_with_lots_data,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_cdeu_config,
    test_tender_cdeu_data,
    test_tender_cdua_config,
    test_tender_cdua_data,
)
from openprocurement.tender.esco.tests.base import (
    test_tender_esco_config,
    test_tender_esco_data,
)
from openprocurement.tender.limited.tests.base import (
    test_tender_negotiation_config,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_config,
    test_tender_negotiation_quick_data,
    test_tender_reporting_config,
    test_tender_reporting_data,
)
from openprocurement.tender.openeu.tests.base import (
    test_tender_openeu_config,
    test_tender_openeu_data,
)
from openprocurement.tender.openua.tests.base import (
    test_tender_openua_config,
    test_tender_openua_data,
)

test_tenders = [
    (test_tender_below_data, test_tender_below_config),
    (test_tender_cfaua_with_lots_data, test_tender_cfaua_config),
    (test_tender_cfaselectionua_data, test_tender_cfaselectionua_config),
    (test_tender_cdeu_data, test_tender_cdeu_config),
    (test_tender_cdua_data, test_tender_cdua_config),
    (test_tender_esco_data, test_tender_esco_config),
    (test_tender_reporting_data, test_tender_reporting_config),
    (test_tender_negotiation_data, test_tender_negotiation_config),
    (test_tender_negotiation_quick_data, test_tender_negotiation_quick_config),
    (test_tender_openeu_data, test_tender_openeu_config),
    (test_tender_openua_data, test_tender_openua_config),
]


@pytest.fixture(scope="function")
def migration_app(app):
    for test_tender_data, test_tender_config in test_tenders:
        app.authorization = ("Basic", ("broker", "broker"))

        test_tender_data = deepcopy(test_tender_data)
        test_tender_data["title"] = "original title"
        test_tender_data["title_en"] = "original title en"

        response = app.post_json("/tenders", {"data": test_tender_data, "config": test_tender_config})
        assert response.status == "201 Created"

        assert response.json["data"]["title"] == "original title"
        assert response.json["data"]["title_en"] == "original title en"

    collection = app.app.registry.mongodb.tenders.collection
    tenders = list(collection.find())
    assert len(tenders) == len(test_tenders)
    assert len(tenders) > 0

    yield app


def app_env(app):
    env = prepare(None, app.app.registry)
    env["app"] = app.app
    return env


default_test_args = Namespace(
    b=1000,
    log=False,
    test=False,
    readonly=False,
    filter=None,
)


class TestMigration(CollectionMigration):
    collection_name = "tenders"

    def update_document(self, doc: dict, context: dict = None) -> dict:
        doc["title"] = "test"
        return doc


def test_migration(migration_app):
    collection = migration_app.app.registry.mongodb.tenders.collection

    # Get not migrated data
    tenders_before = list(collection.find())

    for tender in tenders_before:
        assert len(tender["revisions"]) == 1

    # Mock bulk_write to track calls
    original_bulk_write = collection.bulk_write
    bulk_write_calls = []

    def mock_bulk_write(*args, **kwargs):
        bulk_write_calls.append((args, kwargs))
        return original_bulk_write(*args, **kwargs)

    collection.bulk_write = mock_bulk_write

    # Create migration
    migration = TestMigration(app_env(migration_app), default_test_args)
    migration.bulk_max_size = len(tenders_before)

    # Run migration
    migration.run()

    # Verify bulk_write was called exactly once
    assert len(bulk_write_calls) == 1

    # Get migrated data
    tenders = list(collection.find())

    # Verify migration results
    for i in range(len(tenders)):
        assert tenders[i]["_id"] == tenders_before[i]["_id"]
        assert tenders[i]["_rev"] != tenders_before[i]["_rev"]  # changed
        assert tenders[i]["title"] != tenders_before[i]["title"]  # changed
        assert tenders[i]["title_en"] == tenders_before[i]["title_en"]
        assert tenders[i]["dateModified"] == tenders_before[i]["dateModified"]
        assert tenders[i]["public_modified"] == tenders_before[i]["public_modified"]
        assert len(tenders[i]["revisions"]) == 2
        assert tenders[i]["revisions"][-1] == {
            'author': 'migration',
            'changes': [
                {
                    'op': 'replace',
                    'path': '/title',
                    'value': 'original title',
                }
            ],
            'date': tenders[i]["revisions"][-1]["date"],
            'rev': tenders_before[i]["_rev"],
        }

    # Restore original bulk_write
    collection.bulk_write = original_bulk_write


def test_migration_multiple_bulk_write(migration_app):
    collection = migration_app.app.registry.mongodb.tenders.collection

    # Get not migrated data
    tenders_before = list(collection.find())

    # Mock bulk_write to track calls
    original_bulk_write = collection.bulk_write
    bulk_write_calls = []

    def mock_bulk_write(*args, **kwargs):
        bulk_write_calls.append((args, kwargs))
        return original_bulk_write(*args, **kwargs)

    collection.bulk_write = mock_bulk_write

    # Create migration
    migration = TestMigration(app_env(migration_app), default_test_args)
    migration.bulk_max_size = math.ceil(len(tenders_before) / 2)

    # Run migration
    migration.run()

    # Verify bulk_write was called twice
    assert len(bulk_write_calls) == 2

    # Get migrated data
    tenders = list(collection.find())

    # Verify migration results
    for i in range(len(tenders)):
        assert tenders[i]["_id"] == tenders_before[i]["_id"]
        assert tenders[i]["_rev"] != tenders_before[i]["_rev"]  # changed
        assert tenders[i]["title"] != tenders_before[i]["title"]  # changed
        assert tenders[i]["title_en"] == tenders_before[i]["title_en"]
        assert tenders[i]["dateModified"] == tenders_before[i]["dateModified"]
        assert tenders[i]["public_modified"] == tenders_before[i]["public_modified"]

    # Restore original bulk_write
    collection.bulk_write = original_bulk_write


def test_migration_multiple_bulk_write_fail(migration_app):
    collection = migration_app.app.registry.mongodb.tenders.collection

    # Get not migrated data
    tenders_before = list(collection.find())

    # Mock bulk_write to track calls
    original_bulk_write = collection.bulk_write
    bulk_write_calls = []

    def mock_bulk_write(*args, **kwargs):
        bulk_write_calls.append((args, kwargs))
        if len(bulk_write_calls) == 1:
            raise BulkWriteError(
                results={
                    "n": 0,
                    "nModified": 0,
                    "ok": 0,
                    "writeErrors": [{"code": 11000, "errmsg": "test"}],
                }
            )
        return original_bulk_write(*args, **kwargs)

    collection.bulk_write = mock_bulk_write

    # Mock update_one to track calls
    original_update_one = collection.update_one
    update_one_calls = []

    def mock_update_one(*args, **kwargs):
        update_one_calls.append((args, kwargs))
        return original_update_one(*args, **kwargs)

    collection.update_one = mock_update_one

    # Create migration
    migration = TestMigration(app_env(migration_app), default_test_args)
    migration.bulk_max_size = math.ceil(len(tenders_before) / 2)

    # Run migration
    migration.run()

    # Verify bulk_write was called twice
    assert len(bulk_write_calls) == 2

    # Verify update_one was called for each document of failed batch
    assert len(update_one_calls) == migration.bulk_max_size

    # Get migrated data
    tenders = list(collection.find())

    # Verify migration results
    for i in range(len(tenders)):
        assert tenders[i]["_id"] == tenders_before[i]["_id"]
        assert tenders[i]["_rev"] != tenders_before[i]["_rev"]  # changed
        assert tenders[i]["title"] != tenders_before[i]["title"]  # changed
        assert tenders[i]["title_en"] == tenders_before[i]["title_en"]
        assert tenders[i]["dateModified"] == tenders_before[i]["dateModified"]
        assert tenders[i]["public_modified"] == tenders_before[i]["public_modified"]

    # Restore original bulk_write
    collection.bulk_write = original_bulk_write


def test_migration_with_filter(migration_app):
    collection = migration_app.app.registry.mongodb.tenders.collection

    # Get not migrated data
    tenders_before = list(collection.find())

    # Create migration class
    class Migration(TestMigration):
        def get_filter(self) -> dict:
            return {"procurementMethodType": "belowThreshold"}

    # Create migration
    migration = Migration(app_env(migration_app), default_test_args)

    # Run migration
    migration.run()

    # Get migrated data
    tenders = list(collection.find())

    # Verify migration results
    for i in range(len(tenders)):
        assert tenders[i]["_id"] == tenders_before[i]["_id"]
        if tenders[i]["procurementMethodType"] == "belowThreshold":
            assert tenders[i]["_rev"] != tenders_before[i]["_rev"]  # changed
            assert tenders[i]["title"] != tenders_before[i]["title"]  # changed
        else:
            assert tenders[i]["_rev"] == tenders_before[i]["_rev"]  # not changed
            assert tenders[i]["title"] == tenders_before[i]["title"]  # not changed
        assert tenders[i]["title_en"] == tenders_before[i]["title_en"]
        assert tenders[i]["dateModified"] == tenders_before[i]["dateModified"]
        assert tenders[i]["public_modified"] == tenders_before[i]["public_modified"]


def test_migration_with_filter_arg(migration_app):
    collection = migration_app.app.registry.mongodb.tenders.collection

    # Get not migrated data
    tenders_before = list(collection.find())

    # Set filter arg
    test_args = deepcopy(default_test_args)
    test_args.filter = '{"procurementMethodType": "belowThreshold"}'

    # Create migration
    migration = TestMigration(app_env(migration_app), test_args)

    # Run migration
    migration.run()

    # Get migrated data
    tenders = list(collection.find())

    # Verify migration results
    for i in range(len(tenders)):
        assert tenders[i]["_id"] == tenders_before[i]["_id"]
        if tenders[i]["procurementMethodType"] == "belowThreshold":
            assert tenders[i]["_rev"] != tenders_before[i]["_rev"]  # changed
            assert tenders[i]["title"] != tenders_before[i]["title"]  # changed
        else:
            assert tenders[i]["_rev"] == tenders_before[i]["_rev"]  # not changed
            assert tenders[i]["title"] == tenders_before[i]["title"]  # not changed
        assert tenders[i]["title_en"] == tenders_before[i]["title_en"]
        assert tenders[i]["dateModified"] == tenders_before[i]["dateModified"]
        assert tenders[i]["public_modified"] == tenders_before[i]["public_modified"]


def test_migration_with_projection(migration_app):
    collection = migration_app.app.registry.mongodb.tenders.collection

    # Get not migrated data
    tenders_before = list(collection.find())

    # Create migration class
    class Migration(TestMigration):
        def get_projection(self) -> dict:
            return {"_id": 1, "title": 1}

    # Run migration
    migration = Migration(app_env(migration_app), default_test_args)

    # Run migration
    migration.run()

    # Get migrated data
    tenders = list(collection.find())

    # Verify migration results
    for i in range(len(tenders)):
        assert tenders[i]["_id"] == tenders_before[i]["_id"]
        assert tenders[i]["_rev"] != tenders_before[i]["_rev"]  # changed
        assert tenders[i]["title"] != tenders_before[i]["title"]
        assert tenders[i]["title_en"] == tenders_before[i]["title_en"]
        assert tenders[i]["dateModified"] == tenders_before[i]["dateModified"]
        assert tenders[i]["public_modified"] == tenders_before[i]["public_modified"]


def test_migration_update_date_modified(migration_app):
    collection = migration_app.app.registry.mongodb.tenders.collection

    # Get not migrated data
    tenders_before = list(collection.find())

    # Create migration
    migration = TestMigration(app_env(migration_app), default_test_args)
    migration.update_date_modified = True

    # Run migration
    migration.run()

    # Get migrated data
    tenders = list(collection.find())

    # Verify migration results
    for i in range(len(tenders)):
        assert tenders[i]["_id"] == tenders_before[i]["_id"]
        assert tenders[i]["_rev"] != tenders_before[i]["_rev"]  # changed
        assert tenders[i]["title"] != tenders_before[i]["title"]  # changed
        assert tenders[i]["title_en"] == tenders_before[i]["title_en"]
        assert tenders[i]["dateModified"] != tenders_before[i]["dateModified"]  # changed
        assert tenders[i]["public_modified"] == tenders_before[i]["public_modified"]


def test_migration_update_feed_position(migration_app):
    collection = migration_app.app.registry.mongodb.tenders.collection

    # Get not migrated data
    tenders_before = list(collection.find())

    # Create migration
    migration = TestMigration(app_env(migration_app), default_test_args)
    migration.update_feed_position = True

    # Run migration
    migration.run()

    # Get migrated data
    tenders = list(collection.find())

    # Verify migration results
    for i in range(len(tenders)):
        assert tenders[i]["_id"] == tenders_before[i]["_id"]
        assert tenders[i]["_rev"] != tenders_before[i]["_rev"]  # changed
        assert tenders[i]["title"] != tenders_before[i]["title"]  # changed
        assert tenders[i]["title_en"] == tenders_before[i]["title_en"]
        assert tenders[i]["dateModified"] == tenders_before[i]["dateModified"]
        assert tenders[i]["public_modified"] != tenders_before[i]["public_modified"]  # changed


def test_migration_with_readonly_arg(migration_app):
    collection = migration_app.app.registry.mongodb.tenders.collection

    # Get not migrated data
    tenders_before = list(collection.find())

    # Set filter arg
    test_args = deepcopy(default_test_args)
    test_args.readonly = True

    # Create migration
    migration = TestMigration(app_env(migration_app), test_args)

    # Run migration
    migration.run()

    # Get migrated data
    tenders = list(collection.find())

    # Verify migration results
    for i in range(len(tenders)):
        assert tenders[i]["_id"] == tenders_before[i]["_id"]
        assert tenders[i]["_rev"] == tenders_before[i]["_rev"]
        assert tenders[i]["title"] == tenders_before[i]["title"]
        assert tenders[i]["title_en"] == tenders_before[i]["title_en"]
        assert tenders[i]["dateModified"] == tenders_before[i]["dateModified"]
        assert tenders[i]["public_modified"] == tenders_before[i]["public_modified"]

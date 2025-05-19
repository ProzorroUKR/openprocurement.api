from openprocurement.api.tests.base import (  # pylint: disable=unused-import
    app,
    singleton_app,
)
from openprocurement.api.tests.migration import create_collection_migration_test

test_0031_migrate_local_origin_criteria = create_collection_migration_test(
    "openprocurement.tender.core.migrations.0031_migrate_local_origin_criteria.Migration"
)

test_0032_migrate_bids_initial_value = create_collection_migration_test(
    "openprocurement.tender.core.migrations.0032_migrate_bids_initial_value.Migration"
)

test_0034_migrate_contract_template_name = create_collection_migration_test(
    "openprocurement.tender.core.migrations.0034_migrate_contract_template_name.Migration"
)

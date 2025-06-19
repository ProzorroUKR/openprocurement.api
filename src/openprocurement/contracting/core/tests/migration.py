from openprocurement.api.tests.base import (  # pylint: disable=unused-import
    app,
    singleton_app,
)
from openprocurement.api.tests.migration import create_collection_migration_test

test_0006_migrate_contract_template_name = create_collection_migration_test(
    "openprocurement.contracting.core.migrations.0006_migrate_contract_template_name.Migration"
)

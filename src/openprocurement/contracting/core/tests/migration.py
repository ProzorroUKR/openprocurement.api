from openprocurement.api.tests.base import app, singleton_app
from openprocurement.api.tests.migration import create_collection_migration_test

fixtures = (app, singleton_app)


test_0006_migrate_contract_template_name = create_collection_migration_test(
    "openprocurement.contracting.core.migrations.0006_migrate_contract_template_name.Migration"
)

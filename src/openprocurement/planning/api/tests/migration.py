from openprocurement.api.tests.base import app, singleton_app
from openprocurement.api.tests.migration import create_collection_migration_test

fixtures = (app, singleton_app)


test_0001_migrate_plan_budget_project_scheme = create_collection_migration_test(
    "openprocurement.planning.migrations.0001_migrate_plan_budget_project_scheme.Migration"
)

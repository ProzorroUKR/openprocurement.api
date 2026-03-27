from openprocurement.api.tests.base import (  # pylint: disable=unused-import
    app,
    singleton_app,
)
from openprocurement.api.tests.migration import create_collection_migration_test

test_0010_rename_cfaua_agreement_type = create_collection_migration_test(
    "openprocurement.framework.core.migrations.0010_rename_cfaua_agreement_type.Migration"
)

test_0011_migrate_milestones_to_cfaua_agreements = create_collection_migration_test(
    "openprocurement.framework.core.migrations.0011_migrate_milestones_to_cfaua_agreements.Migration"
)

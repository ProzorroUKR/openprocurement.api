import logging
from importlib import import_module
from typing import Type

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection

tender_migration = import_module("openprocurement.tender.core.migrations.0034_migrate_contract_template_name")
BaseMigration: Type[CollectionMigration] = tender_migration.Migration

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(BaseMigration):
    description = "Migrate contract template name (contracts)"

    collection_name = "contracts"


if __name__ == "__main__":
    migrate_collection(Migration)

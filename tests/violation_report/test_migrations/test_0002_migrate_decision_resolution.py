from importlib import import_module

from openprocurement.api.migrations.base import CollectionMigrationArgumentParser
from tests.factories.violation_report import (
    DecisionFactory,
    ViolationReportDBModelFactory,
)

migration_module = import_module("prozorro_cdb.violation_report.migrations.0002_migrate_decision_resolution")

OLD_RESOLUTION = "declinedLackEvidence"
NEW_RESOLUTION = "declinedNoViolation"


async def test_migration_updates_matching_resolution(api):
    violation_report = ViolationReportDBModelFactory.build(
        decisions=[
            DecisionFactory.build(resolution=NEW_RESOLUTION),
            DecisionFactory.build(resolution="satisfied"),
        ]
    )
    # OLD_RESOLUTION is no longer a valid enum value, so it can't be built via the
    # pydantic-backed factory. Insert the document directly to simulate legacy data in the DB.
    data = violation_report.model_dump(by_alias=True, mode="json")
    data["decisions"][0]["resolution"] = OLD_RESOLUTION

    collection = ViolationReportDBModelFactory.get_collection()
    await collection.collection.insert_one(data)

    args = CollectionMigrationArgumentParser().parse_args([])
    migration = migration_module.Migration(args=args)
    await migration.run()

    updated_data = await migration.collection.find_one({"_id": violation_report.id})

    assert updated_data["decisions"][0]["resolution"] == NEW_RESOLUTION
    assert updated_data["decisions"][1]["resolution"] == "satisfied"
    assert updated_data["_rev"] != violation_report.rev
    assert "public_modified" in updated_data
    assert updated_data["public_modified"] != violation_report.public_modified
    assert updated_data["dateModified"] == violation_report.dateModified.isoformat()


async def test_migration_skips_documents_without_matching_resolution(api):
    violation_report = await ViolationReportDBModelFactory.create(
        decisions=[
            DecisionFactory.build(resolution="satisfied"),
            DecisionFactory.build(resolution=NEW_RESOLUTION),
        ]
    )

    args = CollectionMigrationArgumentParser().parse_args([])
    migration = migration_module.Migration(args=args)
    await migration.run()

    updated_data = await migration.collection.find_one({"_id": violation_report.id})

    assert updated_data["decisions"][0]["resolution"] == "satisfied"
    assert updated_data["decisions"][1]["resolution"] == NEW_RESOLUTION
    assert updated_data["_rev"] == violation_report.rev
    assert updated_data["public_modified"] == violation_report.public_modified

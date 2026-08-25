from prozorro_cdb.api.migrations.utils import AsyncIOMotorCollectionMigration, migrate_collection
from prozorro_cdb.violation_report.database.collection import ViolationReportCollection

OLD_RESOLUTION = "declinedLackEvidence"
NEW_RESOLUTION = "declinedNoViolation"


class Migration(AsyncIOMotorCollectionMigration):
    description: str = f"migrate decisions.resolution {OLD_RESOLUTION!r} to {NEW_RESOLUTION!r}"

    collection_name = ViolationReportCollection.collection_name

    append_revision = False
    update_date_modified = False
    update_feed_position = True

    def get_filter(self) -> dict:
        return {"decisions.resolution": OLD_RESOLUTION}

    def get_projection(self) -> dict:
        return {"decisions": 1}

    def update_document(self, doc: dict, context: dict = None):
        changed = False
        for decision in doc.get("decisions", []):
            if decision.get("resolution") == OLD_RESOLUTION:
                decision["resolution"] = NEW_RESOLUTION
                changed = True

        return doc if changed else None


if __name__ == "__main__":
    # python src/prozorro_cdb/violation_report/migrations/0002_migrate_decision_resolution.py -p <path to service.ini>
    migrate_collection(Migration)

import logging
from copy import deepcopy

from jsonpatch import JsonPatchConflict, apply_patch
from jsonpointer import JsonPointerException

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Fix bids revisions"

    collection_name = "tenders"

    append_revision = False

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {
            "bids": {
                "$exists": True,
                "$not": {"$size": 0},
            },
        }

    def update_document(self, doc, context=None):
        self.fix_bids_revisions(doc)
        return doc

    def fix_bids_revisions(self, doc):
        if "bids" not in doc:
            return doc

        rewinded_doc = deepcopy(doc)

        for revision in reversed(doc["revisions"]):
            changes_to_remove = []

            for change in list(revision["changes"]):
                if change["path"].startswith("/bids"):
                    try:
                        # to avoid mutating the original change
                        # after new changes are applied on top of it
                        change_copy = deepcopy(change)
                        # apply the change to the rewinded document
                        apply_patch(rewinded_doc, [change_copy], in_place=True)

                    except JsonPointerException as e:

                        # empty lists was handled wrong for some period
                        if change["op"] == "add" and str(e).startswith("member 'lotValues' not found in"):
                            new_path = change["path"].rsplit("/", 1)[0]
                            if new_path.endswith("/lotValues"):
                                change["path"] = new_path
                                change["value"] = [change["value"]]
                                continue

                        logger.error(f"JsonPointerException: {e}, for change: {change}")
                        raise

                    except JsonPatchConflict as e:

                        # empty lists was handled wrong for some period
                        if str(e) in [
                            "can't remove non-existent object 'parameters'",
                            "can't remove non-existent object 'documents'",
                            "can't remove non-existent object 'additionalIdentifiers'",
                        ]:
                            changes_to_remove.append(change)
                            continue

                        # those where deleted by migration in the past
                        # without a proper revision
                        if "/requirementResponses/" in change["path"] and str(e) in [
                            "can't remove non-existent object 'title'",
                            "can't replace non-existent object 'title'",
                            "can't remove non-existent object 'description'",
                            "can't replace non-existent object 'description'",
                        ]:
                            changes_to_remove.append(change)
                            continue

                        logger.error(f"JsonPatchConflict: {e}, for change: {change}")
                        raise

            if changes_to_remove:
                self.remove_changes(revision, changes_to_remove)

            draft_leave_change = {"op": "replace", "path": "/status", "value": "draft"}
            if draft_leave_change in revision["changes"]:
                break

        return doc

    def remove_changes(self, revision, changes):
        for change in changes:
            try:
                revision["changes"].remove(change)
            except ValueError:
                pass

    def generate_base_pipeline_stages(self, doc: dict) -> list:
        return [
            {
                "$set": {
                    "revisions": doc["revisions"],
                }
            },
        ]


if __name__ == "__main__":
    migrate_collection(Migration)

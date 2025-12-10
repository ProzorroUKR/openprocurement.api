import logging
from copy import deepcopy

from jsonpatch import JsonPatchConflict, apply_patch
from jsonpointer import JsonPointerException

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection

logging.basicConfig(level=logging.INFO, format="%(message)s")
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

            if "changes" not in revision:
                # there are revisions without changes from chronograph in some old tenders
                # probably was a bug in the past
                # ignoring them
                continue

            for change in list(revision["changes"]):
                if change["path"].startswith("/bids"):
                    try:
                        apply_patch(rewinded_doc, [deepcopy(change)], in_place=True)

                    except JsonPointerException as e:
                        # empty lists was handled wrong for some period
                        if str(e).startswith(
                            (
                                "member 'lotValues' not found in",
                                "member 'parameters' not found in",
                                "member 'documents' not found in",
                                "member 'eligibilityDocuments' not found in",
                                "member 'qualificationDocuments' not found in",
                                "member 'financialDocuments' not found in",
                            )
                        ):
                            if change["op"] != "add":
                                raise

                            key = str(e).split("'")[1]
                            if not change["path"].endswith(f"/{key}/0"):
                                raise

                            self.fix_add_to_new_list(change)

                            # apply fixed change
                            apply_patch(rewinded_doc, [deepcopy(change)], in_place=True)
                            continue

                        logger.error(f"JsonPointerException: {e}, for change: {change}")
                        raise

                    except JsonPatchConflict as e:
                        # empty lists was handled wrong for some period
                        if str(e) in [
                            "can't remove non-existent object 'lotValues'",
                            "can't remove non-existent object 'parameters'",
                            "can't remove non-existent object 'documents'",
                            "can't remove non-existent object 'eligibilityDocuments'",
                            "can't remove non-existent object 'qualificationDocuments'",
                            "can't remove non-existent object 'financialDocuments'",
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

    def fix_add_to_new_list(self, change):
        """
        empty lists was handled wrong for some period

        there are revisions that describe revert action as adding 0th element to list
        {
            "op": "add",
            "path": "/bids/1/parameters/0",
            "value": {...}
        }

        but it should be adding to non existing list (creating a list) instead
        {
            "op": "add",
            "path": "/bids/1/parameters",
            "value": [{...}]
        }
        """
        change["path"] = change["path"].rsplit("/", 1)[0]  # removed index
        change["value"] = [change["value"]]  # wrap in list

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

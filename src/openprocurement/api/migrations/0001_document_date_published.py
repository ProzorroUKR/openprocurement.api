import logging
import os
import re
from time import sleep

from jsonpath_ng import parse
from pymongo import UpdateOne
from pymongo.errors import OperationFailure

from openprocurement.api.migrations.base import (
    BaseMigration,
    BaseMigrationArgumentParser,
    migrate,
)
from openprocurement.api.utils import get_now

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

DOCUMENTS_PATHS_MAP = {
    "tenders": (
        "$.documents[*]",
        "$.awards[*].documents[*]",
        "$.awards[*].complaints[*].documents[*]",
        "$.awards[*].complaints[*].posts[*].documents[*]",
        "$.agreements[*].documents[*]",
        "$.bids[*].documents[*]",
        "$.bids[*].financialDocuments[*]",
        "$.bids[*].qualificationDocuments[*]",
        "$.bids[*].eligibilityDocuments[*]",
        "$.qualifications[*].documents[*]",
        "$.qualifications[*].complaints[*].documents[*]",
        "$.qualifications[*].complaints[*].posts[*].documents[*]",
        "$.cancellations[*].documents[*]",
        "$.cancellations[*].complaints[*].documents[*]",
        "$.cancellations[*].complaints[*].posts[*].documents[*]",
        "$.complaints[*].documents[*]",
        "$.contracts[*].documents[*]",
    ),
    "contracts": (
        "$.documents[*]",
        "$.transactions[*].documents[*]",
    ),
    "frameworks": ("$.documents[*]",),
    "submissions": ("$.documents[*]",),
    "qualifications": ("$.documents[*]",),
    "agreements": ("$.documents[*]", "$.contracts[*].milestones[*].documents[*]"),
    "plans": ("$.documents[*]", "$.milestones[*].documents[*]"),
}


def get_documents_date(revisions):
    regex = r"documents\/\d+$"
    documents_date_published = {}
    for rev in revisions:
        for c in rev.get("changes", ""):
            if c.get("op", "") == "remove" and re.search(regex, c.get("path", ""), flags=re.IGNORECASE):
                if rev.get("date"):
                    documents_date_published[c["path"]] = rev["date"]

    return documents_date_published


def convert_path(path):
    parts = path.split(".")
    parts[0] = "/" + parts[0]
    for i in range(len(parts)):
        if parts[i].startswith("["):
            parts[i] = parts[i].replace("[", "").replace("]", "")
    return "/".join(parts)


def update_documents_from_tender(obj, collection_name, updated):
    is_updated = False
    tender = obj.pop("tender", None)
    if not tender:
        return

    date_published = [
        doc["datePublished"]
        for i in tender.get(collection_name, "")
        for doc in i.get("documents", "")
        if i.get("id", "") == obj["_id"] and "datePublished" in doc
    ]

    if not date_published:
        return

    for i, doc in enumerate(obj.get("documents", "")):
        if len(date_published) > i:
            is_updated = True
            doc["datePublished"] = date_published[i]

    if is_updated:
        updated["documents"] = obj["documents"]


def update_documents_date_published(obj, collection_name, doc_paths):
    updated = {}

    revisions = obj.pop("revisions", "")
    documents_date_published = get_documents_date(revisions)
    # Only for contracts and agreements
    if collection_name == "contracts":
        update_documents_from_tender(obj, collection_name, updated)

    for path in doc_paths:
        duplicated_id = set()
        is_updated = False

        for match in path.find(obj):
            doc = match.value
            if doc["id"] not in duplicated_id:
                duplicated_id.add(doc["id"])
            else:
                path = convert_path(str(match.full_path))
                date_published = documents_date_published.get(path)
                if date_published:
                    doc["datePublished"] = date_published
                    is_updated = True
        if is_updated:
            key = path.split("/")[1]
            updated[key] = obj[key]

    return updated


def bulk_update(bulk, collection, collection_name):
    bulk_size = len(bulk)
    try:
        collection.bulk_write(bulk)
        return bulk_size
    except OperationFailure as e:
        logger.warning(f"Skip updating {bulk_size} {collection_name} Details: {e}")
        return 0


def run(env, args):
    collection_name = args.c

    document_paths_expr = DOCUMENTS_PATHS_MAP.get(collection_name)
    document_paths = []
    projection = {"_rev": 1, "revisions": 1}

    for i in document_paths_expr:
        field_name = i.split(".")[1]
        field_name = field_name[: field_name.find("[")]
        projection[field_name] = 1
        document_paths.append(parse(i))

    migration_name = os.path.basename(__file__).split(".")[0]

    start_date = get_now()
    logger.info(
        f"Starting migration: {migration_name}",
    )

    log_every = 100000

    collection = getattr(env["registry"].mongodb, collection_name).collection

    if collection_name == "contracts":
        projection["tender"] = 1
        pipeline = [
            {
                "$lookup": {
                    "from": env["registry"].mongodb.tenders.collection.name,
                    "let": {"tender_id": "$tender_id"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$_id", "$$tender_id"]}}},
                        {"$project": {"_id": 0, collection_name: 1}},
                    ],
                    "as": "tender",
                }
            },
            {"$unwind": "$tender"},
            {"$project": projection},
        ]
        cursor = collection.aggregate(pipeline)
    else:
        cursor = collection.find(
            {},
            projection=projection,
            no_cursor_timeout=True,
        )
    cursor.batch_size(args.b)

    bulk = []
    count = 0
    bulk_max_size = 500
    try:
        for obj in cursor:
            updated_fields = update_documents_date_published(obj, collection_name, document_paths)

            if updated_fields:
                bulk.append(UpdateOne({"_id": obj["_id"], "_rev": obj["_rev"]}, {"$set": updated_fields}))

            if bulk and len(bulk) % bulk_max_size == 0:
                count += bulk_update(bulk, collection, collection_name)
                bulk = []

                if count % log_every == 0:
                    logger.info(f"Updating {collection_name} documents datePublished: {count} updated")

        sleep(0.000001)
    finally:
        cursor.close()

    if bulk:
        count += bulk_update(bulk, collection, collection_name)

    logger.info(f"Updated {count} {collection_name}")
    time_spent = get_now() - start_date

    logger.info(
        f"Time spent: {time_spent.days} days, {time_spent.seconds//3600} hours, "
        f"{(time_spent.seconds//60)%60 if time_spent.seconds > 3600 else time_spent.seconds} seconds"
    )
    logger.info(f"Successful migration: {migration_name}")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


class MigrationArgumentParser(BaseMigrationArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument("-c", type=str, default="tenders", help="Collection name.")


if __name__ == "__main__":
    migrate(Migration, parser=MigrationArgumentParser)

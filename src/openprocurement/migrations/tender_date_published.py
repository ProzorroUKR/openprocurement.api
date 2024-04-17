# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import argparse
import logging
import os
import re
from time import sleep

from jsonpath_ng import parse
from pymongo.errors import OperationFailure
from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR
from openprocurement.api.utils import get_now

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

DOCUMENTS_PATHS_MAP = {
    "tenders": (
        "$.documents[*]",
        "$.awards[*].documents[*]",
        "$.awards[*].complaints[*].documents[*]",
        "$.awards[*].complaints[*].posts[*].documents[*]",
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


def get_documents_date(obj):
    regex = r"documents\/\d+$"
    documents_date_published = {}
    for rev in obj["revisions"]:
        c = rev["changes"][0]
        if c["op"] == "remove" and re.search(regex, c["path"], flags=re.IGNORECASE):
            documents_date_published[c["path"]] = rev["date"]

    return documents_date_published


def convert_path(path):
    parts = path.split('.')
    parts[0] = '/' + parts[0]
    for i in range(len(parts)):
        if parts[i].startswith('['):
            parts[i] = parts[i].replace('[', '').replace(']', '')
    return '/'.join(parts)


def update_documents_date_published(obj, doc_pathes):
    updated = {}

    documents_date_published = get_documents_date(obj)

    for path in doc_pathes:
        duplicated_id = set()
        is_updated = False

        for match in parse(path).find(obj):
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


def run(env):
    collection_name = args.c

    document_paths = DOCUMENTS_PATHS_MAP.get(collection_name)
    projection = {"_rev": 1, "revisions": 1}

    for i in document_paths:
        field_name = i.split(".")[1]
        field_name = field_name[: field_name.find("[")]
        projection[field_name] = 1

    migration_name = os.path.basename(__file__).split(".")[0]

    start_date = get_now()
    logger.info(
        f"Starting migration: {migration_name}",
    )

    log_every = 1000

    collection = getattr(env["registry"].mongodb, collection_name).collection

    cursor = collection.find(
        {},
        projection=projection,
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)

    count = 0
    try:
        for obj in cursor:
            updated_fields = update_documents_date_published(obj, document_paths)

            if updated_fields:
                try:
                    collection.find_one_and_update(
                        {"_id": obj["_id"], "_rev": obj["_rev"]},
                        [
                            {
                                "$set": updated_fields,
                            },
                        ],
                    )
                    count += 1
                    if count % log_every == 0:
                        logger.info(f"Updating {collection_name} documents datePublished: {count} updated")
                except OperationFailure as e:
                    logger.warning(f"Skip updating {collection_name} {obj['_id']}. Details: {e}")

        sleep(0.000001)
    finally:
        cursor.close()

    logger.info(f"Updated {count} {collection_name}")
    time_spent = get_now() - start_date

    logger.info(
        f"Time spent: {time_spent.days} days, {time_spent.seconds//3600} hours, "
        f"{(time_spent.seconds//60)%60 if time_spent.seconds > 3600 else time_spent.seconds} seconds"
    )
    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        default=os.path.join(BASE_DIR, "etc/service.ini"),
        help="Path to service.ini file",
    )
    parser.add_argument(
        "-b",
        type=int,
        default=1000,
        help=(
            "Limits the number of documents returned in one batch. Each batch " "requires a round trip to the server."
        ),
    )
    parser.add_argument("-c", type=str, default="tenders", help="Collection name.")
    args = parser.parse_args()

    with bootstrap(args.p) as env:
        run(env)

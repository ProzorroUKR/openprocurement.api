# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os
from datetime import datetime

import pymongo
from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    current_collection = env["registry"].mongodb.tenders.collection
    backup_client = pymongo.MongoClient(args.backup_uri)
    backup_db = backup_client[args.backup_db]
    backup_collection = backup_db[args.backup_collection]

    logger.info(f"Using backup collection: {args.backup_collection}")

    if args.readonly:
        logger.info("Running in readonly mode, will only announce changes")

    if args.start_from:
        logger.info(f"Starting from {args.start_from}")

    if args.limit is not None:
        logger.info(f"Limiting to {args.limit} records")

    log_every = 10000
    count = 0

    cutoff_date = datetime(2024, 1, 1)
    query = {
        "is_public": True,
        "public_modified": {"$lte": cutoff_date.timestamp()},
    }

    if args.start_from:
        query["public_modified"]["$gte"] = args.start_from.timestamp()

    cursor = current_collection.find(
        query,
        {
            "_id": 1,
            "complaintPeriod": 1,
            "public_modified": 1,
        },
        no_cursor_timeout=True,
    ).sort("public_modified", pymongo.ASCENDING)
    cursor.batch_size(args.b)

    try:
        for tender in cursor:
            if args.limit is not None and count >= args.limit:
                logger.info(f"Reached limit of {args.limit} records. Stopping.")
                break

            backup_tender = backup_collection.find_one(
                {"_id": tender["_id"]},
                {"complaintPeriod": 1},
            )

            if backup_tender and "complaintPeriod" in backup_tender:
                if "complaintPeriod" not in tender or tender["complaintPeriod"] != backup_tender["complaintPeriod"]:
                    if args.readonly:
                        logger.info(
                            f"Would update complaintPeriod for tender {tender['_id']} to {backup_tender['complaintPeriod']}"
                        )
                    else:
                        current_collection.update_one(
                            {"_id": tender["_id"]},
                            {"$set": {"complaintPeriod": backup_tender["complaintPeriod"]}},
                        )
                    count += 1
            elif "complaintPeriod" in tender:
                if args.readonly:
                    logger.info(f"Would remove complaintPeriod for tender {tender['_id']}")
                else:
                    current_collection.update_one(
                        {"_id": tender["_id"]},
                        {"$unset": {"complaintPeriod": ""}},
                    )
                count += 1

            if count % log_every == 0:
                logger.info(f"Processing complaintPeriod field: processed {count} tenders")
    finally:
        cursor.close()

    logger.info(f"Processing complaintPeriod field finished: processed {count} tenders")

    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    parser.add_argument(
        "--backup-uri",
        required=True,
        help="MongoDB connection string for the backup database",
    )
    parser.add_argument(
        "--backup-db",
        required=True,
        help="Name of the backup database to process",
    )
    parser.add_argument(
        "--backup-collection",
        required=True,
        help="Name of the backup collection to process",
    )
    parser.add_argument(
        "--readonly",
        action="store_true",
        default=False,
        help="Run in readonly mode, only announcing changes without modifying the database",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of records to process",
    )
    parser.add_argument(
        "--start-from",
        type=datetime.fromisoformat,
        default=None,
        help="Start processing from this date (ISO format)",
    )
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)

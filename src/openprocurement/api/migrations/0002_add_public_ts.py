# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)


import logging
from decimal import Decimal

from bson import Timestamp
from pymongo import ASCENDING, IndexModel
from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

source_field_name = "public_modified"
target_field_name = "public_ts"
log_every = 100000


def migrate(*_, database, batch_size, item_types):
    logger.info(f"Starting migration for {item_types}")

    for item_type in item_types:
        logger.info(f"Starting migrate {item_type}")
        count = 0

        collection = getattr(database, item_type).collection
        cursor = collection.find(
            {source_field_name: {"$exists": True}, target_field_name: {"$exists": False}},
            {source_field_name: 1},
        )
        cursor.batch_size(batch_size)

        try:
            for item in cursor:
                source_value = item[source_field_name]  # ex.: 1720853533.483
                decimal_value = Decimal(str(source_value))  # so 0.829 won't become 0.8289999961853027
                seconds = int(decimal_value)
                milliseconds = int((decimal_value - seconds) * 1000)
                collection.update_one(
                    {
                        "_id": item["_id"],
                        source_field_name: source_value,
                    },
                    {
                        "$set": {
                            target_field_name: Timestamp(seconds, milliseconds),
                        },
                    },
                )
                count += 1
                if count % log_every == 0:
                    logger.info(f"Updating {item_type} with {target_field_name}: updated {count}")
        finally:
            cursor.close()

        logger.info(f"Migration of {item_type} finished: updated {count}")

    logger.info("Migration finished")


def add_index(*_, database, item_types):
    logger.info(f"Adding indices to {item_types}")

    for item_type in item_types:
        logger.info(f"Adding index to {item_type}")
        collection = getattr(database, item_type).collection

        test_by_public_ts = IndexModel(
            [(target_field_name, ASCENDING), ("existing_key", ASCENDING)],
            name="test_by_public_ts",
            partialFilterExpression={
                "is_test": True,
                "is_public": True,
            },
        )
        real_by_public_ts = IndexModel(
            [(target_field_name, ASCENDING)],
            name="real_by_public_ts",
            partialFilterExpression={
                "is_test": False,
                "is_public": True,
            },
        )
        all_by_public_ts = IndexModel(
            [
                (target_field_name, ASCENDING),
                ("surely_existing_key", ASCENDING),
            ],
            name="all_by_public_ts",
            partialFilterExpression={
                "is_public": True,
            },
        )
        indices = [all_by_public_ts, real_by_public_ts, test_by_public_ts]

        if item_type in ("submissions", "agreement"):
            for_framework_by_public_ts = IndexModel(
                [("frameworkID", ASCENDING), (target_field_name, ASCENDING)],
                name="for_framework_by_public_ts",
                partialFilterExpression={
                    "is_public": True,
                },
            )
            indices.append(for_framework_by_public_ts)

        try:
            result = collection.create_indexes(indices)
        except Exception as e:
            logger.error(f"Index failed for {item_type}. If already exists, then ignore")
            logger.exception(e)
        else:
            logger.info(f"Index added for {item_type}: {result}")

    logger.info("All indices processed")


def check(*_, database, item_types):
    logger.info(f"Starting checks for {item_types}")

    for item_type in item_types:
        logger.info(f"Check {item_type}")
        collection = getattr(database, item_type).collection

        try:
            count = collection.count_documents(
                {
                    target_field_name: {"$exists": False},
                    "is_public": True,  # to use index
                },
            )
        except Exception as e:
            logger.error(f"Count failed for {item_type}")
            logger.exception(e)
        else:
            if count == 0:
                logger.info(f"Success: '{item_type}' migrated!")
            else:
                logger.info(f"Failure: there are {count} unprocessed '{item_type}'!")

    logger.info("All checks finished")


if __name__ == "__main__":
    parser = MigrationArgumentParser()

    commands = ["all", "migrate", "index", "check"]
    default_cmd = commands[0]
    parser.add_argument(
        "--cmd",
        choices=commands,
        default=default_cmd,
        nargs="?",
        help=f"Provide cmd to run: {', '.join(commands)}",
    )

    all_item_types = [
        "tenders",
        "plans",
        "contracts",
        "agreements",
        "frameworks",
        "qualifications",
        "submissions",
    ]
    parser.add_argument(
        "--item_types",
        choices=all_item_types,
        default=all_item_types,
        nargs="*",
        help=f"Provide item types to process: {', '.join(all_item_types)}",
    )
    args = parser.parse_args()

    process_item_types = args.item_types or all_item_types

    with bootstrap(args.p) as env:
        if args.cmd in ("all", "migrate"):
            migrate(
                database=env["registry"].mongodb,
                batch_size=args.b,
                item_types=process_item_types,
            )

        if args.cmd in ("all", "index"):
            add_index(
                database=env["registry"].mongodb,
                item_types=process_item_types,
            )

        if args.cmd in ("all", "check"):
            check(
                database=env["registry"].mongodb,
                item_types=process_item_types,
            )

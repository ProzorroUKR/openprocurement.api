#!/usr/bin/env python
import datetime
from time import sleep

from gevent import monkey

from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.framework.core.utils import calculate_framework_date, SUBMISSION_STAND_STILL_DURATION

monkey.patch_all(thread=False, select=False)

import os
import argparse
import logging

from openprocurement.api.constants import BASE_DIR, TZ
from pyramid.paster import bootstrap

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def load_ids(file_path):
    ids = []
    with open(file_path, 'r') as file:
        for line in file:
            ids.append(line.strip())
    return ids

def run(env):
    base_path = os.path.dirname(os.path.abspath(__file__))

    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    frameworks_collection = env["registry"].mongodb.frameworks.collection
    agreements_collection = env["registry"].mongodb.agreements.collection

    ids = []

    try:
        ids = load_ids(args.f)
    except FileNotFoundError:
        ids = load_ids(os.path.join(base_path, args.f))

    logger.info(f"Loaded {len(ids)} framework ids: ")

    new_qual_period_end_date = parse_date(args.d, default_timezone=TZ)

    logger.info(f"New qualificationPeriod.endDate: {new_qual_period_end_date.isoformat()}")

    logger.info("Updating framework/agreement pairs")

    count = 0

    cursor = frameworks_collection.find(
        {"_id": {"$in": ids}},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for framework in cursor:
            new_period_end_date = calculate_framework_date(
                new_qual_period_end_date,
                datetime.timedelta(days=-SUBMISSION_STAND_STILL_DURATION),
                framework,
            )

            now = get_now()

            logger.info(f"Updating framework {framework['_id']}: {now}")
            frameworks_collection.find_one_and_update(
                {"_id": framework["_id"], "_rev": framework["_rev"]},
                [
                    {
                        "$set": {
                            "qualificationPeriod.endDate": new_qual_period_end_date.isoformat(),
                            "period.endDate": new_period_end_date.isoformat(),
                            "dateModified": now.isoformat(),
                            "public_modified": {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                        },
                    },
                ],
            )

            if not "agreementID" in framework:
                logger.info(f"Framework {framework['_id']} has no agreementID")
                continue

            agreement = agreements_collection.find_one({"_id": framework['agreementID']})
            logger.info(f"Updating agreement {agreement['_id']} of framework {framework['_id']}: {now}")

            for contract in agreement.get('contracts', []):
                for milestone in contract.get('milestones', []):
                    if milestone['type'] == 'activation' and milestone['status'] == 'scheduled':
                        milestone['dueDate'] = new_qual_period_end_date.isoformat()
                        milestone['dateModified'] = now.isoformat()

            agreements_collection.find_one_and_update(
                {"_id": agreement['_id'], "_rev": agreement["_rev"]},
                [
                    {
                        "$set": {
                            "period.endDate": new_qual_period_end_date.isoformat(),
                            "contracts": agreement.get('contracts', []),
                            "dateModified": now.isoformat(),
                            "public_modified": {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                        },
                    },
                ],
            )

            count += 1

            sleep(0.000001)
    finally:
        cursor.close()

    logger.info(f"Updated {count} framework/agreement pairs")

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
            "Limits the number of documents returned in one batch. Each batch "
            "requires a round trip to the server."
        )
    )
    parser.add_argument(
        "-f",
        type=str,
        required=True,
        help=(
            "File csv with the list of framework ids."
        )
    )
    parser.add_argument(
        "-d",
        type=str,
        required=True,
        help=(
            "New qualificationPeriod.endDate."
        )
    )
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env)

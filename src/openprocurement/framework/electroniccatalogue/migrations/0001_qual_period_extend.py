import datetime
import logging
import os
from time import sleep

from openprocurement.api.constants import TZ
from openprocurement.api.context import get_request
from openprocurement.api.database import get_public_modified, get_public_ts
from openprocurement.api.migrations.base import (
    BaseMigration,
    BaseMigrationArgumentParser,
    migrate,
)
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.framework.core.procedure.state.agreement import AgreementState
from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.framework.core.utils import (
    SUBMISSION_STAND_STILL_DURATION,
    calculate_framework_full_date,
)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def load_ids(file_path):
    ids = []
    with open(file_path) as file:
        for line in file:
            ids.append(line.strip())
    return ids


def run(env, args):
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
            new_period_end_date = calculate_framework_full_date(
                new_qual_period_end_date,
                datetime.timedelta(days=-SUBMISSION_STAND_STILL_DURATION),
                framework=framework,
            )

            now = get_now()

            framework['qualificationPeriod']['endDate'] = new_qual_period_end_date.isoformat()
            framework['period']['endDate'] = new_period_end_date.isoformat()
            framework['dateModified'] = now.isoformat()
            framework["next_check"] = FrameworkState(get_request()).get_next_check(framework)

            logger.info(f"Updating framework {framework['_id']}: {now}")
            frameworks_collection.find_one_and_update(
                {"_id": framework["_id"], "_rev": framework["_rev"]},
                [
                    {
                        "$set": {
                            "qualificationPeriod.endDate": framework['qualificationPeriod']['endDate'],
                            "period.endDate": framework['period']['endDate'],
                            "dateModified": framework['dateModified'],
                            "next_check": framework["next_check"],
                            "public_modified": get_public_modified(),
                            "public_ts": get_public_ts(),
                        },
                    },
                ],
            )

            if not "agreementID" in framework:
                logger.info(f"Framework {framework['_id']} has no agreementID")
                continue

            agreement = agreements_collection.find_one({"_id": framework['agreementID']})
            logger.info(f"Updating agreement {agreement['_id']} of framework {framework['_id']}: {now}")

            agreement['period']['endDate'] = new_qual_period_end_date.isoformat()
            agreement['dateModified'] = now.isoformat()

            for contract in agreement.get('contracts', []):
                for milestone in contract.get('milestones', []):
                    if milestone['type'] == 'activation' and milestone['status'] == 'scheduled':
                        milestone['dueDate'] = new_qual_period_end_date.isoformat()
                        milestone['dateModified'] = now.isoformat()

            agreement["next_check"] = AgreementState.get_next_check(agreement)

            agreements_collection.find_one_and_update(
                {"_id": agreement['_id'], "_rev": agreement["_rev"]},
                [
                    {
                        "$set": {
                            "period.endDate": agreement['period']['endDate'],
                            "contracts": agreement.get('contracts', []),
                            "dateModified": agreement['dateModified'],
                            "next_check": agreement["next_check"],
                            "public_modified": get_public_modified(),
                            "public_ts": get_public_ts(),
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


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


class MigrationArgumentParser(BaseMigrationArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument("-f", type=str, required=True, help=("File csv with the list of framework ids."))
        self.add_argument("-d", type=str, required=True, help=("New qualificationPeriod.endDate."))


if __name__ == "__main__":
    migrate(Migration, parser=MigrationArgumentParser)

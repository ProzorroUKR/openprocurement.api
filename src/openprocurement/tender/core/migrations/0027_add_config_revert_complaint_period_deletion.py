# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os
from datetime import timedelta

import pymongo
from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_tender_full_date
from openprocurement.tender.openuadefense.constants import ABOVE_THRESHOLD_UA_DEFENSE
from openprocurement.tender.simpledefense.constants import SIMPLE_DEFENSE

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def get_working_days(tender):
    return tender["procurementMethodType"] in (
        SIMPLE_DEFENSE,
        ABOVE_THRESHOLD_UA_DEFENSE,
    )


def get_complaint_period(tender):
    if tender["config"]["hasTenderComplaints"] is not True:
        return
    if "tenderPeriod" not in tender or "endDate" not in tender["tenderPeriod"]:
        return
    if tender["config"]["tenderComplainRegulation"] == 0:
        return
    tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
    end_date = calculate_tender_full_date(
        tendering_end,
        -timedelta(days=tender["config"]["tenderComplainRegulation"]),
        tender=tender,
        working_days=get_working_days(tender),
    )
    return {
        "startDate": tender["tenderPeriod"]["startDate"],
        "endDate": end_date.isoformat(),
    }


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tenders with complaintPeriod field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {
            "is_public": True,
            "complaintPeriod": {"$exists": 0},
        },
        {
            "procurementMethodType": 1,
            "config": 1,
            "tenderPeriod": 1,
            "procurementMethodDetails": 1,
        },
        no_cursor_timeout=True,
    ).sort(
        "public_modified",
        pymongo.DESCENDING,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            period = get_complaint_period(tender)
            if period:
                collection.update_one(
                    {"_id": tender["_id"]},
                    {"$set": {"complaintPeriod": period}},
                )
                count += 1
                if count % log_every == 0:
                    logger.info(f"Updating tenders with complaintPeriod field: updated {count} tenders")
    finally:
        cursor.close()

    logger.info(f"Updating tenders with complaintPeriod field finished: updated {count} tenders")

    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)

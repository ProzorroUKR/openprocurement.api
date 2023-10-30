from datetime import timedelta

from gevent import monkey

from openprocurement.api.utils import parse_date
from openprocurement.tender.cfaua.constants import CFA_UA
from openprocurement.tender.competitivedialogue.constants import CD_UA_TYPE, CD_EU_TYPE, STAGE_2_EU_TYPE
from openprocurement.tender.esco.constants import ESCO
from openprocurement.tender.openeu.constants import ABOVE_THRESHOLD_EU

if __name__ == "__main__":
    monkey.patch_all(thread=False, select=False)

import os
import argparse
import logging

from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def count_reporting_date_publication(tender):
    pmt = tender.get("procurementMethodType")
    qualification_types = (ABOVE_THRESHOLD_EU, CFA_UA, ESCO, CD_UA_TYPE, CD_EU_TYPE, STAGE_2_EU_TYPE)
    period_end_date = parse_date(tender.get("qualificationPeriod", {}).get("endDate"))
    reporting_date = period_end_date - timedelta(days=6) if pmt in qualification_types else period_end_date
    return reporting_date.isoformat()


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tenders with qualificationPeriod.reportingDatePublication field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {
            "qualificationPeriod.endDate": {"$exists": True},
            "qualificationPeriod.reportingDatePublication": {"$exists": False},
        },
        {"qualificationPeriod": 1, "procurementMethodType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            if tender.get("qualificationPeriod", {}).get("reportingDatePublication") is None:
                collection.update_one(
                    {"_id": tender["_id"]},
                    {"$set": {"qualificationPeriod.reportingDatePublication": count_reporting_date_publication(tender)}}
                )
                count += 1
                if count % log_every == 0:
                    logger.info(
                        f"Updating tenders with qualificationPeriod.reportingDatePublication field: "
                        f"updated {count} tenders"
                    )
    finally:
        cursor.close()

    logger.info(
        f"Updating tenders with qualificationPeriod.reportingDatePublication field finished: "
        f"updated {count} tenders"
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
            "Limits the number of documents returned in one batch. Each batch "
            "requires a round trip to the server."
        )
    )
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)

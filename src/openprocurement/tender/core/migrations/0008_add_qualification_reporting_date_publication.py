import logging
import os
from datetime import timedelta

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.migrations.base import BaseMigration, migrate
from openprocurement.api.procedure.utils import parse_date

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def count_reporting_date_publication(tender):
    pmt = tender.get("procurementMethodType")
    qualification_types = (
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
        ProcurementMethodType.ESCO,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    )
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
                    {
                        "$set": {
                            "qualificationPeriod.reportingDatePublication": count_reporting_date_publication(tender)
                        }
                    },
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


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)

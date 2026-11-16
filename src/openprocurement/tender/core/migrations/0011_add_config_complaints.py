import logging
import os

from pymongo.errors import OperationFailure

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.migrations.base import BaseMigration, migrate

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def has_tender_complaints_populator(tender):
    if tender.get("config", {}).get("tenderComplaints") is not None:
        return tender["config"]["tenderComplaints"]
    pmt = tender.get("procurementMethodType")
    if pmt in (
        ProcurementMethodType.BELOW_THRESHOLD,
        ProcurementMethodType.COMPETITIVE_ORDERING,
        ProcurementMethodType.REPORTING,
        ProcurementMethodType.NEGOTIATION,
        ProcurementMethodType.NEGOTIATION_QUICK,
        ProcurementMethodType.PRICE_QUOTATION,
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA,
    ):
        return False
    return True


def has_award_complaints_populator(tender):
    if tender.get("config", {}).get("awardComplaints") is not None:
        return tender["config"]["awardComplaints"]
    pmt = tender.get("procurementMethodType")
    if pmt in (
        ProcurementMethodType.BELOW_THRESHOLD,
        ProcurementMethodType.COMPETITIVE_ORDERING,
        ProcurementMethodType.REPORTING,
        ProcurementMethodType.PRICE_QUOTATION,
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    ):
        return False
    return True


def has_cancellation_complaints_populator(tender):
    if tender.get("config", {}).get("cancellationComplaints") is not None:
        return tender["config"]["cancellationComplaints"]
    pmt = tender.get("procurementMethodType")
    if pmt in (
        ProcurementMethodType.BELOW_THRESHOLD,
        ProcurementMethodType.COMPETITIVE_ORDERING,
        ProcurementMethodType.REPORTING,
        ProcurementMethodType.PRICE_QUOTATION,
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA,
    ):
        return False
    return True


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tenders with hasTenderComplaints, hasAwardComplaints, hasCancellationComplaints field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.hasTenderComplaints": {"$exists": False}},
        {"config": 1, "procurementMethodType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            if tender.get("config", {}).get("hasTenderComplaints") is None:
                try:
                    collection.update_one(
                        {"_id": tender["_id"]},
                        {
                            "$set": {
                                "config.hasTenderComplaints": has_tender_complaints_populator(tender),
                                "config.hasAwardComplaints": has_award_complaints_populator(tender),
                                "config.hasCancellationComplaints": has_cancellation_complaints_populator(tender),
                            },
                            # delete previous config fields
                            "$unset": {
                                "config.tenderComplaints": "",
                                "config.awardComplaints": "",
                                "config.cancellationComplaints": "",
                            },
                        },
                    )
                    count += 1
                    if count % log_every == 0:
                        logger.info(f"Updating tenders with complaints configurations: updated {count} tenders")
                except OperationFailure as e:
                    logger.warning(f"Skip updating tender {tender['_id']}. Details: {e}")
    finally:
        cursor.close()

    logger.info(f"Updating tenders with complaints configurations: updated {count} tenders")

    logger.info(f"Successful migration: {migration_name}")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)

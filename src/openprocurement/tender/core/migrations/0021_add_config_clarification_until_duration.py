import logging
import os

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.migrations.base import BaseMigration, migrate

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def clarification_until_duration_populator(tender):
    """Populate tender with clarificationUntilDuration config parameter.

    :param tender: Tender instance
    :return:
    """
    pmt = tender.get("procurementMethodType")
    if pmt in [
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
        ProcurementMethodType.COMPETITIVE_ORDERING,
        ProcurementMethodType.ESCO,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE,
    ]:
        return 3
    if pmt in [ProcurementMethodType.BELOW_THRESHOLD]:
        return 1
    if pmt in [
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA,
        ProcurementMethodType.NEGOTIATION,
        ProcurementMethodType.NEGOTIATION_QUICK,
        ProcurementMethodType.PRICE_QUOTATION,
        ProcurementMethodType.REPORTING,
    ]:
        return 0


def run(env, args):
    """Run the migration.

    :param env: WSGI environment
    :param args: command line arguments
    :return int: Days quantity.
    """
    migration_name = os.path.basename(__file__).split(".")[0]
    logger.info("Starting migration: %s", migration_name)
    logger.info("Updating tenders with clarificationUntilDuration field")
    log_every = 100000
    count = 0

    collection = env["registry"].mongodb.tenders.collection
    cursor = collection.find(
        {},
        {"config": 1, "procurementMethodType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)

    try:
        for tender in cursor:
            if tender.get("config", {}).get("clarificationUntilDuration") is None:
                collection.update_one(
                    {"_id": tender["_id"]},
                    {"$set": {"config.clarificationUntilDuration": clarification_until_duration_populator(tender)}},
                )
                count += 1
                if count % log_every == 0:
                    logger.info("Updating tenders with clarificationUntilDuration field: updated %s tenders", count)
    finally:
        cursor.close()

    logger.info(f"Updating tenders with clarificationUntilDuration field finished: updated {count} tenders")
    logger.info(f"Successful migration: {migration_name}")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)

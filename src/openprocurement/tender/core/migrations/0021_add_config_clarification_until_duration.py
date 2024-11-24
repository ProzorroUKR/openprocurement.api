# pylint: disable=wrong-import-position

"""Migration for clarificationUntilDuration config parameter.

Add parameter to all existed tenders.
"""

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os

from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.cfaua.constants import CFA_UA
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE,
    CD_UA_TYPE,
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.esco.constants import ESCO
from openprocurement.tender.limited.constants import (
    NEGOTIATION,
    NEGOTIATION_QUICK,
    REPORTING,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD, COMPETITIVE_ORDERING
from openprocurement.tender.openeu.constants import ABOVE_THRESHOLD_EU
from openprocurement.tender.openua.constants import ABOVE_THRESHOLD_UA
from openprocurement.tender.openuadefense.constants import ABOVE_THRESHOLD_UA_DEFENSE
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.simpledefense.constants import SIMPLE_DEFENSE

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def clarification_until_duration_populator(tender):
    """Populate tender with clarificationUntilDuration config parameter.

    :param tender: Tender instance
    :return:
    """
    pmt = tender.get("procurementMethodType")
    if pmt in [
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_EU,
        ABOVE_THRESHOLD_UA,
        CD_EU_TYPE,
        CD_UA_TYPE,
        COMPETITIVE_ORDERING,
        ESCO,
        SIMPLE_DEFENSE,
        STAGE_2_EU_TYPE,
        STAGE_2_UA_TYPE,
        CFA_UA,
        ABOVE_THRESHOLD_UA_DEFENSE,
    ]:
        return 3
    if pmt in [BELOW_THRESHOLD]:
        return 1
    if pmt in [CFA_SELECTION, NEGOTIATION, NEGOTIATION_QUICK, PQ, REPORTING]:
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


if __name__ == '__main__':
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)

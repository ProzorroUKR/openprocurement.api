# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os

from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.pricequotation.constants import PQ

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def pre_selection_populator(tender):
    pmt = tender.get("procurementMethodType")
    if pmt in (
        CFA_SELECTION,
        PQ,
        COMPETITIVE_ORDERING,
    ):
        return True
    return False


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tenders with hasPreSelectionAgreement field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.hasPreSelectionAgreement": {"$exists": False}},
        {"config": 1, "procurementMethodType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            if tender.get("config", {}).get("hasPreSelectionAgreement") is None:
                collection.update_one(
                    {"_id": tender["_id"]},
                    {"$set": {"config.hasPreSelectionAgreement": pre_selection_populator(tender)}},
                )
                count += 1
                if count % log_every == 0:
                    logger.info(f"Updating tenders with hasPreSelectionAgreement field: updated {count} tenders")
    finally:
        cursor.close()

    logger.info(f"Updating tenders with hasPreSelectionAgreement field finished: updated {count} tenders")

    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)

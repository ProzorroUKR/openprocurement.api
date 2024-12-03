# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os

from pymongo.errors import OperationFailure
from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.limited.constants import (
    NEGOTIATION,
    NEGOTIATION_QUICK,
    REPORTING,
)
from openprocurement.tender.pricequotation.constants import PQ

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def has_tender_complaints_populator(tender):
    if tender.get("config", {}).get("tenderComplaints") is not None:
        return tender["config"]["tenderComplaints"]
    pmt = tender.get("procurementMethodType")
    if pmt in (
        BELOW_THRESHOLD,
        COMPETITIVE_ORDERING,
        REPORTING,
        NEGOTIATION,
        NEGOTIATION_QUICK,
        PQ,
        CFA_SELECTION,
    ):
        return False
    return True


def has_award_complaints_populator(tender):
    if tender.get("config", {}).get("awardComplaints") is not None:
        return tender["config"]["awardComplaints"]
    pmt = tender.get("procurementMethodType")
    if pmt in (
        BELOW_THRESHOLD,
        COMPETITIVE_ORDERING,
        REPORTING,
        PQ,
        CFA_SELECTION,
        CD_EU_TYPE,
        CD_UA_TYPE,
    ):
        return False
    return True


def has_cancellation_complaints_populator(tender):
    if tender.get("config", {}).get("cancellationComplaints") is not None:
        return tender["config"]["cancellationComplaints"]
    pmt = tender.get("procurementMethodType")
    if pmt in (
        BELOW_THRESHOLD,
        COMPETITIVE_ORDERING,
        REPORTING,
        PQ,
        CFA_SELECTION,
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
                                "config.tenderComplaints": '',
                                "config.awardComplaints": '',
                                "config.cancellationComplaints": '',
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


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)

#!/usr/bin/env python
from gevent import monkey

if __name__ == "__main__":
    monkey.patch_all(thread=False, select=False)

import os
import argparse
import logging

from openprocurement.api.constants import BASE_DIR
from pyramid.paster import bootstrap

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def has_auction_populator(tender):
    pmt = tender.get("procurementMethodType")

    if pmt == "aboveThreshold":
        smd = tender.get("submissionMethodDetails")
        if "quick(mode:no-auction)" in smd:
            return False
        else:
            return True

    if pmt in (
        "reporting",
        "negotiation",
        "negotiation.quick",
        "priceQuotation",
    ):
        return False
    return True

def run(env):
    logger.info("Starting migration: %s", __name__)

    collection = env["registry"].mongodb.tenders.collection

    cursor = collection.find({"$snapshot": True})
    for tender in cursor:
        # TODO: write migration logic
        pass

    logger.info("Successful migration: %s", __name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", help="Path to service.ini file")
    args = parser.parse_args()
    path_to_ini_file = args.p if args.p else os.path.join(BASE_DIR, "etc/service.ini")
    with bootstrap(path_to_ini_file) as env:
        run(env)

#!/usr/bin/env python
from gevent import monkey
monkey.patch_all(thread=False, select=False)

import os
import argparse
import logging

from openprocurement.api.constants import BASE_DIR
from pyramid.paster import bootstrap

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def run(env):
    logger.info("Starting migration")

    collection = env["registry"].mongodb.frameworks.collection

    result = collection.update_many(
        {"frameworkType": "open"},
        {"$set": {"frameworkType": "dynamicPurchasingSystem"}},
    )

    logger.info(f"Updated {result.modified_count} items")

    logger.info("Successful migration")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", help="Path to service.ini file")
    args = parser.parse_args()
    path_to_ini_file = args.p if args.p else os.path.join(BASE_DIR, "etc/service.ini")
    with bootstrap(path_to_ini_file) as env:
        run(env)

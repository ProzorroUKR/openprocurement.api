#!/usr/bin/env python
from gevent import monkey
monkey.patch_all(thread=False, select=False)

import os
import argparse
import logging
from collections import defaultdict
from copy import deepcopy
import requests

from openprocurement.tender.core.design import tenders_all_view
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.context import set_now
from openprocurement.api.constants import BASE_DIR
from openprocurement.tender.pricequotation.constants import PMT
from pyramid.paster import bootstrap

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def run(env, catalog_url: str):
    logger.info("Starting migration")
    counters = defaultdict(int)
    db = env["registry"].db
    request = env["request"]
    request.validated = {}
    for i in tenders_all_view(db):
        tender_data = db.get(i.id)
        request.validated["tender_src"] = tender_data
        tender = request.validated["tender"] = deepcopy(tender_data)

        if (
            tender["status"] not in ["active.awarded", "active.qualification"]
            or tender["procurementMethodType"] != PMT
            or not tender.get("profile")
        ):
            skip_tender(counters)
            continue

        profile = tender["profile"]
        agreement = get_agreement_id(catalog_url, profile)
        if not agreement:
            skip_tender(counters)
            continue

        for item in tender.get("items", ""):
            item["profile"] = profile
        tender["agreement"] = {"id": agreement}
        del tender["profile"]
        set_now()
        if save_tender(request):
            counters["tenders"] += 1
        else:
            logger.info(f"Tender {i.id} wasn't updated")
            counters["error_tenders"] += 1
        counters["total_tenders"] += 1

    logger.info(f"Finished stats: {dict(counters)}")


def skip_tender(counters):
    counters["skipped_tenders"] += 1
    counters["total_tenders"] += 1


def get_agreement_id(catalog_url: str, profile_id: str) -> str:
    catalog_profile_url = os.path.join(catalog_url, f"api/profiles/{profile_id}")
    response = requests.get(catalog_profile_url)
    profile_data = response.json()
    if (
        response.status_code == 200
        and "data" in profile_data
        and "agreementID" in profile_data["data"]
    ):
        return profile_data["data"]["agreementID"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", help="Path to service.ini file")
    parser.add_argument("-u", help="Catalog url")
    args = parser.parse_args()
    path_to_ini_file = args.p if args.p else os.path.join(BASE_DIR, "etc/service.ini")
    if not args.u:
        logger.error("Use -u flag to set up catalog url.")
    catalog_url = args.u
    with bootstrap(path_to_ini_file) as env:
        run(env, catalog_url)

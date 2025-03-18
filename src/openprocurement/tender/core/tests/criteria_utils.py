from copy import deepcopy

from webtest import TestApp

from openprocurement.tender.core.constants import (
    CRITERION_LOCALIZATION,
    CRITERION_TECHNICAL_FEATURES,
)
from openprocurement.tender.core.tests.base import test_default_criteria
from openprocurement.tender.core.tests.utils import (
    set_bid_responses,
    set_tender_criteria,
)

TENDERS_WITHOUT_CRITERIA = [
    "aboveThresholdUA.defense",
    "simple.defense",
    "reporting",
    "negotiation",
    "negotiation.quick",
]


def add_criteria(self, tender_id=None, tender_token=None, criteria=None):
    app = self if isinstance(self, TestApp) else self.app
    if not tender_id:
        tender_id = self.tender_id
    if not tender_token:
        tender_token = self.tender_token

    response = app.get("/tenders/{}".format(tender_id))
    tender = response.json["data"]

    if tender["procurementMethodType"] in TENDERS_WITHOUT_CRITERIA:
        return

    if not criteria:
        criteria = test_default_criteria

    criteria = set_tender_criteria(
        criteria,
        tender.get("lots", []),
        tender.get("items", []),
    )

    criteria = deepcopy(criteria)

    def should_keep_criterion(criterion):
        for item in tender["items"]:
            if criterion.get("relatesTo") == "item" and item["id"] == criterion.get("relatedItem"):
                # Skip localization criteria for items without category
                if criterion["classification"]["id"] == CRITERION_LOCALIZATION and not item.get("category"):
                    return False

                # Skip technical features criteria for items without profile and category
                if (
                    criterion["classification"]["id"] == CRITERION_TECHNICAL_FEATURES
                    and not item.get("profile")
                    and not item.get("category")
                ):
                    return False

        return True

    # Filter the criteria
    criteria = list(filter(should_keep_criterion, criteria))

    response = app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(tender_id, tender_token),
        {"data": criteria},
    )

    assert response.status == "201 Created"


def generate_responses(self, tender_id=None):
    app = self if isinstance(self, TestApp) else self.app
    if not tender_id:
        tender_id = self.tender_id
    response = app.get("/tenders/{}".format(tender_id))
    tender = response.json["data"]

    if tender["procurementMethodType"] in TENDERS_WITHOUT_CRITERIA:
        return

    return set_bid_responses(tender.get("criteria", []))

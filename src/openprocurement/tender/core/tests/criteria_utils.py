from webtest import TestApp

from openprocurement.api.constants_env import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.base import (
    test_article_16_criteria,
    test_exclusion_criteria,
    test_language_criteria,
)

TENDERS_WITHOUT_CRITERIA = [
    "aboveThresholdUA.defense",
    "simple.defense",
    "reporting",
    "negotiation",
    "negotiation.quick",
]


def add_criteria(self, tender_id=None, tender_token=None, criteria=test_exclusion_criteria):
    app = self if isinstance(self, TestApp) else self.app
    if not tender_id:
        tender_id = self.tender_id
    if not tender_token:
        tender_token = self.tender_token

    response = app.get("/tenders/{}".format(tender_id))
    if response.json["data"]["procurementMethodType"] in TENDERS_WITHOUT_CRITERIA:
        return
    if get_now() > RELEASE_ECRITERIA_ARTICLE_17:
        response = app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(tender_id, tender_token),
            {"data": criteria},
        )

        assert response.status == "201 Created"

        response = app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(tender_id, tender_token),
            {"data": test_article_16_criteria[:1]},
        )

        assert response.status == "201 Created"

        response = app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(tender_id, tender_token),
            {"data": test_language_criteria},
        )

        assert response.status == "201 Created"


def generate_guarantee_criterion_responses(criterion):
    return [
        {
            "requirement": {
                "id": criterion["requirementGroups"][0]["requirements"][0]["id"],
            },
            "value": 4.0,
        },
        {
            "requirement": {
                "id": criterion["requirementGroups"][0]["requirements"][1]["id"],
            },
            "value": 6,
        },
        {
            "requirement": {
                "id": criterion["requirementGroups"][0]["requirements"][2]["id"],
            },
            "value": True,
        },
        {
            "requirement": {
                "id": criterion["requirementGroups"][0]["requirements"][3]["id"],
            },
            "values": ["Гарантія фінансової установи"],
        },
    ]


def generate_responses(self, tender_id=None):
    app = self if isinstance(self, TestApp) else self.app
    if not tender_id:
        tender_id = self.tender_id
    response = app.get("/tenders/{}".format(tender_id))
    tender = response.json["data"]

    if tender["procurementMethodType"] in TENDERS_WITHOUT_CRITERIA:
        return

    rrs = []
    if get_now() > RELEASE_ECRITERIA_ARTICLE_17:
        for criterion in tender.get("criteria", []):
            if criterion["classification"]["id"] == "CRITERION.OTHER.CONTRACT.GUARANTEE":
                guarantee_responses = generate_guarantee_criterion_responses(criterion)
                rrs.extend(guarantee_responses)
            elif criterion["classification"]["id"] == "CRITERION.OTHER.BID.LANGUAGE":
                rrs.append(
                    {
                        "requirement": {
                            "id": criterion["requirementGroups"][0]["requirements"][0]["id"],
                        },
                        "values": ["ukr"],
                    }
                )
            else:
                for req in criterion["requirementGroups"][0]["requirements"]:
                    if criterion["source"] in ("tenderer", "winner"):
                        rrs.append(
                            {
                                "requirement": {
                                    "id": req["id"],
                                },
                                "value": True,
                            },
                        )
    return rrs

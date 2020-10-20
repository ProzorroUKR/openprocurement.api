from openprocurement.tender.belowthreshold.tests.base import test_criteria
from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.utils import get_now


TENDERS_WITHOUT_CRITERIA = ["aboveThresholdUA.defense", "reporting", "negotiation", "negotiation.quick"]


def add_criteria(self, tender_id=None, tender_token=None):
    if not tender_id:
        tender_id = self.tender_id
    if not tender_token:
        tender_token = self.tender_token

    response = self.app.get("/tenders/{}".format(tender_id))
    if response.json["data"]["procurementMethodType"] in TENDERS_WITHOUT_CRITERIA:
        return
    if get_now() > RELEASE_ECRITERIA_ARTICLE_17:
        response = self.app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(tender_id, tender_token),
            {"data": test_criteria},
        )

        self.assertEqual(response.status, "201 Created")


def generate_responses(self, tender_id=None):
    if not tender_id:
        tender_id = self.tender_id
    response = self.app.get("/tenders/{}".format(tender_id))
    tender = response.json["data"]

    if tender["procurementMethodType"] in TENDERS_WITHOUT_CRITERIA:
        return

    rrs = []
    if get_now() > RELEASE_ECRITERIA_ARTICLE_17:
        for criterion in tender["criteria"]:
            for req in criterion["requirementGroups"][0]["requirements"]:
                if criterion["source"] == "tenderer":
                    rrs.append(
                        {
                            "title": "Requirement response",
                            "description": "some description",
                            "requirement": {
                                "id": req["id"],
                                "title": req["title"],
                            },
                            "value": True,
                        },
                    )
    return rrs

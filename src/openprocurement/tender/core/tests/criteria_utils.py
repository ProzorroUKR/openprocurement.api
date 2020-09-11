from openprocurement.tender.belowthreshold.tests.base import test_criteria
from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.utils import get_now


def add_criteria(self, tender_id=None, tender_token=None):
    if not tender_id:
        tender_id = self.tender_id
    if not tender_token:
        tender_token = self.tender_token

    response = self.app.get("/tenders/{}".format(tender_id))
    without_criteria = ["aboveThresholdUA.defense", "reporting", "negotiation", "negotiation.quick"]
    if response.json["data"]["procurementMethodType"] in without_criteria:
        return
    if get_now() > RELEASE_ECRITERIA_ARTICLE_17:
        response = self.app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(tender_id, tender_token),
            {"data": test_criteria},
        )

        self.assertEqual(response.status, "201 Created")

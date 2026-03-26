from copy import deepcopy

from openprocurement.tender.requestforproposal.tests.base import (
    TenderContentWebTest,
    test_tender_rfp_author,
    test_tender_rfp_bids,
    test_tender_rfp_config,
)

test_tender_rfp_qualification_config = deepcopy(test_tender_rfp_config)
test_tender_rfp_qualification_config["hasPrequalification"] = True


class TenderQualificationBaseTestCase(TenderContentWebTest):
    initial_status = "active.tendering"  # 'active.pre-qualification' status sets in setUp
    initial_bids = test_tender_rfp_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_tender_rfp_author
    initial_config = test_tender_rfp_qualification_config

    def setUp(self):
        super().setUp()
        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]
        self.qualification_id = qualifications[0]["id"]

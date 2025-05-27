import unittest
from copy import deepcopy
from datetime import timedelta
from unittest import mock

from esculator import escp, npv

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.award import (
    Tender2LotAwardDocumentResourceTestMixin,
    TenderAwardComplaintDocumentResourceTestMixin,
    TenderAwardComplaintResourceTestMixin,
    TenderAwardDocumentResourceTestMixin,
    TenderLotAwardCheckResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    create_tender_award_document_json_bulk,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
    test_tender_below_supplier,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.esco.procedure.utils import to_decimal
from openprocurement.tender.esco.tests.award_blanks import patch_tender_lot_award
from openprocurement.tender.esco.tests.base import (
    NBU_DISCOUNT_RATE,
    BaseESCOContentWebTest,
    test_tender_esco_bids,
    test_tender_esco_lots,
)
from openprocurement.tender.open.tests.award import (
    Tender2LotAwardQualificationAfterComplaintMixin,
    TenderAwardQualificationAfterComplaintMixin,
)
from openprocurement.tender.openeu.tests.award import (
    Tender2LotAwardComplaintResourceTestMixin,
    Tender2LotAwardResourceTestMixin,
    TenderLotAwardComplaintResourceTestMixin,
    TenderLotAwardResourceTestMixin,
)
from openprocurement.tender.openeu.tests.award_blanks import (
    check_tender_award_complaint_period_dates,
    create_tender_2lot_award_complaint_document,
    patch_tender_2lot_award_complaint_document,
    patch_tender_award_complaint_document,
    put_tender_2lot_award_complaint_document,
)
from openprocurement.tender.openua.tests.award import (
    TenderUAAwardComplaintResourceTestMixin,
)

award_amount_performance = round(
    float(
        to_decimal(
            npv(
                test_tender_esco_bids[0]["value"]["contractDuration"]["years"],
                test_tender_esco_bids[0]["value"]["contractDuration"]["days"],
                test_tender_esco_bids[0]["value"]["yearlyPaymentsPercentage"],
                test_tender_esco_bids[0]["value"]["annualCostsReduction"],
                get_now(),
                NBU_DISCOUNT_RATE,
            )
        )
    ),
    2,
)

award_amount = round(
    float(
        to_decimal(
            escp(
                test_tender_esco_bids[0]["value"]["contractDuration"]["years"],
                test_tender_esco_bids[0]["value"]["contractDuration"]["days"],
                test_tender_esco_bids[0]["value"]["yearlyPaymentsPercentage"],
                test_tender_esco_bids[0]["value"]["annualCostsReduction"],
                get_now(),
            )
        )
    ),
    2,
)


class TenderLotAwardCheckResourceTest(BaseESCOContentWebTest, TenderLotAwardCheckResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = deepcopy(test_tender_esco_bids)
    initial_bids.append(deepcopy(test_tender_esco_bids[0]))
    initial_bids[1]["tenderers"][0]["name"] = "Не зовсім Державне управління справами"
    initial_bids[1]["tenderers"][0]["identifier"]["id"] = "88837256"
    initial_bids[2]["tenderers"][0]["name"] = "Точно не Державне управління справами"
    initial_bids[2]["tenderers"][0]["identifier"]["id"] = "44437256"
    initial_bids[1]["value"] = {
        "yearlyPaymentsPercentage": 0.9,
        "annualCostsReduction": [500] * 21,
        "contractDuration": {"years": 2, "days": 10},
    }

    reverse = True
    awarding_key = "amountPerformance"

    initial_lots = test_tender_esco_lots
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()
        # switch to active.pre-qualification

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.app.authorization = ("Basic", ("broker", ""))


class TenderLotAwardResourceTest(BaseESCOContentWebTest, TenderLotAwardResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = test_tender_esco_bids
    initial_lots = test_tender_esco_lots
    initial_auth = ("Basic", ("broker", ""))
    expected_award_amountPerformance = award_amount_performance
    expected_award_amount = award_amount

    def setUp(self):
        super().setUp()

        self.prepare_award()
        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.app.authorization = ("Basic", ("broker", ""))

    test_patch_tender_award = snitch(patch_tender_lot_award)
    test_check_tender_award_complaint_period_dates = snitch(check_tender_award_complaint_period_dates)


@mock.patch(
    "openprocurement.tender.core.procedure.state.award.QUALIFICATION_AFTER_COMPLAINT_FROM",
    get_now() - timedelta(days=1),
)
class TenderAwardQualificationAfterComplaint(TenderAwardQualificationAfterComplaintMixin, BaseESCOContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_esco_bids
    initial_lots = test_tender_esco_lots
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]


class Tender2LotAwardResourceTest(BaseESCOContentWebTest, Tender2LotAwardResourceTestMixin):
    initial_status = "active.tendering"
    initial_lots = 2 * test_tender_esco_lots
    initial_bids = test_tender_esco_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.app.authorization = ("Basic", ("broker", ""))


class TenderAwardComplaintResourceTest(
    BaseESCOContentWebTest, TenderAwardComplaintResourceTestMixin, TenderUAAwardComplaintResourceTestMixin
):
    # initial_data = tender_data
    initial_status = "active.tendering"
    initial_bids = test_tender_esco_bids
    initial_lots = 2 * test_tender_esco_lots
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.app.authorization = ("Basic", ("broker", ""))
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


class TenderLotAwardComplaintResourceTest(BaseESCOContentWebTest, TenderLotAwardComplaintResourceTestMixin):
    # initial_data = tender_data
    initial_status = "active.tendering"
    initial_lots = test_tender_esco_lots
    initial_bids = test_tender_esco_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

        self.prepare_award()

        # Create award
        self.app.authorization = ("Basic", ("token", ""))
        bid = self.initial_bids[0]
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "status": "pending",
                    "bid_id": bid["id"],
                    "lotID": bid["lotValues"][0]["relatedLot"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.authorization = ("Basic", ("broker", ""))
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


class Tender2LotAwardComplaintResourceTest(
    TenderLotAwardComplaintResourceTest, Tender2LotAwardComplaintResourceTestMixin
):
    initial_lots = 2 * test_tender_esco_lots


class Tender2LotAwardQualificationAfterComplaintResourceTest(
    BaseESCOContentWebTest, Tender2LotAwardQualificationAfterComplaintMixin
):
    initial_bids = test_tender_esco_bids
    initial_lots = 2 * test_tender_esco_lots
    initial_status = "active.qualification"
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_below_supplier],
                        "status": "pending",
                        "bid_id": self.initial_bids[0]["id"],
                        "lotID": self.initial_bids[0]["lotValues"][0]["relatedLot"],
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]


class TenderAwardComplaintDocumentResourceTest(BaseESCOContentWebTest, TenderAwardComplaintDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_esco_bids

    def setUp(self):
        super().setUp()
        # Create award
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_tender_below_supplier],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.authorization = ("Basic", ("broker", ""))
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        # Create complaint for award
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(
                self.tender_id, self.award_id, list(self.initial_bids_tokens.values())[0]
            ),
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class Tender2LotAwardComplaintDocumentResourceTest(BaseESCOContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_esco_bids
    initial_lots = 2 * test_tender_esco_lots

    def setUp(self):
        super().setUp()
        # Create award
        bid = self.initial_bids[0]
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_below_supplier],
                        "status": "pending",
                        "bid_id": bid["id"],
                        "lotID": bid["lotValues"][0]["relatedLot"],
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(
                self.tender_id, self.award_id, list(self.initial_bids_tokens.values())[0]
            ),
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_create_tender_award_complaint_document = snitch(create_tender_2lot_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_2lot_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_2lot_award_complaint_document)


class TenderAwardDocumentResourceTest(BaseESCOContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_esco_bids

    def setUp(self):
        super().setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_below_supplier],
                        "status": "pending",
                        "bid_id": self.initial_bids[0]["id"],
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]

    test_create_tender_award_document_json_bulk = snitch(create_tender_award_document_json_bulk)


class Tender2LotAwardDocumentResourceTest(BaseESCOContentWebTest, Tender2LotAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_esco_bids
    initial_lots = 2 * test_tender_esco_lots

    def setUp(self):
        super().setUp()
        # Create award
        bid = self.initial_bids[0]
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_below_supplier],
                        "status": "pending",
                        "bid_id": bid["id"],
                        "lotID": bid["lotValues"][0]["relatedLot"],
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")

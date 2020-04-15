# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from datetime import timedelta
import dateutil

import mock
from esculator import npv, escp
from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    create_tender_award_with_scale_not_required,
    create_tender_award_no_scale,
    patch_tender_lot_award_lots_none,
)
from openprocurement.tender.esco.adapters import TenderESCOConfigurator
from openprocurement.tender.belowthreshold.tests.base import test_organization, test_draft_complaint
from openprocurement.tender.belowthreshold.tests.award import (
    TenderLotAwardCheckResourceTestMixin,
    TenderAwardComplaintResourceTestMixin,
    TenderAwardDocumentResourceTestMixin,
    TenderAwardComplaintDocumentResourceTestMixin,
    Tender2LotAwardDocumentResourceTestMixin,
)

from openprocurement.tender.openua.tests.award import TenderUAAwardComplaintResourceTestMixin

from openprocurement.tender.openeu.tests.award import (
    TenderAwardResourceTestMixin,
    TenderLotAwardResourceTestMixin,
    Tender2LotAwardResourceTestMixin,
    TenderLotAwardComplaintResourceTestMixin,
    Tender2LotAwardComplaintResourceTestMixin,
)
from openprocurement.tender.openeu.tests.award_blanks import (
    # Tender2LotAwardComplaintDocumentResourceTest
    patch_tender_award_complaint_document,
    # TenderAwardComplaintDocumentResourceTest
    create_tender_2lot_award_complaint_document,
    put_tender_2lot_award_complaint_document,
    patch_tender_2lot_award_complaint_document,
    check_tender_award_complaint_period_dates,
)

# from openprocurement.tender.openua.tests.award_blanks import che

from openprocurement.tender.esco.tests.base import BaseESCOContentWebTest, test_bids, test_lots, NBU_DISCOUNT_RATE

from openprocurement.tender.esco.tests.award_blanks import (
    patch_tender_award,
    patch_tender_lot_award,
)
from openprocurement.tender.esco.utils import to_decimal


award_amountPerformance = round(
    to_decimal(
        npv(
            test_bids[0]["value"]["contractDuration"]["years"],
            test_bids[0]["value"]["contractDuration"]["days"],
            test_bids[0]["value"]["yearlyPaymentsPercentage"],
            test_bids[0]["value"]["annualCostsReduction"],
            get_now(),
            NBU_DISCOUNT_RATE,
        )
    ),
    2,
)

award_amount = round(
    to_decimal(
        escp(
            test_bids[0]["value"]["contractDuration"]["years"],
            test_bids[0]["value"]["contractDuration"]["days"],
            test_bids[0]["value"]["yearlyPaymentsPercentage"],
            test_bids[0]["value"]["annualCostsReduction"],
            get_now(),
        )
    ),
    2,
)


class TenderAwardResourceTest(BaseESCOContentWebTest, TenderAwardResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = test_bids
    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))
    expected_award_amountPerformance = award_amountPerformance
    expected_award_amount = award_amount

    def setUp(self):
        super(TenderAwardResourceTest, self).setUp()
        # switch to active.pre-qualification

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.app.authorization = ("Basic", ("broker", ""))
        self.old_complaint_period_start_date = dateutil.parser.parse(
            response.json["data"][0]["complaintPeriod"]["startDate"])

    test_patch_tender_award = snitch(patch_tender_award)
    test_check_tender_award_complaint_period_dates = snitch(check_tender_award_complaint_period_dates)


class TenderAwardResourceScaleTest(BaseESCOContentWebTest):
    initial_status = "active.qualification"

    def setUp(self):
        patcher = mock.patch("openprocurement.api.models.ORGANIZATION_SCALE_FROM", get_now() + timedelta(days=1))
        patcher.start()
        self.addCleanup(patcher.stop)
        test_bid = deepcopy(test_bids[0])
        test_bid["tenderers"][0].pop("scale")
        self.initial_bids = [test_bid]
        super(TenderAwardResourceScaleTest, self).setUp()
        self.app.authorization = ("Basic", ("token", ""))

    test_create_tender_award_with_scale_not_required = snitch(create_tender_award_with_scale_not_required)
    test_create_tender_award_with_no_scale = snitch(create_tender_award_no_scale)


class TenderLotAwardCheckResourceTest(BaseESCOContentWebTest, TenderLotAwardCheckResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = deepcopy(test_bids)
    initial_bids.append(deepcopy(test_bids[0]))
    initial_bids[1]["tenderers"][0]["name"] = u"Не зовсім Державне управління справами"
    initial_bids[1]["tenderers"][0]["identifier"]["id"] = u"88837256"
    initial_bids[2]["tenderers"][0]["name"] = u"Точно не Державне управління справами"
    initial_bids[2]["tenderers"][0]["identifier"]["id"] = u"44437256"
    initial_bids[1]["value"] = {
        "yearlyPaymentsPercentage": 0.9,
        "annualCostsReduction": [100] * 21,
        "contractDuration": {"years": 2, "days": 10},
    }
    reverse = TenderESCOConfigurator.reverse_awarding_criteria
    awarding_key = TenderESCOConfigurator.awarding_criteria_key

    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderLotAwardCheckResourceTest, self).setUp()
        # switch to active.pre-qualification

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.app.authorization = ("Basic", ("broker", ""))


class TenderLotAwardResourceTest(BaseESCOContentWebTest, TenderLotAwardResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = test_bids
    initial_lots = test_lots
    initial_auth = ("Basic", ("broker", ""))
    expected_award_amountPerformance = award_amountPerformance
    expected_award_amount = award_amount

    def setUp(self):
        super(TenderLotAwardResourceTest, self).setUp()

        self.prepare_award()
        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.app.authorization = ("Basic", ("broker", ""))

    test_patch_tender_award = snitch(patch_tender_lot_award)


class Tender2LotAwardResourceTest(BaseESCOContentWebTest, Tender2LotAwardResourceTestMixin):
    initial_status = "active.tendering"
    initial_lots = 2 * test_lots
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(Tender2LotAwardResourceTest, self).setUp()

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
    initial_bids = test_bids
    initial_lots = 2 * test_lots
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderAwardComplaintResourceTest, self).setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.app.authorization = ("Basic", ("broker", ""))
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


class TenderLotAwardComplaintResourceTest(BaseESCOContentWebTest, TenderLotAwardComplaintResourceTestMixin):
    # initial_data = tender_data
    initial_status = "active.tendering"
    initial_lots = test_lots
    initial_bids = test_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderLotAwardComplaintResourceTest, self).setUp()

        self.prepare_award()

        # Create award
        self.app.authorization = ("Basic", ("token", ""))
        bid = self.initial_bids[0]
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "bid_id": bid["id"],
                    "lotID": bid["lotValues"][0]["relatedLot"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.authorization = ("Basic", ("broker", ""))
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


class Tender2LotAwardComplaintResourceTest(
    TenderLotAwardComplaintResourceTest, Tender2LotAwardComplaintResourceTestMixin
):
    initial_lots = 2 * test_lots


class TenderAwardComplaintDocumentResourceTest(BaseESCOContentWebTest, TenderAwardComplaintDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {"data": {"suppliers": [test_organization], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        # Create complaint for award
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(
                self.tender_id, self.award_id,
                self.initial_bids_tokens.values()[0]
            ),
            {"data": test_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class Tender2LotAwardComplaintDocumentResourceTest(BaseESCOContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        self.app.authorization = ("Basic", ("token", ""))
        bid = self.initial_bids[0]
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_organization],
                    "status": "pending",
                    "bid_id": bid["id"],
                    "lotID": bid["lotValues"][0]["relatedLot"],
                }
            },
        )
        award = response.json["data"]
        self.award_id = award["id"]
        self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(
                self.tender_id, self.award_id,
                self.initial_bids_tokens.values()[0]
            ),
            {"data": test_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_create_tender_award_complaint_document = snitch(create_tender_2lot_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_2lot_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_2lot_award_complaint_document)


class TenderAwardDocumentResourceTest(BaseESCOContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids

    def setUp(self):
        super(TenderAwardDocumentResourceTest, self).setUp()
        # Create award
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {"data": {"suppliers": [test_organization], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
        )
        award = response.json["data"]
        self.award_id = award["id"]


class Tender2LotAwardDocumentResourceTest(BaseESCOContentWebTest, Tender2LotAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_bids
    initial_lots = 2 * test_lots

    def setUp(self):
        super(Tender2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        self.app.authorization = ("Basic", ("token", ""))
        bid = self.initial_bids[0]
        response = self.app.post_json(
            "/tenders/{}/awards".format(self.tender_id),
            {
                "data": {
                    "suppliers": [test_organization],
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
    suite.addTest(unittest.makeSuite(TenderAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAwardResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(Tender2LotAwardDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")

import unittest
from datetime import timedelta
from unittest import mock

from openprocurement.api.tests.base import change_auth, snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.arma.tests.award_blanks import (
    create_tender_2lot_award,
    create_tender_award_invalid,
    create_tender_lot_award,
    get_tender_award,
    patch_tender_2lot_award,
    patch_tender_award_active,
    patch_tender_lot_award,
    patch_tender_lot_award_unsuccessful,
    prolongation_award,
)
from openprocurement.tender.arma.tests.base import (
    BaseTenderContentWebTest,
    test_tender_arma_bids,
    test_tender_arma_lots,
    test_tender_arma_three_bids,
)
from openprocurement.tender.belowthreshold.tests.award import (
    Tender2LotAwardDocumentResourceTestMixin,
    TenderAwardDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    patch_tender_lot_award_lots_none,
)
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_supplier
from openprocurement.tender.open.tests.award_blanks import (
    award_sign,
    patch_tender_award_unsuccessful_first,
    patch_tender_award_unsuccessful_forbidden,
    patch_tender_award_unsuccessful_second,
)
from openprocurement.tender.openua.tests.award_blanks import (
    create_tender_award_no_scale_invalid,
)


@mock.patch(
    "openprocurement.tender.core.procedure.state.award.QUALIFICATION_AFTER_COMPLAINT_FROM",
    get_now() - timedelta(days=1),
)
class TenderAwardQualificationResourceTest(BaseTenderContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_arma_three_bids
    initial_lots = test_tender_arma_lots
    initial_auth = ("Basic", ("broker", ""))

    test_patch_tender_award_unsuccessful_first = snitch(patch_tender_award_unsuccessful_first)
    test_patch_tender_award_unsuccessful_second = snitch(patch_tender_award_unsuccessful_second)
    test_patch_tender_award_unsuccessful_forbidden = snitch(patch_tender_award_unsuccessful_forbidden)

    def setUp(self):
        super().setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]


@mock.patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class TenderLotAwardResourceTestMixin:
    test_create_tender_award = snitch(create_tender_lot_award)
    test_patch_tender_award = snitch(patch_tender_lot_award)
    test_patch_tender_award_unsuccessful = snitch(patch_tender_lot_award_unsuccessful)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)
    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_patch_tender_award_active = snitch(patch_tender_award_active)
    test_get_tender_award = snitch(get_tender_award)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)


class TenderLotAwardResourceTest(BaseTenderContentWebTest, TenderLotAwardResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = test_tender_arma_bids
    initial_lots = test_tender_arma_lots
    initial_auth = ("Basic", ("broker", ""))
    expected_award_amount = test_tender_arma_bids[0]["value"]["amount"]

    def setUp(self):
        super().setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.app.authorization = ("Basic", ("broker", ""))

    test_award_sign = snitch(award_sign)
    test_prolongation_award = snitch(prolongation_award)


class Tender2LotAwardResourceTestMixin:
    test_create_tender_award = snitch(create_tender_2lot_award)
    test_patch_tender_award = snitch(patch_tender_2lot_award)


class Tender2LotAwardResourceTest(BaseTenderContentWebTest, Tender2LotAwardResourceTestMixin):
    initial_status = "active.tendering"
    initial_lots = 2 * test_tender_arma_lots
    initial_bids = test_tender_arma_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.app.authorization = ("Basic", ("broker", ""))


class TenderAwardDocumentResourceTest(BaseTenderContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_arma_bids
    initial_auth = ("Basic", ("broker", ""))

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


class Tender2LotAwardDocumentResourceTest(BaseTenderContentWebTest, Tender2LotAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_arma_bids
    initial_lots = 2 * test_tender_arma_lots
    initial_auth = ("Basic", ("broker", ""))

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
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardQualificationResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardDocumentResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")

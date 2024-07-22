import unittest
from datetime import timedelta
from unittest import mock

from openprocurement.api.tests.base import change_auth, snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.award import (
    Tender2LotAwardDocumentResourceTestMixin,
    TenderAwardComplaintDocumentResourceTestMixin,
    TenderAwardComplaintResourceTestMixin,
    TenderAwardDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
    patch_tender_lot_award_lots_none,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
    test_tender_below_organization,
)
from openprocurement.tender.open.tests.award import (
    Tender2LotAwardQualificationAfterComplaintMixin,
    TenderAwardQualificationAfterComplaintMixin,
)
from openprocurement.tender.open.tests.award_blanks import (
    patch_tender_award_unsuccessful_complaint_first,
    patch_tender_award_unsuccessful_complaint_second,
)
from openprocurement.tender.openeu.tests.award_blanks import (
    check_tender_award_complaint_period_dates,
    create_tender_2lot_award,
    create_tender_2lot_award_complaint_document,
    create_tender_award_invalid,
    create_tender_lot_award,
    get_tender_award,
    patch_tender_2lot_award,
    patch_tender_2lot_award_complaint_document,
    patch_tender_award_active,
    patch_tender_award_complaint_document,
    patch_tender_lot_award,
    patch_tender_lot_award_unsuccessful,
    put_tender_2lot_award_complaint_document,
)
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_tender_openeu_bids,
    test_tender_openeu_lots,
    test_tender_openeu_three_bids,
)
from openprocurement.tender.openua.tests.award import (
    TenderUAAwardComplaintResourceTestMixin,
)
from openprocurement.tender.openua.tests.award_blanks import (
    create_tender_award_no_scale_invalid,
    create_tender_lot_award_complaint,
    create_tender_lots_award_complaint,
    patch_tender_lot_award_complaint,
    patch_tender_lots_award_complaint,
)


@mock.patch(
    "openprocurement.tender.core.procedure.state.award.QUALIFICATION_AFTER_COMPLAINT_FROM",
    get_now() - timedelta(days=1),
)
class TenderAwardQualificationAfterComplaint(TenderAwardQualificationAfterComplaintMixin, BaseTenderContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_openeu_three_bids
    initial_lots = test_tender_openeu_lots
    initial_auth = ("Basic", ("broker", ""))

    test_patch_tender_award_unsuccessful_complaint_first = snitch(patch_tender_award_unsuccessful_complaint_first)
    test_patch_tender_award_unsuccessful_complaint_second = snitch(patch_tender_award_unsuccessful_complaint_second)

    def setUp(self):
        super().setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]


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
    initial_bids = test_tender_openeu_bids
    initial_lots = test_tender_openeu_lots
    initial_auth = ("Basic", ("broker", ""))
    expected_award_amount = test_tender_openeu_bids[0]["value"]["amount"]

    def setUp(self):
        super().setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        self.app.authorization = ("Basic", ("broker", ""))

    test_check_tender_award_complaint_period_dates = snitch(check_tender_award_complaint_period_dates)


class Tender2LotAwardResourceTestMixin:
    test_create_tender_award = snitch(create_tender_2lot_award)
    test_patch_tender_award = snitch(patch_tender_2lot_award)


class Tender2LotAwardResourceTest(BaseTenderContentWebTest, Tender2LotAwardResourceTestMixin):
    initial_status = "active.tendering"
    initial_lots = 2 * test_tender_openeu_lots
    initial_bids = test_tender_openeu_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

        self.prepare_award()

        # Get award
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.award_id = response.json["data"][0]["id"]
        self.app.authorization = ("Basic", ("broker", ""))


class TenderAwardComplaintResourceTest(
    BaseTenderContentWebTest, TenderAwardComplaintResourceTestMixin, TenderUAAwardComplaintResourceTestMixin
):
    # initial_data = tender_data
    initial_status = "active.tendering"
    initial_bids = test_tender_openeu_bids
    initial_lots = 2 * test_tender_openeu_lots
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

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


class TenderLotAwardComplaintResourceTestMixin:
    test_create_tender_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_lot_award_complaints)


class TenderLotAwardComplaintResourceTest(BaseTenderContentWebTest, TenderLotAwardComplaintResourceTestMixin):
    # initial_data = tender_data
    initial_status = "active.tendering"
    initial_lots = test_tender_openeu_lots
    initial_bids = test_tender_openeu_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

        self.prepare_award()

        # Create award
        bid = self.initial_bids[0]
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_below_organization],
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
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


class Tender2LotAwardComplaintResourceTestMixin:
    test_create_tender_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lots_award_complaint)


class Tender2LotAwardComplaintResourceTest(
    TenderLotAwardComplaintResourceTest, Tender2LotAwardComplaintResourceTestMixin
):
    initial_lots = 2 * test_tender_openeu_lots


class Tender2LotAwardQualificationAfterComplaintResourceTest(
    BaseTenderContentWebTest, Tender2LotAwardQualificationAfterComplaintMixin
):
    initial_bids = test_tender_openeu_bids
    initial_lots = 2 * test_tender_openeu_lots
    initial_status = "active.qualification"
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()

        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_below_organization],
                        "status": "pending",
                        "bid_id": self.initial_bids[0]["id"],
                        "lotID": self.initial_bids[0]["lotValues"][0]["relatedLot"],
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]


class TenderAwardComplaintDocumentResourceTest(BaseTenderContentWebTest, TenderAwardComplaintDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_openeu_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_below_organization],
                        "status": "pending",
                        "bid_id": self.initial_bids[0]["id"],
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
            f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints?acc_token={list(self.initial_bids_tokens.values())[0]}",
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class Tender2LotAwardComplaintDocumentResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_openeu_bids
    initial_lots = 2 * test_tender_openeu_lots
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
                        "suppliers": [test_tender_below_organization],
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
            f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints?acc_token={list(self.initial_bids_tokens.values())[0]}",
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_create_tender_award_complaint_document = snitch(create_tender_2lot_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_2lot_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_2lot_award_complaint_document)


class TenderAwardDocumentResourceTest(BaseTenderContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_openeu_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_below_organization],
                        "status": "pending",
                        "bid_id": self.initial_bids[0]["id"],
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]


class Tender2LotAwardDocumentResourceTest(BaseTenderContentWebTest, Tender2LotAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_openeu_bids
    initial_lots = 2 * test_tender_openeu_lots
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
                        "suppliers": [test_tender_below_organization],
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
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotAwardResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")

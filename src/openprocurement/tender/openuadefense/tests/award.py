import unittest

from parameterized import parameterized

from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.award import (
    TenderAwardDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    create_tender_award_complaint_document,
    create_tender_award_complaint_invalid,
    create_tender_award_document_json_bulk,
    create_tender_award_invalid,
    create_tender_lots_award_complaint_document,
    create_tender_lots_award_document,
    get_tender_award,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    not_found as complaint_docs_not_found,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    patch_tender_lot_award_lots_none,
    patch_tender_lots_award_document,
    put_tender_award_complaint_document,
    put_tender_lots_award_document,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
    test_tender_below_lots,
    test_tender_below_organization,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.open.tests.award import (
    Tender2LotAwardQualificationAfterComplaintMixin,
)
from openprocurement.tender.openua.tests.award_blanks import (
    bot_patch_tender_award_complaint,
    bot_patch_tender_award_complaint_forbidden,
    create_tender_award_complaint,
    create_tender_award_complaint_not_active,
    create_tender_award_no_scale_invalid,
    create_tender_lot_award,
    create_tender_lot_award_complaint,
    create_tender_lots_award,
    create_tender_lots_award_complaint,
    patch_tender_award_complaint,
    patch_tender_award_complaint_document,
    patch_tender_lot_award,
    patch_tender_lot_award_complaint,
    patch_tender_lots_award,
    patch_tender_lots_award_complaint_document,
    put_tender_lots_award_complaint_document,
    review_tender_award_complaint,
    review_tender_award_stopping_complaint,
)
from openprocurement.tender.openuadefense.tests.award_blanks import (
    check_tender_award_complaint_period_dates_after_new,
    check_tender_award_complaint_period_dates_before_new,
    check_tender_award_complaint_period_dates_new,
    create_tender_award_claim,
    create_tender_award_claim_denied,
    get_tender_award_complaint,
    get_tender_award_complaints,
    get_tender_lot_award_complaint,
    get_tender_lot_award_complaints,
    patch_tender_award_active_after_new,
    patch_tender_award_active_before_new,
    patch_tender_award_active_new,
    patch_tender_award_unsuccessful_after_new,
    patch_tender_award_unsuccessful_before_new,
    patch_tender_award_unsuccessful_new,
    patch_tender_lot_award_unsuccessful_after_new,
    patch_tender_lot_award_unsuccessful_before_new,
    patch_tender_lot_award_unsuccessful_new,
    patch_tender_lots_award_complaint,
    review_tender_award_claim,
    tender_award_complaint_period,
    tender_award_complaint_period_params,
)
from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    BaseTenderUAWebTest,
    test_tender_openuadefense_bids,
)


class TenderAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_openuadefense_bids

    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_check_tender_award_complaint_period_dates_before_new = snitch(
        check_tender_award_complaint_period_dates_before_new
    )
    test_check_tender_award_complaint_period_dates_after_new = snitch(
        check_tender_award_complaint_period_dates_after_new
    )
    test_check_tender_award_complaint_period_dates_new = snitch(check_tender_award_complaint_period_dates_new)
    test_patch_tender_award_active_before_new = snitch(patch_tender_award_active_before_new)
    test_patch_tender_award_active_after_new = snitch(patch_tender_award_active_after_new)
    test_patch_tender_award_active_new = snitch(patch_tender_award_active_new)
    test_patch_tender_award_unsuccessful_before_new = snitch(patch_tender_award_unsuccessful_before_new)
    test_patch_tender_award_unsuccessful_after_new = snitch(patch_tender_award_unsuccessful_after_new)
    test_patch_tender_award_unsuccessful_new = snitch(patch_tender_award_unsuccessful_new)
    test_get_tender_award = snitch(get_tender_award)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)


class TenderAwardResourceComplaintPeriodTest(BaseTenderUAWebTest):
    initial_status = "active.qualification"
    initial_bid_status = "pending"
    initial_bids = test_tender_openuadefense_bids

    @parameterized.expand(tender_award_complaint_period_params)
    def test_tender_award_complaint_period(self, name, date_str, expected_date_str, expected_sb_date_str):
        tender_award_complaint_period(
            self,
            parse_date(date_str),
            parse_date(expected_date_str),
            parse_date(expected_sb_date_str),
        )


class TenderLotAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_openuadefense_bids

    test_create_tender_award = snitch(create_tender_lot_award)
    test_patch_tender_award = snitch(patch_tender_lot_award)
    test_patch_tender_award_unsuccessful_before_new = snitch(patch_tender_lot_award_unsuccessful_before_new)
    test_patch_tender_award_unsuccessful_after_new = snitch(patch_tender_lot_award_unsuccessful_after_new)
    test_patch_tender_award_unsuccessful_new = snitch(patch_tender_lot_award_unsuccessful_new)
    test_patch_tender_lot_award_lots_none = snitch(patch_tender_lot_award_lots_none)


class Tender2LotAwardResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_lots = 2 * test_tender_below_lots
    initial_bids = test_tender_openuadefense_bids

    test_create_tender_award = snitch(create_tender_lots_award)
    test_patch_tender_award = snitch(patch_tender_lots_award)


class TenderAwardPendingResourceTestCase(BaseTenderUAContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_openuadefense_bids

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
                        "lotID": self.initial_bids[0]["lotValues"][0]["relatedLot"] if self.initial_lots else None,
                    }
                },
            )
        award = response.json["data"]
        self.award_id = award["id"]


class TenderAwardActiveResourceTestCase(TenderAwardPendingResourceTestCase):
    def setUp(self):
        super().setUp()
        with change_auth(self.app, ("Basic", ("token", ""))):
            self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, self.award_id),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
        self.bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]


class TenderAwardComplaintResourceTest(TenderAwardActiveResourceTestCase):
    test_create_tender_award_complaint_invalid = snitch(create_tender_award_complaint_invalid)
    test_create_tender_award_claim = snitch(create_tender_award_claim)
    test_create_tender_award_claim_denied = snitch(create_tender_award_claim_denied)
    test_create_tender_award_complaint_not_active = snitch(create_tender_award_complaint_not_active)
    test_create_tender_award_complaint = snitch(create_tender_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_award_complaint)
    test_review_tender_award_complaint = snitch(review_tender_award_complaint)
    test_review_tender_award_stopping_complaint = snitch(review_tender_award_stopping_complaint)
    test_review_tender_award_claim = snitch(review_tender_award_claim)
    test_get_tender_award_complaint = snitch(get_tender_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_award_complaints)
    test_bot_patch_tender_award_complaint = snitch(bot_patch_tender_award_complaint)
    test_bot_patch_tender_award_complaint_forbidden = snitch(bot_patch_tender_award_complaint_forbidden)


class TenderLotAwardComplaintResourceTest(TenderAwardActiveResourceTestCase):
    initial_lots = test_tender_below_lots

    test_create_tender_award_complaint = snitch(create_tender_lot_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lot_award_complaint)
    test_get_tender_award_complaint = snitch(get_tender_lot_award_complaint)
    test_get_tender_award_complaints = snitch(get_tender_lot_award_complaints)


class Tender2LotAwardComplaintResourceTest(TenderLotAwardComplaintResourceTest):
    initial_lots = 2 * test_tender_below_lots

    test_create_tender_award_complaint = snitch(create_tender_lots_award_complaint)
    test_patch_tender_award_complaint = snitch(patch_tender_lots_award_complaint)


class TenderAwardComplaintDocumentResourceTest(TenderAwardActiveResourceTestCase):
    def setUp(self):
        super().setUp()

        # Create complaint for award
        bid_token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, bid_token),
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_not_found = snitch(complaint_docs_not_found)
    test_create_tender_award_complaint_document = snitch(create_tender_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_award_complaint_document)


class Tender2LotAwardComplaintDocumentResourceTest(TenderAwardActiveResourceTestCase):
    initial_lots = 2 * test_tender_below_lots

    def setUp(self):
        super().setUp()
        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, self.bid_token),
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_create_tender_award_complaint_document = snitch(create_tender_lots_award_complaint_document)
    test_put_tender_award_complaint_document = snitch(put_tender_lots_award_complaint_document)
    test_patch_tender_award_complaint_document = snitch(patch_tender_lots_award_complaint_document)


class TenderAwardDocumentResourceTest(TenderAwardPendingResourceTestCase, TenderAwardDocumentResourceTestMixin):
    test_create_tender_award_document_json_bulk = snitch(create_tender_award_document_json_bulk)


class Tender2LotAwardDocumentResourceTest(TenderAwardPendingResourceTestCase):
    initial_lots = 2 * test_tender_below_lots

    test_create_tender_award_document = snitch(create_tender_lots_award_document)
    test_put_tender_award_document = snitch(put_tender_lots_award_document)
    test_patch_tender_award_document = snitch(patch_tender_lots_award_document)


class Tender2LotAwardQualificationAfterComplaintResourceTest(
    Tender2LotAwardQualificationAfterComplaintMixin, TenderAwardPendingResourceTestCase
):
    initial_lots = 2 * test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Tender2LotAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardComplaintResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotAwardResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")

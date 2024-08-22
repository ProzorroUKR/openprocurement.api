import unittest
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.award import (
    TenderAwardDocumentResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.award_blanks import (
    create_tender_award_no_scale_invalid,
    get_tender_award,
)
from openprocurement.tender.pricequotation.tests.award_blanks import (
    check_tender_award,
    check_tender_award_cancellation,
    create_tender_award,
    create_tender_award_invalid,
    move_award_contract_to_contracting,
    patch_tender_award,
    tender_award_transitions,
)
from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest,
    test_tender_pq_bids,
)


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class TenderAwardResourceTestMixin:
    test_create_tender_award_invalid = snitch(create_tender_award_invalid)
    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)
    test_get_tender_award = snitch(get_tender_award)


class TenderAwardResourceTest(TenderContentWebTest, TenderAwardResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_pq_bids
    reverse = False

    test_create_tender_award = snitch(create_tender_award)
    test_patch_tender_award = snitch(patch_tender_award)
    test_tender_award_transitions = snitch(tender_award_transitions)
    test_check_tender_award = snitch(check_tender_award)
    test_check_tender_award_cancellation = snitch(check_tender_award_cancellation)
    test_move_award_contract_to_contracting = snitch(move_award_contract_to_contracting)


class TenderAwardResourceScaleTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_pq_bids
    reverse = False

    test_create_tender_award_no_scale_invalid = snitch(create_tender_award_no_scale_invalid)


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class TenderAwardDocumentResourceTest(TenderContentWebTest, TenderAwardDocumentResourceTestMixin):
    initial_status = "active.qualification"
    initial_bids = test_tender_pq_bids

    def setUp(self):
        super().setUp()
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        self.awards_ids = [award["id"] for award in response.json["data"]]

    @property
    def award_id(self):
        data = self.mongodb.tenders.get(self.tender_id)
        return data['awards'][-1]['id'] if data.get('awards') else None


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAwardResourceScaleTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")

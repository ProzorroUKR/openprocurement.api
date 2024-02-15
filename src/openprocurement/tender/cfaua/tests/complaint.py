# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_draft_complaint,
)

from openprocurement.tender.belowthreshold.tests.complaint import TenderComplaintResourceTestMixin
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    not_found,
    create_tender_complaint_document,
)
from openprocurement.tender.open.tests.complaint import (
    ComplaintObjectionMixin,
    TenderComplaintObjectionMixin,
    TenderCancellationComplaintObjectionMixin,
    TenderAwardComplaintObjectionMixin,
)

from openprocurement.tender.openua.tests.complaint import TenderUAComplaintResourceTestMixin
from openprocurement.tender.openua.tests.complaint_blanks import (
    patch_tender_complaint_document,
)

from openprocurement.tender.openeu.tests.complaint_blanks import (
    put_tender_complaint_document,
)
from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_tender_cfaua_lots,
    test_tender_cfaua_bids,
)

from openprocurement.tender.cfaua.tests.complaint_blanks import (
    create_tender_complaint,
    create_tender_lot_complaint,
)


class TenderComplaintResourceTest(
    BaseTenderContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin
):
    initial_auth = ("Basic", ("broker", ""))
    test_author = test_tender_below_author

    test_create_tender_complaint = snitch(create_tender_complaint)


class TenderLotAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_lots = test_tender_cfaua_lots
    test_author = test_tender_below_author
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender_complaint = snitch(create_tender_lot_complaint)


class TenderComplaintDocumentResourceTest(BaseTenderContentWebTest):
    test_author = test_tender_below_author
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderComplaintDocumentResourceTest, self).setUp()
        # Create complaint
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {"data": test_tender_below_draft_complaint},
        )
        complaint = response.json["data"]
        self.complaint_id = complaint["id"]
        self.complaint_owner_token = response.json["access"]["token"]

    test_not_found = snitch(not_found)
    test_create_tender_complaint_document = snitch(create_tender_complaint_document)
    test_put_tender_complaint_document = snitch(put_tender_complaint_document)
    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document)


class TenderComplaintObjectionTest(
    BaseTenderContentWebTest,
    TenderComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.tendering"  # 'active.pre-qualification.stand-still' status sets in setUp
    initial_bids = test_tender_cfaua_bids
    initial_auth = ("Basic", ("broker", ""))
    author_data = test_tender_below_author


class TenderCancellationComplaintObjectionTest(
    BaseTenderContentWebTest,
    TenderCancellationComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True

    def setUp(self):
        super(TenderCancellationComplaintObjectionTest, self).setUp()
        self.set_complaint_period_end()
        self.create_cancellation()


class TenderAwardComplaintObjectionTest(
    BaseTenderContentWebTest,
    TenderAwardComplaintObjectionMixin,
    ComplaintObjectionMixin,
):
    docservice = True
    initial_status = "active.qualification.stand-still"
    initial_lots = test_tender_cfaua_lots
    initial_bids = test_tender_cfaua_bids
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderAwardComplaintObjectionTest, self).setUp()
        response = self.app.get(f"/tenders/{self.tender_id}/awards")
        self.awards_ids = [award["id"] for award in response.json["data"]]
        self.award_id = self.awards_ids[0]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintObjectionTest))
    suite.addTest(unittest.makeSuite(TenderCancellationComplaintObjectionTest))
    suite.addTest(unittest.makeSuite(TenderAwardComplaintObjectionTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")

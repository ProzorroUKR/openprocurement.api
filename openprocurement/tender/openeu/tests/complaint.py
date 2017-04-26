# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.complaint import TenderComplaintResourceTestMixin
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    # TenderComplaintDocumentResourceTest
    not_found,
    create_tender_complaint_document,
)

from openprocurement.tender.openua.tests.complaint import TenderUAComplaintResourceTestMixin
from openprocurement.tender.openua.tests.complaint_blanks import (
    # TenderComplaintDocumentResourceTest
    patch_tender_complaint_document,
    # TenderLotAwardComplaintResourceTest
    create_tender_lot_award_complaint,
)

from openprocurement.tender.openeu.tests.complaint_blanks import (
    # TenderComplaintDocumentResourceTest
    put_tender_complaint_document,
)
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_bids,
    test_lots,
)


class TenderComplaintResourceTest(BaseTenderContentWebTest,
                                  TenderComplaintResourceTestMixin,
                                  TenderUAComplaintResourceTestMixin):
    initial_auth = ('Basic', ('broker', ''))
    test_author = test_bids[0]["tenderers"][0]


class TenderLotAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_lots = test_lots
    test_author = test_bids[0]["tenderers"][0]
    initial_auth = ('Basic', ('broker', ''))

    test_create_tender_complaint = snitch(create_tender_lot_award_complaint)


class TenderComplaintDocumentResourceTest(BaseTenderContentWebTest):

    test_author = test_bids[0]["tenderers"][0]
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderComplaintDocumentResourceTest, self).setUp()
        # Create complaint
        response = self.app.post_json('/tenders/{}/complaints'.format(
            self.tender_id), {'data': {'title': 'complaint title',
                                       'description': 'complaint description',
                                       'author': test_bids[0]["tenderers"][0]
                                       }})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_not_found = snitch(not_found)
    test_create_tender_complaint_document = snitch(create_tender_complaint_document)
    test_put_tender_complaint_document = snitch(put_tender_complaint_document)
    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

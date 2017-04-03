# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.openeu.tests.base import test_lots
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_bids,
)
from openprocurement.tender.openeu.tests.complaint_blanks import (
    # TenderComplaintDocumentResourceTest
    not_found,
    create_tender_complaint_document,
    put_tender_complaint_document,
    patch_tender_complaint_document,
    # TenderLotAwardComplaintResourceTest
    lot_create_tender_complaint,
    # TenderComplaintResourceTest
    create_tender_complaint_invalid,
    create_tender_complaint,
    patch_tender_complaint,
    review_tender_complaint,
    get_tender_complaint,
    get_tender_complaints,
)


class TenderComplaintResourceTest(BaseTenderContentWebTest):

    author = test_bids[0]["tenderers"][0]
    initial_auth = ('Basic', ('broker', ''))

    test_create_tender_complaint_invalid = snitch(create_tender_complaint_invalid)
    test_create_tender_complaint = snitch(create_tender_complaint)
    test_patch_tender_complaint = snitch(patch_tender_complaint)
    test_review_tender_complaint = snitch(review_tender_complaint)
    test_get_tender_complaint = snitch(get_tender_complaint)
    test_get_tender_complaints = snitch(get_tender_complaints)


class TenderLotAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_lots = test_lots
    author = test_bids[0]["tenderers"][0]
    initial_auth = ('Basic', ('broker', ''))

    test_create_tender_complaint = snitch(lot_create_tender_complaint)


class TenderComplaintDocumentResourceTest(BaseTenderContentWebTest):

    author = test_bids[0]["tenderers"][0]
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderComplaintDocumentResourceTest, self).setUp()
        # Create complaint
        response = self.app.post_json('/tenders/{}/complaints'.format(
            self.tender_id), {'data': {'title': 'complaint title',
                                       'description': 'complaint description',
                                       'author': self.author
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

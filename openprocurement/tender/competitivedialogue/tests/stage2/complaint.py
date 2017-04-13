# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.competitivedialogue.tests.stage2.complaint_blanks import (
    # TenderStage2UEComplaintResourceTest
    create_tender_complaint_invalid_eu,
    create_tender_complaint_eu,
    patch_tender_complaint_eu,
    review_tender_complaint_eu,
    get_tender_complaint_eu,
    get_tender_complaints_eu,
    # TenderStage2EULotAwardComplaintResourceTest
    create_tender_with_lot_complaint_eu,
    # TenderStage2EUComplaintDocumentResourceTest
    not_found_eu,
    create_tender_complaint_document_eu,
    put_tender_complaint_document_eu,
    patch_tender_complaint_document_eu,
    # TenderStage2UAComplaintResourceTest
    create_tender_complaint_invalid_ua,
    create_tender_complaint_ua,
    patch_tender_complaint_ua,
    review_tender_complaint_ua,
    get_tender_complaint_ua,
    get_tender_complaints_ua,
    # TenderStage2UALotAwardComplaintResourceTest
    create_tender_with_lot_complaint_ua,
    # TenderStage2UAComplaintDocumentResourceTest
    not_found_ua,
    create_tender_complaint_document_ua,
    put_tender_complaint_document_ua,
    patch_tender_complaint_document_ua, 
)
from openprocurement.tender.competitivedialogue.tests.base import (
    test_lots,
    test_bids,
    test_shortlistedFirms,
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest)

author = deepcopy(test_bids[0]["tenderers"][0])
author['identifier']['id'] = test_shortlistedFirms[0]['identifier']['id']
author['identifier']['scheme'] = test_shortlistedFirms[0]['identifier']['scheme']


class TenderStage2UEComplaintResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    author_data = author

    test_create_tender_complaint_invalid = snitch(create_tender_complaint_invalid_eu)

    test_create_tender_complaint = snitch(create_tender_complaint_eu)

    test_patch_tender_complaint = snitch(patch_tender_complaint_eu)

    test_review_tender_complaint = snitch(review_tender_complaint_eu)

    test_get_tender_complaint = snitch(get_tender_complaint_eu)

    test_get_tender_complaints = snitch(get_tender_complaints_eu)


class TenderStage2EULotAwardComplaintResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    author_data = author  # TODO: change attribute identifier

    test_create_tender_complaint = snitch(create_tender_with_lot_complaint_eu)


class TenderStage2EUComplaintDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderStage2EUComplaintDocumentResourceTest, self).setUp()
        # Create complaint
        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_not_found = snitch(not_found_eu)

    test_create_tender_complaint_document = snitch(create_tender_complaint_document_eu)

    test_put_tender_complaint_document  = snitch(put_tender_complaint_document_eu)

    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document_eu)


class TenderStage2UAComplaintResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    author_data = author  # TODO: change attribute identifier

    test_create_tender_complaint_invalid = snitch(create_tender_complaint_invalid_ua)

    test_create_tender_complaint = snitch(create_tender_complaint_ua)

    test_patch_tender_complaint = snitch(patch_tender_complaint_ua)

    test_review_tender_complaint = snitch(review_tender_complaint_ua)

    test_get_tender_complaint = snitch(get_tender_complaint_ua)

    test_get_tender_complaints = snitch(get_tender_complaints_ua)


class TenderStage2UALotAwardComplaintResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = test_lots
    author_data = author  # TODO: change attribute identifier

    test_create_tender_complaint = snitch(create_tender_with_lot_complaint_ua)


class TenderStage2UAComplaintDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    def setUp(self):
        super(TenderStage2UAComplaintDocumentResourceTest, self).setUp()
        # Create complaint
        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_not_found = snitch(not_found_ua)

    test_create_tender_complaint_document = snitch(create_tender_complaint_document_ua)

    test_put_tender_complaint_document  = snitch(put_tender_complaint_document_ua)

    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document_ua)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2UEComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAComplaintDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

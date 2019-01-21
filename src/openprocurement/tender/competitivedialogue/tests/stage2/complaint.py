# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.complaint import TenderComplaintResourceTestMixin
from openprocurement.tender.openua.tests.complaint import TenderUAComplaintResourceTestMixin
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    # TenderStage2EU(UA)ComplaintDocumentResourceTest
    not_found,
    create_tender_complaint_document,
)
from openprocurement.tender.openua.tests.complaint_blanks import (
    # TenderStage2EU(UA)LotAwardComplaintResourceTest
    create_tender_lot_complaint,
    # TenderStage2EU(UA)ComplaintDocumentResourceTest
    put_tender_complaint_document,
    patch_tender_complaint_document,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    test_lots,
    test_bids,
    test_shortlistedFirms,
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest
)

author = deepcopy(test_bids[0]["tenderers"][0])
author['identifier']['id'] = test_shortlistedFirms[0]['identifier']['id']
author['identifier']['scheme'] = test_shortlistedFirms[0]['identifier']['scheme']


class TenderStage2EUComplaintResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin):

    initial_auth = ('Basic', ('broker', ''))
    test_author = author


class TenderStage2EULotAwardComplaintResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_author = author  # TODO: change attribute identifier

    test_create_tender_complaint = snitch(create_tender_lot_complaint)


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

    test_not_found = snitch(not_found)
    test_create_tender_complaint_document = snitch(create_tender_complaint_document)
    test_put_tender_complaint_document = snitch(put_tender_complaint_document)
    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document)


class TenderStage2UAComplaintResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin):
    test_author = author  # TODO: change attribute identifier


class TenderStage2UALotAwardComplaintResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderStage2EULotAwardComplaintResourceTest):
    initial_lots = test_lots
    test_author = author  # TODO: change attribute identifier


class TenderStage2UAComplaintDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderStage2EUComplaintDocumentResourceTest):

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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAComplaintDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

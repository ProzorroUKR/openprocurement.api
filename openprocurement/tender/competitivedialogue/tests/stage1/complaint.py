# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUContentWebTest,
    BaseCompetitiveDialogUAContentWebTest,
    test_lots
)
from openprocurement.tender.openeu.tests.base import test_bids
from openprocurement.tender.belowthreshold.tests.complaint import (
    TenderComplaintResourceTestMixin
)
from openprocurement.tender.openua.tests.complaint import (
    TenderUAComplaintResourceTestMixin
)
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

author = test_bids[0]["tenderers"][0]


class CompetitiveDialogEUComplaintResourceTest(BaseCompetitiveDialogEUContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin):

    initial_auth = ('Basic', ('broker', ''))
    test_author = author  # TODO: change attribute identifier


class CompetitiveDialogEULotAwardComplaintResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_author = author  # TODO: change attribute identifier

    test_create_tender_complaint = snitch(create_tender_lot_complaint)


class CompetitiveDialogEUComplaintDocumentResourceTest(BaseCompetitiveDialogEUContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(CompetitiveDialogEUComplaintDocumentResourceTest, self).setUp()
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


class CompetitiveDialogUAComplaintResourceTest(BaseCompetitiveDialogUAContentWebTest, TenderComplaintResourceTestMixin, TenderUAComplaintResourceTestMixin):

    initial_auth = ('Basic', ('broker', ''))
    test_author = author  # TODO: change attribute identifier


class CompetitiveDialogUALotAwardComplaintResourceTest(BaseCompetitiveDialogUAContentWebTest):

    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_author = author  # TODO: change attribute identifier

    test_create_tender_complaint = snitch(create_tender_lot_complaint)


class CompetitiveDialogUAComplaintDocumentResourceTest(BaseCompetitiveDialogUAContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(CompetitiveDialogUAComplaintDocumentResourceTest, self).setUp()
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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUComplaintResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEULotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUAComplaintResourceTest))
    suite.addTest(unittest.makesuite(CompetitiveDialogUALotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUAComplaintDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

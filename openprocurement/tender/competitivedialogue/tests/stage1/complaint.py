# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUContentWebTest,
    BaseCompetitiveDialogUAContentWebTest,
    test_lots
)
from openprocurement.tender.competitivedialogue.tests.stage1.complaint_blanks import (
    # CompetitiveDialogEUComplaintResourceTest
    create_tender_complaint_invalid_eu,
    create_tender_complaint_eu,
    patch_tender_complaint_eu,
    review_tender_complaint_eu,
    get_tender_complaint_eu,
    get_tender_complaints_eu,
    # CompetitiveDialogEULotAwardComplaintResourceTest
    create_tender_with_lot_complaint_eu,
    # CompetitiveDialogEUComplaintDocumentResourceTest
    not_found_eu,
    create_tender_complaint_document_eu,
    put_tender_complaint_document_eu,
    patch_tender_complaint_document_eu,
    # CompetitiveDialogUAComplaintResourceTest
    create_tender_complaint_invalid_ua,
    create_tender_complaint_ua,
    patch_tender_complaint_ua,
    review_tender_complaint_ua,
    get_tender_complaint_ua,
    get_tender_complaints_ua,
    # CompetitiveDialogUALotAwardComplaintResourceTest
    create_tender_with_lot_complaint_ua,
    # CompetitiveDialogUAComplaintDocumentResourceTest
    not_found_ua,
    create_tender_complaint_document_ua,
    put_tender_complaint_document_ua,
    patch_tender_complaint_document_ua,
)

from openprocurement.tender.openeu.tests.base import test_bids
author = test_bids[0]["tenderers"][0]


class CompetitiveDialogEUComplaintResourceTest(BaseCompetitiveDialogEUContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    author_data = author  # TODO: change attribute identifier


    test_create_tender_complaint_invalid = snitch(create_tender_complaint_invalid_eu)

    test_create_tender_complaint = snitch(create_tender_complaint_eu)

    test_patch_tender_complaint = snitch(patch_tender_complaint_eu)

    test_review_tender_complaint = snitch(review_tender_complaint_eu)

    test_get_tender_complaint = snitch(get_tender_complaint_eu)

    test_get_tender_complaints = snitch(get_tender_complaints_eu)


class CompetitiveDialogEULotAwardComplaintResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    author_data = author  # TODO: change attribute identifier

    test_create_tender_complaint = snitch(create_tender_with_lot_complaint_eu)


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

    test_not_found = snitch(not_found_eu)

    test_create_tender_complaint_document = snitch(create_tender_complaint_document_eu)

    test_put_tender_complaint_document = snitch(put_tender_complaint_document_eu)

    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document_eu)


class CompetitiveDialogUAComplaintResourceTest(BaseCompetitiveDialogUAContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    author_data = author  # TODO: change attribute identifier

    test_create_tender_complaint_invalid = snitch(create_tender_complaint_invalid_ua)

    test_create_tender_complaint = snitch(create_tender_complaint_ua)

    test_patch_tender_complaint = snitch(patch_tender_complaint_ua)

    test_review_tender_complaint = snitch(review_tender_complaint_ua)

    test_get_tender_complaint = snitch(get_tender_complaint_ua)

    test_get_tender_complaints = snitch(get_tender_complaints_ua)

class CompetitiveDialogUALotAwardComplaintResourceTest(BaseCompetitiveDialogUAContentWebTest):

    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    author_data = author  # TODO: change attribute identifier

    test_create_tender_complaint = snitch(create_tender_with_lot_complaint_ua)


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

    test_not_found = snitch(not_found_ua)

    test_create_tender_complaint_document = snitch(create_tender_complaint_document_ua)

    test_put_tender_complaint_document = snitch(put_tender_complaint_document_ua)

    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document_ua)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUComplaintResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEULotAwardComplaintResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

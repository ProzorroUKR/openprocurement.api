# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogUAContentWebTest,
    BaseCompetitiveDialogEUContentWebTest,
    test_lots,
    test_bids
)

from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationResourceTestMixin,
    TenderCancellationDocumentResourceTestMixin
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    # CompetitiveDialogLotCancellationResourceTest
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
    # CompetitiveDialogUALotsCancellationResourceTest
    create_tender_lots_cancellation,
    patch_tender_lots_cancellation,
)
from openprocurement.tender.competitivedialogue.tests.stage1.cancellation_blanks import (
    cancellation_active_qualification_j1427,
)


class CompetitiveDialogUACancellationResourceTest(BaseCompetitiveDialogUAContentWebTest, TenderCancellationResourceTestMixin):
    pass


class CompetitiveDialogUALotCancellationResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = test_lots
    initial_bids = test_bids

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)
    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)


class CompetitiveDialogUALotsCancellationResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = 2 * test_lots
    initial_bids = test_bids

    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)
    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)


class CompetitiveDialogUACancellationDocumentResourceTest(BaseCompetitiveDialogUAContentWebTest, TenderCancellationDocumentResourceTestMixin):

    def setUp(self):
        super(CompetitiveDialogUACancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']


class CompetitiveDialogEUCancellationResourceTest(BaseCompetitiveDialogEUContentWebTest, TenderCancellationResourceTestMixin):

    initial_auth = ('Basic', ('broker', ''))


class CompetitiveDialogEULotCancellationResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_lots
    initial_bids = test_bids

    initial_auth = ('Basic', ('broker', ''))

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)
    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)


class CompetitiveDialogEULotsCancellationResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = 2 * test_lots
    initial_bids = test_bids
    initial_auth = ('Basic', ('broker', ''))

    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)
    test_cancellation_active_qualification_j1427 = snitch(cancellation_active_qualification_j1427)


class CompetitiveDialogEUCancellationDocumentResourceTest(BaseCompetitiveDialogEUContentWebTest, TenderCancellationDocumentResourceTestMixin):

    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(CompetitiveDialogEUCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogUACancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUALotsCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUALotCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEULotCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEULotsCancellationResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

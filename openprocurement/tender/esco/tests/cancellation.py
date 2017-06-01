# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.cancellation import (
    TenderCancellationResourceTestMixin,
    TenderCancellationDocumentResourceTestMixin
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    # TenderLotsCancellationResourceTest
    create_tender_lots_cancellation,
    patch_tender_lots_cancellation,
    # TenderLotCancellationResourceTest
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
)

from openprocurement.tender.openua.tests.cancellation_blanks import (
    # TenderCancellationResourceTest
    create_tender_cancellation,
    patch_tender_cancellation,
)

from openprocurement.tender.openeu.tests.cancellation import TenderCancellationBidsAvailabilityUtils
from openprocurement.tender.openeu.tests.cancellation_blanks import (
    # TenderAwardsCancellationResourceTest
    cancellation_active_qualification,
    cancellation_unsuccessful_qualification,
    cancellation_active_award,
    cancellation_unsuccessful_award,
    # TenderCancellationBidsAvailabilityTest
    bids_on_tender_cancellation_in_tendering,
    bids_on_tender_cancellation_in_pre_qualification,
    bids_on_tender_cancellation_in_pre_qualification_stand_still,
    bids_on_tender_cancellation_in_auction,
    bids_on_tender_cancellation_in_qualification,
    bids_on_tender_cancellation_in_awarded,
)

from openprocurement.tender.esco.tests.base import (
    BaseESCOEUContentWebTest,
    test_bids,
    test_lots
)


class TenderCancellationResourceTest(BaseESCOEUContentWebTest, TenderCancellationResourceTestMixin):

    initial_auth = ('Basic', ('broker', ''))

    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)


class TenderCancellationBidsAvailabilityTest(BaseESCOEUContentWebTest, TenderCancellationBidsAvailabilityUtils):
    initial_auth = ('Basic', ('broker', ''))
    initial_bids = test_bids * 2
    bid_visible_fields = [u'status', u'documents', u'tenderers', u'id', u'eligibilityDocuments']
    doc_id_by_type = {}
    valid_bids = []

    def setUp(self):
        super(TenderCancellationBidsAvailabilityTest, self).setUp()
        self.valid_bids = self.initial_bids_tokens.keys()
        self._prepare_bids_docs()

    test_bids_on_tender_cancellation_in_tendering = snitch(bids_on_tender_cancellation_in_tendering)
    test_bids_on_tender_cancellation_in_pre_qualification = snitch(bids_on_tender_cancellation_in_pre_qualification)
    test_bids_on_tender_cancellation_in_pre_qualification_stand_still = snitch(bids_on_tender_cancellation_in_pre_qualification_stand_still)
    test_bids_on_tender_cancellation_in_auction = snitch(bids_on_tender_cancellation_in_auction)
    test_bids_on_tender_cancellation_in_qualification = snitch(bids_on_tender_cancellation_in_qualification)
    test_bids_on_tender_cancellation_in_awarded = snitch(bids_on_tender_cancellation_in_awarded)


class TenderLotCancellationResourceTest(BaseESCOEUContentWebTest):
    initial_lots = test_lots

    initial_auth = ('Basic', ('broker', ''))

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(BaseESCOEUContentWebTest):
    initial_lots = 2 * test_lots

    initial_auth = ('Basic', ('broker', ''))
    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)


class TenderAwardsCancellationResourceTest(BaseESCOEUContentWebTest):
    initial_lots = 2 * test_lots
    initial_status = 'active.tendering'
    initial_bids = test_bids

    test_cancellation_active_qualification = snitch(cancellation_active_qualification)
    test_cancellation_unsuccessful_qualification = snitch(cancellation_unsuccessful_qualification)
    test_cancellation_active_award = snitch(cancellation_active_award)
    test_cancellation_unsuccessful_award = snitch(cancellation_unsuccessful_award)


class TenderCancellationDocumentResourceTest(BaseESCOEUContentWebTest, TenderCancellationDocumentResourceTestMixin):

    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

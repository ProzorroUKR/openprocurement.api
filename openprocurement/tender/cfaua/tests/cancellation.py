# -*- coding: utf-8 -*-
import unittest
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
    create_tender_cancellation_invalid,
    get_tender_cancellation,
    get_tender_cancellations,
    not_found,
    create_tender_cancellation_document,
    put_tender_cancellation_document,
    patch_tender_cancellation_document,
)

from openprocurement.tender.openeu.tests.cancellation import TenderCancellationBidsAvailabilityUtils
from openprocurement.tender.openua.tests.cancellation_blanks import (
    create_tender_cancellation,
    patch_tender_cancellation
)
from openprocurement.tender.cfaua.tests.cancellation_blanks import (
    # Cancellation tender
    cancellation_tender_active_tendering,
    cancellation_tender_active_pre_qualification,
    cancellation_tender_active_pre_qualification_stand_still,
    cancellation_tender_active_auction,
    cancellation_tender_active_qualification,
    cancellation_tender_active_qualification_stand_still,
    cancellation_tender_active_awarded,
    cancellation_tender_active_awarded_wo_timetravel,
    # Cancellation lot
    cancel_lot_active_tendering,
    cancel_lot_active_pre_qualification,
    cancel_lot_active_pre_qualification_stand_still,
    cancel_lot_active_auction,
    cancel_lot_active_qualification,
    cancel_lot_active_qualification_stand_still,
    cancel_lot_active_awarded,
    cancel_lot_active_awarded_wo_timetravel
)
from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_lots,
    test_bids)

no_award_logic = True
one_lot_restriction = True


class TenderCancellationResourceTest(BaseTenderContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    test_create_tender_cancellation = snitch(create_tender_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_cancellation)
    test_create_tender_cancellation_invalid = snitch(create_tender_cancellation_invalid)
    test_get_tender_cancellation = snitch(get_tender_cancellation)
    test_get_tender_cancellations = snitch(get_tender_cancellations)


class TenderLotCancellationResourceTest(BaseTenderContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)
    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)


class TenderCancellationDocumentResourceTest(BaseTenderContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']

    test_not_found = snitch(not_found)
    test_create_tender_cancellation_document = snitch(create_tender_cancellation_document)
    test_put_tender_cancellation_document = snitch(put_tender_cancellation_document)
    test_patch_tender_cancellation_document = snitch(patch_tender_cancellation_document)


class CancellationTenderAndLotOnAllStage(BaseTenderContentWebTest):
    initial_auth = ('Basic', ('broker', ''))
    initial_bids = test_bids
    test_author = test_bids[0]["tenderers"][0]
    # Cancellation tender
    test_cancellation_tender_active_tendering = snitch(cancellation_tender_active_tendering)
    test_cancellation_tender_active_pre_qualification = snitch(cancellation_tender_active_pre_qualification)
    test_cancellation_tender_active_pre_qualification_stand_still = snitch(
        cancellation_tender_active_pre_qualification_stand_still
    )
    test_cancellation_tender_active_auction = snitch(cancellation_tender_active_auction)
    test_cancellation_tender_active_qualification = snitch(cancellation_tender_active_qualification)
    test_cancellation_tender_active_qualification_stand_still = snitch(
        cancellation_tender_active_qualification_stand_still
    )
    test_cancellation_tender_active_awarded = snitch(cancellation_tender_active_awarded)
    test_cancellation_tender_active_awarded_wo_timetravel = snitch(cancellation_tender_active_awarded_wo_timetravel)

    # Cancellation lot
    test_cancel_lot_active_tendering = snitch(cancel_lot_active_tendering)
    test_cancel_lot_active_pre_qualification = snitch(cancel_lot_active_pre_qualification)
    test_cancel_lot_active_pre_qualification_stand_still = snitch(cancel_lot_active_pre_qualification_stand_still)
    test_cancel_lot_active_auction = snitch(cancel_lot_active_auction)
    test_cancel_lot_active_qualification = snitch(cancel_lot_active_qualification)
    test_cancel_lot_active_qualification_stand_still = snitch(cancel_lot_active_qualification_stand_still)
    test_cancel_lot_active_awarded = snitch(cancel_lot_active_awarded)
    test_cancel_lot_active_awarded_wo_timetravel = snitch(cancel_lot_active_awarded_wo_timetravel)




def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CancellationTenderAndLotOnAllStage))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

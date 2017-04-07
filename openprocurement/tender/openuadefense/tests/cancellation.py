# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_lots

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest
)
from openprocurement.tender.belowthreshold.tests.cancellation_blanks import (
    # TenderCancellationResourceTest
    create_tender_cancellation_invalid,
    create_tender_cancellation,
    patch_tender_cancellation,
    get_tender_cancellation,
    get_tender_cancellations,
    # TenderLotCancellationResourceTest
    create_tender_lot_cancellation,
    patch_tender_lot_cancellation,
    # TenderLotsCancellationResourceTest
    create_tender_lots_cancellation,
    patch_tender_lots_cancellation,
    # TenderCancellationDocumentResourceTest
    not_found,
    create_tender_cancellation_document,
    put_tender_cancellation_document,
    patch_tender_cancellation_document,
)


class TenderCancellationResourceTest(BaseTenderUAContentWebTest):

    test_create_tender_cancellation_invalid = snitch(create_tender_cancellation_invalid)

    test_create_tender_cancellation = snitch(create_tender_cancellation)

    test_patch_tender_cancellation = snitch(patch_tender_cancellation)

    test_get_tender_cancellation = snitch(get_tender_cancellation)

    test_get_tender_cancellations = snitch(get_tender_cancellations)


class TenderLotCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots

    test_create_tender_cancellation = snitch(create_tender_lot_cancellation)

    test_patch_tender_cancellation = snitch(patch_tender_lot_cancellation)


class TenderLotsCancellationResourceTest(BaseTenderUAContentWebTest):
    initial_lots = 2 * test_lots

    test_create_tender_cancellation = snitch(create_tender_lots_cancellation)

    test_patch_tender_cancellation = snitch(patch_tender_lots_cancellation)


class TenderCancellationDocumentResourceTest(BaseTenderUAContentWebTest):

    def setUp(self):
        super(TenderCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/tenders/{}/cancellations'.format(
            self.tender_id), {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']

    test_not_found = snitch(not_found)

    test_create_tender_cancellation_document = snitch(create_tender_cancellation_document)

    test_put_tender_cancellation_document = snitch(put_tender_cancellation_document)

    test_patch_tender_cancellation_document = snitch(patch_tender_cancellation_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderCancellationResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

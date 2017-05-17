# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.lot import (
    TenderLotProcessTestMixin
)

from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    create_tender_lot,
    patch_tender_lot,
    delete_tender_lot,
    tender_lot_guarantee,
    tender_lot_document
)

from openprocurement.tender.openeu.tests.lot_blanks import (
    # TenderLotProcessTest
    two_lot_1can,
)

from openprocurement.tender.esco.tests.base import (
    BaseESCOEUContentWebTest,
    test_tender_data,
    test_lots,
)

from openprocurement.tender.esco.tests.lot_blanks import (
    create_tender_lot_invalid,
    patch_tender_lot_minValue,
    patch_tender_currency,
    patch_tender_vat,
    get_tender_lot,
    get_tender_lots,
    tender_min_value,
    tender_features_invalid

)

class TenderLotResourceTest(BaseESCOEUContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    test_lots_data = test_lots  # TODO: change attribute identifier
    initial_data = test_tender_data

    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid)
    test_create_tender_lot = snitch(create_tender_lot)
    test_patch_tender_lot = snitch(patch_tender_lot)
    test_patch_tender_lot_minValue = snitch(patch_tender_lot_minValue)
    test_delete_tender_lot = snitch(delete_tender_lot)

    test_patch_tender_currency = snitch(patch_tender_currency)
    test_patch_tender_vat = snitch(patch_tender_vat)
    test_tender_lot_guarantee = snitch(tender_lot_guarantee)

    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)


class TenderLotFeatureResourceTest(BaseESCOEUContentWebTest):
    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data
    invalid_feature_value = 0.4
    max_feature_value = 0.3
    sum_of_max_value_of_all_features = 0.3

    test_tender_min_value = snitch(tender_min_value)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_tender_lot_document = snitch(tender_lot_document)


class TenderLotProcessTest(BaseESCOEUContentWebTest, TenderLotProcessTestMixin):
    setUp = BaseESCOEUContentWebTest.setUp
    test_lots_data = test_lots  # TODO: change attribute identifier
    initial_data = test_tender_data

    days_till_auction_starts = 16

    test_2lot_1can = snitch(two_lot_1can)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderLotResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotProcessTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

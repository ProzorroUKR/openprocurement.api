import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_author
from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_tender_cfaua_bids,
    test_tender_cfaua_features_data,
    test_tender_cfaua_lots,
)
from openprocurement.tender.cfaua.tests.chronograph_blanks import (  # TenderSwitchAuctionResourceTest; TenderSwitchPreQualificationResourceTest
    active_tendering_to_pre_qual,
    next_check_field_in_active_qualification,
    pre_qual_switch_to_stand_still,
)
from openprocurement.tender.cfaua.tests.chronograph_blanks import (
    set_auction_period_0bid as set_auction_period,  # TenderComplaintSwitchResourceTest; TenderSwitchAuctionResourceTest; TenderSwitchPreQualificationResourceTest; TenderSwitchPreQualificationStandStillResourceTest
)
from openprocurement.tender.cfaua.tests.chronograph_blanks import (  # TenderSwitchAuctionResourceTest; TenderSwitchPreQualificationResourceTest
    switch_to_auction,
    switch_to_awarded,
    switch_to_complaint,
    switch_to_unsuccessful,
    switch_to_unsuccessful_from_qualification_stand_still,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    set_auction_period_lot_0bid as set_auction_period_lot,
)


class TenderSwitchPreQualificationResourceTest(BaseTenderContentWebTest):
    initial_status = "active.pre-qualification"
    initial_bids = test_tender_cfaua_bids

    test_switch_to_pre_qual = snitch(active_tendering_to_pre_qual)
    test_switch_to_stand_still = snitch(pre_qual_switch_to_stand_still)


class TenderSwitchAuctionResourceTest(BaseTenderContentWebTest):
    initial_status = "active.pre-qualification.stand-still"
    initial_bids = test_tender_cfaua_bids

    test_switch_to_auction = snitch(switch_to_auction)


class TenderSwitchUnsuccessfulResourceTest(BaseTenderContentWebTest):
    initial_status = "active.tendering"

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderLotSwitchPreQualificationResourceTest(TenderSwitchPreQualificationResourceTest):
    initial_lots = test_tender_cfaua_lots


class TenderLotSwitchAuctionResourceTest(TenderSwitchAuctionResourceTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_cfaua_lots
    initial_bids = test_tender_cfaua_bids


class TenderLotSwitchUnsuccessfulResourceTest(TenderSwitchUnsuccessfulResourceTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_cfaua_lots

    test_switch_to_unsuccessful_from_qualification_stand_still = snitch(
        switch_to_unsuccessful_from_qualification_stand_still
    )


class TenderAuctionPeriodResourceTest(BaseTenderContentWebTest):
    initial_status = "active.pre-qualification.stand-still"

    test_set_auction_period = snitch(set_auction_period)


class TenderLotAuctionPeriodResourceTest(BaseTenderContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_cfaua_lots

    test_set_auction_period = snitch(set_auction_period_lot)


class TenderSwitchStatusesForNextCheckResourceTest(BaseTenderContentWebTest):
    initial_status = "active.pre-qualification"
    initial_bids = test_tender_cfaua_bids

    test_next_check_field_in_active_qualification = snitch(next_check_field_in_active_qualification)


class TenderSwitchQualificationStandStillResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_cfaua_features_data
    initial_status = "active.qualification.stand-still"
    initial_bids = deepcopy(test_tender_cfaua_bids)

    def setUp(self):
        for bid in self.initial_bids:
            bid.update({"parameters": [{"code": i["code"], "value": 0.1} for i in self.initial_data["features"]]})
        super().setUp()

    test_switch_to_awarded = snitch(switch_to_awarded)


class TenderLotSwitchQualificationStandStillResourceTest(TenderSwitchQualificationStandStillResourceTest):
    initial_lots = test_tender_cfaua_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintSwitchResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotComplaintSwitchResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotSwitchAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSwitchAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSwitchQualificationStandStillResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotSwitchQualificationStandStillResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSwitchStatusesForNextCheckResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")

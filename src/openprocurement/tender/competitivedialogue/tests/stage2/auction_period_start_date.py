import unittest
from openprocurement.api.tests.base import snitch
from openprocurement.tender.competitivedialogue.tests.stage2.auction_period_start_date_blanks import (
    tender_collection_put_auction_period_in_active_tendering,
    tender_collection_put_auction_period_in_active_pre_qualification,
    tender_collection_put_auction_period_in_active_auction,
    tender_put_auction_period_permission_error,
    tender_collection_put_auction_period_for_not_allowed_tender_status,
    tender_lot_put_auction_period_for_not_allowed_tender_status,
    tender_lot_put_auction_period_in_active_tendering,
    tender_lot_put_auction_period_in_active_pre_qualification,
    tender_lot_put_auction_period_in_active_auction,
    tender_multe_lot_put_auction_period_for_not_allowed_tender_status,
    tender_multe_lot_put_auction_period_in_active_tendering,
    tender_multe_lot_put_auction_period_in_active_auction,
    tender_multe_lot_put_auction_period_in_active_pre_qualification,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest, test_lots,
    BaseCompetitiveDialogUAStage2ContentWebTest,
)
from freezegun import freeze_time


@freeze_time("2022-01-04")
class TenderStage2EUAuctionPeriodStartDateResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    days_till_auction_starts = 10
    test_tender_collection_put_auction_period_in_active_tendering = snitch(
        tender_collection_put_auction_period_in_active_tendering)
    test_tender_collection_put_auction_period_in_active_pre_qualification = snitch(
        tender_collection_put_auction_period_in_active_pre_qualification)
    test_tender_put_auction_period_permission_error = snitch(tender_put_auction_period_permission_error)
    test_tender_collection_put_auction_period_for_not_allowed_tender_status = snitch(
        tender_collection_put_auction_period_for_not_allowed_tender_status)

@freeze_time("2022-01-04")
class TenderStage2UAAuctionPeriodStartDateResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    days_till_auction_starts = 10
    test_tender_collection_put_auction_period_in_active_tendering = snitch(
        tender_collection_put_auction_period_in_active_tendering)
    test_tender_collection_put_auction_period_in_active_auction = snitch(
        tender_collection_put_auction_period_in_active_auction)
    test_tender_put_auction_period_permission_error = snitch(tender_put_auction_period_permission_error)
    test_tender_collection_put_auction_period_for_not_allowed_tender_status = snitch(
        tender_collection_put_auction_period_for_not_allowed_tender_status)

@freeze_time("2022-01-04")
class TenderStage2EULotAuctionPeriodStartDateResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = test_lots
    days_till_auction_starts = 10
    test_tender_lot_put_auction_period_for_not_allowed_tender_status = snitch(
        tender_lot_put_auction_period_for_not_allowed_tender_status)
    test_tender_lot_put_auction_period_in_active_tendering = snitch(
        tender_lot_put_auction_period_in_active_tendering)
    test_tender_lot_put_auction_period_in_active_pre_qualification = snitch(
        tender_lot_put_auction_period_in_active_pre_qualification)

@freeze_time("2022-01-04")
class TenderStage2UALotAuctionPeriodStartDateResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = test_lots
    days_till_auction_starts = 10
    test_tender_lot_put_auction_period_for_not_allowed_tender_status = snitch(
        tender_lot_put_auction_period_for_not_allowed_tender_status)
    test_tender_lot_put_auction_period_in_active_tendering = snitch(
        tender_lot_put_auction_period_in_active_tendering)
    test_tender_lot_put_auction_period_in_active_auction = snitch(
        tender_lot_put_auction_period_in_active_auction)

@freeze_time("2022-01-04")
class TenderStage2EUMultipleLotAuctionPeriodStartDateResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    days_till_auction_starts = 10
    initial_lots = 2 * test_lots
    test_tender_multe_lot_put_auction_period_for_not_allowed_tender_status = snitch(
        tender_multe_lot_put_auction_period_for_not_allowed_tender_status)
    test_tender_multe_lot_put_auction_period_in_active_tendering = snitch(
        tender_multe_lot_put_auction_period_in_active_tendering)
    test_tender_multe_lot_put_auction_period_in_active_pre_qualification = snitch(
        tender_multe_lot_put_auction_period_in_active_pre_qualification)

@freeze_time("2022-01-04")
class TenderStage2UAMultipleLotAuctionPeriodStartDateResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    days_till_auction_starts = 10
    initial_lots = 2 * test_lots
    test_tender_multe_lot_put_auction_period_for_not_allowed_tender_status = snitch(
        tender_multe_lot_put_auction_period_for_not_allowed_tender_status)
    test_tender_multe_lot_put_auction_period_in_active_tendering = snitch(
        tender_multe_lot_put_auction_period_in_active_tendering)
    test_tender_multe_lot_put_auction_period_in_active_auction = snitch(
        tender_multe_lot_put_auction_period_in_active_auction)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUAuctionPeriodStartDateResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAAuctionPeriodStartDateResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotAuctionPeriodStartDateResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotAuctionPeriodStartDateResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUMultipleLotAuctionPeriodStartDateResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UAMultipleLotAuctionPeriodStartDateResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")

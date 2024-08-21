import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    switch_to_unsuccessful,
)
from openprocurement.tender.core.tests.chronograph import (
    switch_award_complaints_draft,
    switch_qualification_complaints_draft,
    switch_tender_after_cancellation_unsuccessful,
    switch_tender_cancellation_complaints_draft,
    switch_tender_complaints_draft,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_tender_openeu_bids,
    test_tender_openeu_lots,
)
from openprocurement.tender.openeu.tests.chronograph_blanks import (
    active_tendering_to_pre_qual,
    active_tendering_to_pre_qual_unsuccessful,
    active_tendering_to_unsuccessful,
    pre_qual_switch_to_auction,
    pre_qual_switch_to_stand_still,
    switch_to_auction,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    set_auction_period_0bid as set_auction_period,
)
from openprocurement.tender.openua.tests.chronograph_blanks import (
    set_auction_period_lot_0bid as set_auction_period_lot,
)


class TenderSwitchPreQualificationResourceTest(BaseTenderContentWebTest):
    initial_status = "active.pre-qualification"
    initial_bids = test_tender_openeu_bids

    test_switch_to_pre_qual = snitch(active_tendering_to_pre_qual)
    test_switch_to_auction = snitch(pre_qual_switch_to_auction)
    test_switch_to_stand_still = snitch(pre_qual_switch_to_stand_still)


class TenderSwitchAuctionResourceTest(BaseTenderContentWebTest):
    initial_status = "active.pre-qualification.stand-still"
    initial_bids = test_tender_openeu_bids

    test_switch_to_auction = snitch(switch_to_auction)


class TenderSwitchUnsuccessfulResourceTest(BaseTenderContentWebTest):
    initial_status = "active.tendering"

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderLotSwitchPreQualificationResourceTest(TenderSwitchPreQualificationResourceTest):
    initial_lots = test_tender_openeu_lots


class TenderLotSwitchPreQualificationUnsuccessfulTest(BaseTenderContentWebTest):
    initial_bids = test_tender_openeu_bids
    initial_lots = test_tender_openeu_lots * 3
    initial_status = "active.tendering"

    def setUp(self):
        super().setUp()

        tender = self.mongodb.tenders.get(self.tender_id)
        # Create award with an unsuccessful lot
        for bid in tender["bids"]:
            response = self.app.patch_json(
                f"/tenders/{self.tender_id}/bids/{bid['id']}?acc_token={bid['owner_token']}",
                {"data": {"lotValues": bid["lotValues"][:1]}},
            )
            self.assertEqual(response.status, "200 OK")
            response = self.activate_bid(self.tender_id, bid['id'], bid['owner_token'])
            self.assertEqual(response.status, "200 OK")

    test_switch_to_pre_qual_unsuccessful = snitch(active_tendering_to_pre_qual_unsuccessful)


class TenderLotUnsuccessfulTenderingTest(BaseTenderContentWebTest):
    initial_bids = test_tender_openeu_bids[:1]
    initial_lots = test_tender_openeu_lots
    initial_status = "active.tendering"
    test_lot_active_tendering_to_unsuccessful = snitch(active_tendering_to_unsuccessful)


class TenderUnsuccessfulTenderingTest(BaseTenderContentWebTest):
    initial_bids = test_tender_openeu_bids[:1]
    initial_status = "active.tendering"
    test_lot_active_tendering_to_unsuccessful = snitch(active_tendering_to_unsuccessful)


class TenderLotSwitchAuctionResourceTest(TenderSwitchAuctionResourceTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_openeu_lots
    initial_bids = test_tender_openeu_bids


class TenderLotSwitchUnsuccessfulResourceTest(TenderSwitchUnsuccessfulResourceTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_openeu_lots


class TenderAuctionPeriodResourceTest(BaseTenderContentWebTest):
    initial_status = "active.tendering"

    test_set_auction_period = snitch(set_auction_period)
    test_switch_tender_complaints_draft = snitch(switch_tender_complaints_draft)
    test_switch_tender_cancellation_complaints_draft = snitch(switch_tender_cancellation_complaints_draft)


class TenderLotAuctionPeriodResourceTest(BaseTenderContentWebTest):
    initial_status = "active.tendering"
    initial_lots = test_tender_openeu_lots

    test_set_auction_period = snitch(set_auction_period_lot)


class TenderComplaintSwitchResourceTest(BaseTenderContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "active.tendering"
    initial_bids = test_tender_openeu_bids
    initial_lots = test_tender_openeu_lots
    author_data = test_tender_below_author

    test_switch_qualification_complaints_draft = snitch(switch_qualification_complaints_draft)
    test_switch_tender_after_cancellation_unsuccessful = snitch(switch_tender_after_cancellation_unsuccessful)


class TenderLotComplaintSwitchResourceTest(TenderComplaintSwitchResourceTest):
    initial_lots = test_tender_openeu_lots


class TenderAwardComplaintSwitchResourceTest(BaseTenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_openeu_bids

    def setUp(self):
        super().setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_below_organization],
                        "status": "pending",
                        "bid_id": self.initial_bids[0]["id"],
                    }
                },
            )
            award = response.json["data"]
            self.award_id = award["id"]

    test_switch_award_complaints_draft = snitch(switch_award_complaints_draft)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderComplaintSwitchResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotComplaintSwitchResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotSwitchAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSwitchAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSwitchUnsuccessfulResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")

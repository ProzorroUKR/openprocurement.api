from openprocurement.tender.openuadefense.tests.award import TenderAwardPendingResourceTestCase
from openprocurement.tender.openuadefense.tests.base import test_bids, BaseTenderUAContentWebTest
from openprocurement.tender.core.tests.base import change_auth
from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderQualificationMilestone24HMixin,
    TenderQualificationMilestoneALPMixin,
)
from copy import deepcopy


class TenderAwardMilestoneTestCase(TenderQualificationMilestone24HMixin, TenderAwardPendingResourceTestCase):
    context_name = "award"


class TenderAwardMilestoneALPTestCase(TenderQualificationMilestoneALPMixin, BaseTenderUAContentWebTest):
    initial_bids = test_bids
    initial_lots = test_lots

    def test_milestone(self):
        """
        Redefine original method, to check that the milestone won't appear
        """
        # sending auction results
        auction_results = deepcopy(self.initial_bids)
        lot_id = auction_results[0]["lotValues"][0]["relatedLot"]
        auction_results[0]["lotValues"][0]["value"]["amount"] = 1
        with change_auth(self.app, ("Basic", ("auction", ""))):
            response = self.app.post_json(
                "/tenders/{}/auction/{}".format(self.tender_id, lot_id),
                {"data": {"bids": auction_results}},
                status=200
            )
        tender = response.json["data"]
        self.assertEqual("active.qualification", tender["status"])
        self.assertGreater(len(tender["awards"]), 0)
        award = tender["awards"][0]
        bid_id = award["bid_id"]
        self.assertEqual(bid_id, auction_results[0]["id"])

        # check that a milestone's been created
        self.assertNotIn("milestones", award)


from openprocurement.tender.openuadefense.tests.award import TenderAwardPendingResourceTestCase
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneALPMixin,
)
from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_openuadefense_bids,
)


class TenderAwardMilestoneTestCase(TenderAwardMilestone24HMixin, TenderAwardPendingResourceTestCase):
    pass


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderUAContentWebTest):
    initial_bids = test_tender_openuadefense_bids
    initial_lots = test_tender_below_lots

    def test_milestone(self):
        """
        Redefine original method, to check that the milestone won't appear
        """
        # sending auction results
        auction_results = [
            {"id": b["id"], "lotValues": [
                {"relatedLot": l["relatedLot"], "value": l["value"]} for l in b["lotValues"]
            ]}
            for b in self.initial_bids
        ]
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


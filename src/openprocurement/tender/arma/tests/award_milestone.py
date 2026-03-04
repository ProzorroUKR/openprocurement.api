from copy import deepcopy

from openprocurement.tender.arma.tests.base import (
    BaseTenderContentWebTest,
    test_tender_arma_bids,
    test_tender_arma_lots,
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestoneALPMixin,
)


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderContentWebTest):
    initial_bids = test_tender_arma_bids
    initial_lots = test_tender_arma_lots
    alp_period_work_days = 2

    def setUp(self):
        more_bids = 4 - len(self.initial_bids)
        if more_bids > 0:
            self.initial_bids = deepcopy(self.initial_bids) + deepcopy(self.initial_bids)[:more_bids]
        self.initial_bids[0]["value"]["amountPercentage"] = 50
        self.initial_bids[1]["value"]["amountPercentage"] = 50
        self.initial_bids[2]["value"]["amountPercentage"] = 50
        self.initial_bids[3]["value"]["amountPercentage"] = 50
        self.assertEqual(len(self.initial_bids), 4)

        BaseTenderContentWebTest.setUp(self)

        tender = self.mongodb.tenders.get(self.tender_id)
        for b in tender["bids"]:
            b["status"] = "active"
            if "lotValues" in b:
                for l_value in b["lotValues"]:
                    if "status" in l_value:
                        l_value["status"] = "active"  # in case they were "pending" #openeu
        self.mongodb.tenders.save(tender)

    def generate_auction_results(self):
        if self.initial_lots:
            auction_results = [
                {
                    "id": b["id"],
                    "lotValues": [
                        {"relatedLot": l_value["relatedLot"], "value": {"amount": l_value["value"]["amountPercentage"]}}
                        for l_value in b["lotValues"]
                    ],
                }
                for b in self.initial_bids
            ]
            auction_results[0]["lotValues"][0]["value"]["amount"] = 20  # only 1 case
            auction_results[1]["lotValues"][0]["value"]["amount"] = 21  # both 1 and 2 case
            auction_results[2]["lotValues"][0]["value"]["amount"] = 35  # only 2 case
            auction_results[3]["lotValues"][0]["value"]["amount"] = 50  # no milestones
        else:
            auction_results = [{"id": b["id"], "value": b["value"]} for b in self.initial_bids]
            auction_results[0]["value"]["amount"] = 20  # only 1 case
            auction_results[1]["value"]["amount"] = 21  # both 1 and 2 case
            auction_results[2]["value"]["amount"] = 35  # only 2 case
            auction_results[3]["value"]["amount"] = 50  # no milestones

        return auction_results

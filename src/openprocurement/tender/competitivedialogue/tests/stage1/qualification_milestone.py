from copy import deepcopy

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUContentWebTest,
    BaseCompetitiveDialogUAContentWebTest,
    test_tender_cd_stage1_bids,
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderQualificationMilestone24HMixin,
)
from openprocurement.tender.core.tests.utils import set_bid_items


class TenderPreQualificationMixin:
    initial_auth = ("Basic", ("broker", ""))
    initial_bids = test_tender_cd_stage1_bids
    initial_bids_data = test_tender_cd_stage1_bids

    def setUp(self):
        super().setUp()

        for n, bid in enumerate(self.initial_bids_data):
            bid = deepcopy(bid)
            bid["tenderers"][0]["identifier"]["id"] = "0000{}".format(n)
            set_bid_items(self, bid)

            self.app.post_json(
                "/tenders/{}/bids".format(self.tender_id),
                {"data": bid},
            )

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")


class TenderUAQualificationMilestoneTestCase(
    TenderQualificationMilestone24HMixin, TenderPreQualificationMixin, BaseCompetitiveDialogUAContentWebTest
):
    pass


class TenderEUQualificationMilestoneTestCase(
    TenderQualificationMilestone24HMixin, TenderPreQualificationMixin, BaseCompetitiveDialogEUContentWebTest
):
    pass

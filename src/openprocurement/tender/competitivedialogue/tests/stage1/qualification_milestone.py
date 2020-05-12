from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogUAContentWebTest,
    BaseCompetitiveDialogEUContentWebTest,
    test_bids,
)
from openprocurement.tender.core.tests.qualification_milestone import TenderQualificationMilestone24HMixin
from copy import deepcopy


class TenderPreQualificationMixin(object):
    initial_auth = ("Basic", ("broker", ""))
    initial_bids = test_bids
    context_name = "qualification"

    def setUp(self):
        super(TenderPreQualificationMixin, self).setUp()

        for n, bid in enumerate(self.initial_bids):
            bid = deepcopy(bid)
            bid["tenderers"][0]["identifier"]["id"] = u"0000{}".format(n)
            self.app.post_json(
                "/tenders/{}/bids".format(self.tender_id),
                {"data": bid},
            )

        # update periods to have possibility to change tender status by chronograph
        self.set_status("active.pre-qualification", extra={"status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")


class TenderUAQualificationMilestoneTestCase(TenderQualificationMilestone24HMixin, TenderPreQualificationMixin,
                                             BaseCompetitiveDialogUAContentWebTest):
    pass


class TenderEUQualificationMilestoneTestCase(TenderQualificationMilestone24HMixin, TenderPreQualificationMixin,
                                             BaseCompetitiveDialogEUContentWebTest):
    pass

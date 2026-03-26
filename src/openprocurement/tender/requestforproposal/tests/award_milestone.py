from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneNoALPMixin,
)
from openprocurement.tender.requestforproposal.tests.award import (
    TenderAwardPendingResourceTestCase,
)
from openprocurement.tender.requestforproposal.tests.award_blanks import (
    milestone_24h,
    milestone_24h_dueDate_less_than_24h,
)
from openprocurement.tender.requestforproposal.tests.base import (
    TenderContentWebTest,
    test_tender_rfp_bids,
)


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class TenderAwardMilestone24HTestCase(TenderAwardMilestone24HMixin, TenderAwardPendingResourceTestCase):
    test_24hours_milestone = snitch(milestone_24h)
    test_24hours_milestone_dueDate_less_than_24h = snitch(milestone_24h_dueDate_less_than_24h)


class TenderAwardMilestoneNoALPTestCase(TenderAwardMilestoneNoALPMixin, TenderContentWebTest):
    initial_bids = test_tender_rfp_bids

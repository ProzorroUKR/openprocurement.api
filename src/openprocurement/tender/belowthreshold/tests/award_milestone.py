from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.award import (
    TenderAwardPendingResourceTestCase,
)
from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_below_bids,
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneNoALPMixin,
)


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class TenderAwardMilestone24HTestCase(TenderAwardMilestone24HMixin, TenderAwardPendingResourceTestCase):
    pass


class TenderAwardMilestoneNoALPTestCase(TenderAwardMilestoneNoALPMixin, TenderContentWebTest):
    initial_bids = test_tender_below_bids

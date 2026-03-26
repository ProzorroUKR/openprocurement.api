from openprocurement.api.tests.base import snitch
from openprocurement.tender.core.tests.qualification_milestone import TenderQualificationMilestone24HMixin
from openprocurement.tender.requestforproposal.tests.award_blanks import (
    milestone_24h,
    milestone_24h_dueDate_less_than_24h,
)
from openprocurement.tender.requestforproposal.tests.qualification import TenderQualificationBaseTestCase


class TenderQualificationMilestoneTestCase(TenderQualificationMilestone24HMixin, TenderQualificationBaseTestCase):
    test_24hours_milestone = snitch(milestone_24h)
    test_24hours_milestone_dueDate_less_than_24h = snitch(milestone_24h_dueDate_less_than_24h)

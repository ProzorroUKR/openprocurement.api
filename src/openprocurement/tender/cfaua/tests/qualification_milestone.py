from openprocurement.tender.cfaua.tests.qualification import TenderQualificationBaseTestCase
from openprocurement.tender.core.tests.qualification_milestone import TenderQualificationMilestoneMixin


class TenderQualificationMilestoneTestCase(TenderQualificationMilestoneMixin, TenderQualificationBaseTestCase):
    context_name = "qualification"

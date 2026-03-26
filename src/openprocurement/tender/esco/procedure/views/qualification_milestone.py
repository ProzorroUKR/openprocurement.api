from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_milestone import (
    QualificationMilestoneResource as BaseQualificationMilestoneResource,
)
from openprocurement.tender.esco.constants import ESCO


@resource(
    name=f"{ESCO}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=ESCO,
    description="Tender qualification milestones",
)
class QualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass

from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.core.procedure.views.qualification_milestone import (
    QualificationMilestoneResource as BaseQualificationMilestoneResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender qualification milestones",
)
class QualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass

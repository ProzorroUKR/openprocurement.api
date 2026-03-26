from cornice.resource import resource

from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.core.procedure.views.qualification_milestone import (
    QualificationMilestoneResource as BaseQualificationMilestoneResource,
)


@resource(
    name=f"{CFA_SELECTION}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=CFA_SELECTION,
    description="Tender qualification milestones",
)
class QualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass

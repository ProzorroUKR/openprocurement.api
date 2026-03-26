from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_milestone import (
    QualificationMilestoneResource as BaseQualificationMilestoneResource,
)
from openprocurement.tender.openuadefense.constants import ABOVE_THRESHOLD_UA_DEFENSE


@resource(
    name=f"{ABOVE_THRESHOLD_UA_DEFENSE}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=ABOVE_THRESHOLD_UA_DEFENSE,
    description="Tender qualification milestones",
)
class QualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass

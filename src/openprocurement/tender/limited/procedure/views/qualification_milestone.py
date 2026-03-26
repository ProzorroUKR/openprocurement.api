from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_milestone import (
    QualificationMilestoneResource as BaseQualificationMilestoneResource,
)
from openprocurement.tender.limited.constants import NEGOTIATION, NEGOTIATION_QUICK, REPORTING


@resource(
    name=f"{REPORTING}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=REPORTING,
    description="Tender qualification milestones",
)
class ReportingQualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass


@resource(
    name=f"{NEGOTIATION}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=NEGOTIATION,
    description="Tender qualification milestones",
)
class NegotiationQualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass


@resource(
    name=f"{NEGOTIATION_QUICK}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=NEGOTIATION_QUICK,
    description="Tender qualification milestones",
)
class NegotiationQuickQualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass

from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.qualification_milestone import (
    QualificationMilestoneResource as BaseQualificationMilestoneResource,
)


@resource(
    name=f"{ProcurementMethodType.REPORTING}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=ProcurementMethodType.REPORTING,
    description="Tender qualification milestones",
)
class ReportingQualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION,
    description="Tender qualification milestones",
)
class NegotiationQualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass


@resource(
    name=f"{ProcurementMethodType.NEGOTIATION_QUICK}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION_QUICK,
    description="Tender qualification milestones",
)
class NegotiationQuickQualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass

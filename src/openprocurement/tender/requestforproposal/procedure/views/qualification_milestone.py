from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_milestone import (
    QualificationMilestoneResource as BaseQualificationMilestoneResource,
)
from openprocurement.tender.requestforproposal.constants import REQUEST_FOR_PROPOSAL
from openprocurement.tender.requestforproposal.procedure.state.qualification_milestone import (
    RequestForProposalQualificationMilestoneState,
)


@resource(
    name=f"{REQUEST_FOR_PROPOSAL}:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=REQUEST_FOR_PROPOSAL,
    description="Tender qualification milestones",
)
class QualificationMilestoneResource(BaseQualificationMilestoneResource):
    state_class = RequestForProposalQualificationMilestoneState

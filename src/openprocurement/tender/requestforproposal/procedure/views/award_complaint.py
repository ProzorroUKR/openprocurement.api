from cornice.resource import resource

from openprocurement.tender.core.procedure.serializers.complaint import (
    ComplaintSerializer,
)
from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
)
from openprocurement.tender.requestforproposal.procedure.state.award_claim import (
    RequestForProposalAwardClaimState,
)


@resource(
    name="requestForProposal:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="requestForProposal",
    request_method=["GET"],
    description="Tender award complaints get",
)
class RequestForProposalAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    serializer_class = ComplaintSerializer


@resource(
    name="requestForProposal:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="requestForProposal",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class RequestForProposalAwardClaimResource(AwardClaimResource):
    state_class = RequestForProposalAwardClaimState

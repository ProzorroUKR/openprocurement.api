from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)
from openprocurement.tender.limited.procedure.state.award_complaint import (
    NegotiationAwardComplaintState,
)


@resource(
    name="negotiation:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION,
    request_method=["GET"],
    description="Tender negotiation award complaints get",
)
class NegotiationAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name="negotiation:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender negotiation award complaints",
)
class NegotiationAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = NegotiationAwardComplaintState


@resource(
    name="negotiation.quick:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION_QUICK,
    request_method=["GET"],
    description="Tender negotiation.quick award complaints get",
)
class NegotiationQuickAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name="negotiation.quick:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION_QUICK,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender negotiation.quick award complaints",
)
class NegotiationQuickAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = NegotiationAwardComplaintState

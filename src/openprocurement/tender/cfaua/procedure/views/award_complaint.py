from cornice.resource import resource
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)
from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.cfaua.procedure.state.award_complaint import CFAUAAwardComplaintState
from openprocurement.tender.cfaua.procedure.state.award_claim import CFAUAAwardClaimState


@resource(
    name="closeFrameworkAgreementUA:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["GET"],
    description="Tender EU award complaints get",
)
class CFAUAAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name="closeFrameworkAgreementUA:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender EU award claims",
)
class CFAUATenderAwardClaimResource(AwardClaimResource):
    state_class = CFAUAAwardClaimState


@resource(
    name="closeFrameworkAgreementUA:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender EU award complaints",
)
class CFAUAAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = CFAUAAwardComplaintState

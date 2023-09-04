from cornice.resource import resource
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)
from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.openuadefense.procedure.state.award_claim import OpenUADefenseAwardClaimState


@resource(
    name="aboveThresholdUA.defense:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    request_method=["GET"],
    description="Tender award complaints get",
)
class OpenUADefenseAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name="aboveThresholdUA.defense:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class OpenUADefenseTenderAwardClaimResource(AwardClaimResource):
    state_class = OpenUADefenseAwardClaimState


@resource(
    name="aboveThresholdUA.defense:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
)
class OpenUADefenseAwardComplaintWriteResource(AwardComplaintWriteResource):
    pass


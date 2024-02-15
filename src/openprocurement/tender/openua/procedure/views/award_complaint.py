from cornice.resource import resource
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)
from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.open.procedure.state.award_claim import OpenAwardClaimState
from openprocurement.tender.open.procedure.state.award_complaint import OpenAwardComplaintState


@resource(
    name="aboveThresholdUA:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    request_method=["GET"],
    description="Tender award complaints get",
)
class OpenUAAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name="aboveThresholdUA:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class OpenUATenderAwardClaimResource(AwardClaimResource):
    state_class = OpenAwardClaimState


@resource(
    name="aboveThresholdUA:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
)
class OpenUAAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = OpenAwardComplaintState

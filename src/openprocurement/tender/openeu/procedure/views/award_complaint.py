from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)
from openprocurement.tender.openeu.procedure.state.award_claim import (
    OpenEUAwardClaimState,
)
from openprocurement.tender.openeu.procedure.state.award_complaint import (
    OpenEUAwardComplaintState,
)


@resource(
    name="aboveThresholdEU:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["GET"],
    description="Tender EU award complaints get",
)
class OpenEUAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name="aboveThresholdEU:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender EU award claims",
)
class OpenEUTenderAwardClaimResource(AwardClaimResource):
    state_class = OpenEUAwardClaimState


@resource(
    name="aboveThresholdEU:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender EU award complaints",
)
class OpenEUAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = OpenEUAwardComplaintState

from cornice.resource import resource
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)
from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.esco.procedure.state.award_complaint import ESCOAwardComplaintState
from openprocurement.tender.esco.procedure.state.award_claim import ESCOAwardClaimState


@resource(
    name="esco:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["GET"],
    description="Tender ESCO award complaints get",
)
class ESCOAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name="esco:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender ESCO award claims",
)
class ESCOTenderAwardClaimResource(AwardClaimResource):
    state_class = ESCOAwardClaimState


@resource(
    name="esco:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender ESCO award complaints",
)
class ESCOAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = ESCOAwardComplaintState

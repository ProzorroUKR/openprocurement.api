from cornice.resource import resource
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)
from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.openuadefense.procedure.state.award_claim import OpenUADefenseAwardClaimState
from openprocurement.tender.simpledefense.procedure.state.award_claim import SimpleDefenseAwardClaimState
from openprocurement.tender.simpledefense.procedure.state.award_complaint import SimpleDefenseAwardComplaintState


@resource(
    name="simple.defense:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    request_method=["GET"],
    description="Tender award complaints get",
)
class SimpleDefenseAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name="simple.defense:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class SimpleDefenseTenderAwardClaimResource(AwardClaimResource):
    state_class = SimpleDefenseAwardClaimState


@resource(
    name="simple.defense:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
)
class SimpleDefenseAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = SimpleDefenseAwardComplaintState

from cornice.resource import resource

from openprocurement.tender.competitivedialogue.procedure.state.stage2.award_claim import (
    CDEUStage2AwardClaimState,
    CDUAStage2AwardClaimState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.award_complaint import (
    CDEUStage2AwardComplaintState,
    CDUAStage2AwardComplaintState,
)
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)
from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@resource(
    name="{}:Tender Award Complaints Get".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue Stage 2 EU award complaints get",
)
class CD2EUAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name="{}:Tender Award Claims".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue Stage 2 EU award claims",
)
class CD2EUTenderAwardClaimResource(AwardClaimResource):
    state_class = CDEUStage2AwardClaimState


@resource(
    name="{}:Tender Award Complaints".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue Stage 2 EU award complaints",
)
class CD2EUAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = CDEUStage2AwardComplaintState


@resource(
    name="{}:Tender Award Complaints Get".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue Stage 2 UA award complaints get",
)
class CD2UAAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name="{}:Tender Award Claims".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue Stage 2 UA award claims",
)
class CD2UATenderAwardClaimResource(AwardClaimResource):
    state_class = CDUAStage2AwardClaimState


@resource(
    name="{}:Tender Award Complaints".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue Stage 2 UA award complaints",
)
class CD2UAAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = CDUAStage2AwardComplaintState

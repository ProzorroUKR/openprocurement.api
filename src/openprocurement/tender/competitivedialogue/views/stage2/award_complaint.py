# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.award_complaint import (
    TenderUAAwardComplaintResource,
    TenderUAAwardClaimResource,
)
from openprocurement.tender.openeu.views.award_complaint import (
    TenderEUAwardComplaintResource,
    TenderEUAwardClaimResource,
)
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource,
)
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@optendersresource(
    name="{}:Tender Award Complaints Get".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue Stage 2 EU award complaints get",
)
class CompetitiveDialogueStage2EUAwardComplaintGetResource(BaseComplaintGetResource):
    """ """


@optendersresource(
    name="{}:Tender Award Complaints".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue Stage 2 EU award complaints",
)
class CompetitiveDialogueStage2EUAwardComplaintResource(TenderEUAwardComplaintResource):
    """ """


@optendersresource(
    name="{}:Tender Award Claims".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue Stage 2 EU award claims",
)
class CompetitiveDialogueStage2EUAwardClaimResource(TenderEUAwardClaimResource):
    pass


@optendersresource(
    name="{}:Tender Award Complaints Get".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue Stage 2 UA award complaints get",
)
class CompetitiveDialogueStage2UAAwardComplaintGetResource(BaseComplaintGetResource):
    """ """


@optendersresource(
    name="{}:Tender Award Complaints".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue Stage 2 UA award complaints",
)
class CompetitiveDialogueStage2UAAwardComplaintResource(TenderUAAwardComplaintResource):
    """ """


@optendersresource(
    name="{}:Tender Award Claims".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue Stage 2 UA award claims",
)
class CompetitiveDialogueStage2UAAwardClaimResource(TenderUAAwardClaimResource):
    """ """

# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_complaint import (
    TenderEUQualificationComplaintResource,
    TenderEUQualificationClaimResource,
)
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource
)
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE


@qualifications_resource(
    name="{}:Tender Qualification Complaints Get".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue Stage 2 EU qualification complaints get",
)
class CompetitiveDialogueEUQualificationComplaintGetResource(BaseComplaintGetResource):
    """ """


@qualifications_resource(
    name="{}:Tender Qualification Complaints".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue Stage 2 EU qualification complaints",
)
class CompetitiveDialogueStage2EUQualificationComplaintResource(TenderEUQualificationComplaintResource):
    """ """


@qualifications_resource(
    name="{}:Tender Qualification Claims".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue Stage 2 EU qualification claims",
)
class CompetitiveDialogueStage2EUQualificationClaimResource(TenderEUQualificationClaimResource):
    """ """

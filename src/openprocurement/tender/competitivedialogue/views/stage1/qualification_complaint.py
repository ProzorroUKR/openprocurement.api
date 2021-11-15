# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_complaint import (
    TenderEUQualificationComplaintResource as BaseTenderQualificationComplaintResource,
    TenderEUQualificationClaimResource as BaseTenderQualificationClaimResource,
)
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource
)
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@qualifications_resource(
    name="{}:Tender Qualification Complaints Get".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=CD_EU_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue EU qualification complaints get",
)
class CompetitiveDialogueEUQualificationComplaintGetResource(BaseComplaintGetResource):
    """ """


@qualifications_resource(
    name="{}:Tender Qualification Complaints".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=CD_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue EU qualification complaints",
)
class CompetitiveDialogueEUQualificationComplaintResource(BaseTenderQualificationComplaintResource):
    """ """


@qualifications_resource(
    name="{}:Tender Qualification Claims".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=CD_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue EU qualification claims",
)
class CompetitiveDialogueEUQualificationClaimResource(BaseTenderQualificationClaimResource):
    """ """


@qualifications_resource(
    name="{}:Tender Qualification Complaints Get".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=CD_UA_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue UA qualification complaints get",
)
class CompetitiveDialogueUAQualificationComplaintGetResource(BaseComplaintGetResource):
    """ """


@qualifications_resource(
    name="{}:Tender Qualification Complaints".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType=CD_UA_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue UA qualification complaints",
)
class CompetitiveDialogueUAQualificationComplaintResource(BaseTenderQualificationComplaintResource):
    """ """


@qualifications_resource(
    name="{}:Tender Qualification Claims".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA qualification claims",
)
class CompetitiveDialogueUAQualificationClaimResource(BaseTenderQualificationClaimResource):
    """ """

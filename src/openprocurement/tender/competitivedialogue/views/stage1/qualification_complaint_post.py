# -*- coding: utf-8 -*-
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_complaint_post import (
    TenderQualificationComplaintPostResource as BaseTenderQualificationComplaintPostResource
)


@qualifications_resource(
    name="{}:Tender Qualification Complaint Posts".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender qualification complaint posts",
)
class TenderCompetitiveDialogueEUQualificationComplaintPostResource(BaseTenderQualificationComplaintPostResource):
    pass



@qualifications_resource(
    name="{}:Tender Qualification Complaint Posts".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender qualification complaint posts",
)
class TenderCompetitiveDialogueUAQualificationComplaintPostResource(BaseTenderQualificationComplaintPostResource):
    pass

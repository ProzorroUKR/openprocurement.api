# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_complaint_post import (
    TenderQualificationComplaintPostResource as BaseTenderQualificationComplaintPostResource
)


@qualifications_resource(
    name="esco:Tender Qualification Complaint Posts",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="esco",
    description="Tender qualification complaint posts",
)
class TenderQualificationComplaintPostResource(BaseTenderQualificationComplaintPostResource):
    pass

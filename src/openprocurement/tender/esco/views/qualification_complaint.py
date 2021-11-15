# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_complaint import (
    TenderEUQualificationComplaintResource,
    TenderEUQualificationClaimResource,
)
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource
)


@qualifications_resource(
    name="esco:Tender Qualification Complaints Get",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["GET"],
    description="Tender EU qualification complaints get",
)
class TenderESCOQualificationComplaintGetResource(BaseComplaintGetResource):
    """ """


@qualifications_resource(
    name="esco:Tender Qualification Complaints",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender ESCO qualification complaints",
)
class TenderESCOQualificationComplaintResource(TenderEUQualificationComplaintResource):
    """ Tender ESCO Qualification Complaints Resource """


@qualifications_resource(
    name="esco:Tender Qualification Claims",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender ESCO qualification claims",
)
class TenderESCOQualificationClaimsResource(TenderEUQualificationClaimResource):
    """ Tender ESCO Qualification Claims Resource """

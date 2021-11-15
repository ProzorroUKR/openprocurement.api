# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.award_complaint import (
    TenderEUAwardComplaintResource,
    TenderEUAwardClaimResource,
)
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource,
)

@optendersresource(
    name="esco:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["GET"],
    description="Tender ESCO award complaints get",
)
class TenderESCOComplaintGetResource(BaseComplaintGetResource):
    """ Tender ESCO Award Complaint Get Resource """


@optendersresource(
    name="esco:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender ESCO award complaints",
)
class TenderESCOAwardComplaintResource(TenderEUAwardComplaintResource):
    """ Tender ESCO Award Complaint Resource """


@optendersresource(
    name="esco:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender ESCO award claims",
)
class TenderESCOAwardClaimResource(TenderEUAwardClaimResource):
    """ Tender ESCO Award Claims Resource """

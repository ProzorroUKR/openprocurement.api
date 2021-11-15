# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.complaint import TenderEUComplaintResource, TenderEUClaimResource
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource,
)


@optendersresource(
    name="esco:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["GET"],
    description="Tender ESCO complaints get",
)
class TenderESCOComplaintGetResource(BaseComplaintGetResource):
    """ Tender ESCO Complaint Get Resource """


@optendersresource(
    name="esco:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender ESCO Complaints",
)
class TenderESCOComplaintResource(TenderEUComplaintResource):
    """ Tender ESCO Complaint Resource """


@optendersresource(
    name="esco:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender ESCO Claims",
)
class TenderESCOClaimResource(TenderEUClaimResource):
    """ Tender ESCO Claim Resource """

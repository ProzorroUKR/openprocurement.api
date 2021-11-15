# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource,
)
from openprocurement.tender.openuadefense.views.complaint import (
    TenderUaComplaintResource as BaseTenderComplaintResource,
    TenderUaClaimResource as BaseTenderClaimResource,
)


@optendersresource(
    name="simple.defense:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    request_method=["GET"],
    description="Tender complaints get",
)
class TenderSimpleComplaintGetResource(BaseComplaintGetResource):
    """"""


@optendersresource(
    name="simple.defense:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
)
class TenderSimpleComplaintResource(BaseTenderComplaintResource):
    """"""


@optendersresource(
    name="simple.defense:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class TenderSimpleClaimResource(BaseTenderClaimResource):
    """"""

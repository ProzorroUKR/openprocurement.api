# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openuadefense.views.award_complaint import (
    TenderUaAwardComplaintResource,
    TenderUaAwardClaimResource,
)
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource,
)


@optendersresource(
    name="simple.defense:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    request_method=["GET"],
    description="Tender award complaints get",
)
class TenderSimpleDefAwardComplaintGetResource(BaseComplaintGetResource):
    """"""


@optendersresource(
    name="simple.defense:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
)
class TenderSimpleDefAwardComplaintResource(TenderUaAwardComplaintResource):
    """"""


@optendersresource(
    name="simple.defense:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class TenderSimpleDefAwardClaimResource(TenderUaAwardClaimResource):
    """"""

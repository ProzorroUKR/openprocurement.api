# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.complaint import TenderUAComplaintResource, TenderUAClaimResource
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource,
)


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["GET"],
    description="Tender EU complaints get",
)
class TenderEUComplaintGetResource(BaseComplaintGetResource):
    """"""


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender EU complaints",
)
class TenderEUComplaintResource(TenderUAComplaintResource):
    """ """


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender EU claims",
)
class TenderEUClaimResource(TenderUAClaimResource):
    """ """

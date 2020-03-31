# -*- coding: utf-8 -*-

from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.award_complaint_document import\
    TenderAwardComplaintDocumentResource
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Award Complaint Documents".format(PMT),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=PMT,
    description="Tender award complaint documents",
)
class PQTenderAwardComplaintDocumentResource(TenderAwardComplaintDocumentResource):
    """PriceQuotation award complaint document """

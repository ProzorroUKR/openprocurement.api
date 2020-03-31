# -*- coding: utf-8 -*-

from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.complaint_document import\
    TenderComplaintDocumentResource as BasetComplaintDocumentResource

from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Complaint Documents".format(PMT),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=PMT,
    description="Tender complaint documents",
)
class TenderComplaintDocumentResource(BasetComplaintDocumentResource):
    """ PriceQuotation complaint document resource """

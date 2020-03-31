# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.cancellation_document import\
    TenderCancellationDocumentResource

from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Cancellation Documents".format(PMT),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
    procurementMethodType=PMT,
    description="Tender cancellation documents",
)
class TenderCancellationDocumentResource(TenderCancellationDocumentResource):
    """ PriceQuotation cancellation document """

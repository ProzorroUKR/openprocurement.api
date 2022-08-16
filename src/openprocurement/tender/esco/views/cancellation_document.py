# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.cancellation_document import (
    TenderCancellationDocumentResource as TenderEUCancellationDocumentResource,
)


# @optendersresource(
#     name="esco:Tender Cancellation Documents",
#     collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents",
#     path="/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO cancellation documents",
# )
class TenderESCOCancellationDocumentResource(TenderEUCancellationDocumentResource):
    """ Tender ESCO Cancellation Document Resource """

# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.cancellation_document import (
    TenderUaCancellationDocumentResource as TenderCancellationDocumentResource
)


@optendersresource(name='aboveThresholdUA.defense:Tender Cancellation Documents',
                   collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
                   procurementMethodType='aboveThresholdUA.defense',
                   description="Tender UA.defense cancellation documents")
class TenderUaCancellationDocumentResource(TenderCancellationDocumentResource):
    """ """

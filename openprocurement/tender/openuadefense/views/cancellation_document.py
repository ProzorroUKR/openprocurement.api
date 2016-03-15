# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.cancellation_document import TenderUaCancellationDocumentResource as TenderCancellationDocumentResource


@opresource(name='Tender UA.defense Cancellation Documents',
            collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender UA.defense cancellation documents")
class TenderUaCancellationDocumentResource(TenderCancellationDocumentResource):
    """ """

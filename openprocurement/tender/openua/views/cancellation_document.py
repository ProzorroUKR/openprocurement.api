# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.api.views.cancellation_document import TenderCancellationDocumentResource

LOGGER = getLogger(__name__)


@opresource(name='Tender UA Cancellation Documents',
            collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender UA cancellation documents")
class TenderUaCancellationDocumentResource(TenderCancellationDocumentResource):
    pass

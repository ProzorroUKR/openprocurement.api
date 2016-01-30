# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.api.views.cancellation_document import TenderCancellationDocumentResource as BaseResource

LOGGER = getLogger(__name__)


@opresource(name='Tender EU Cancellation Documents',
            collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU cancellation documents")
class TenderCancellationDocumentResource(BaseResource):
   """ Cancellation Document """

# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.cancellation_document import (
    TenderCancellationDocumentResource as BaseResource
)


@optendersresource(name='aboveThresholdEU:Tender Cancellation Documents',
                   collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
                   procurementMethodType='aboveThresholdEU',
                   description="Tender EU cancellation documents")
class TenderCancellationDocumentResource(BaseResource):
    """ Cancellation Document """

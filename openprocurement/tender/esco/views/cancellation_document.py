# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.cancellation_document import TenderCancellationDocumentResource as TenderUACancellationDocumentResource
from openprocurement.tender.openeu.views.cancellation_document import TenderCancellationDocumentResource as TenderEUCancellationDocumentResource


@optendersresource(name='Tender ESCO UA Cancellation Documents',
            collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
            procurementMethodType='esco.UA',
            description="Tender ESCO UA cancellation documents")
class TenderESCOUACancellationDocumentResource(TenderUACancellationDocumentResource):
    """ Tender ESCO UA Cancellation Document Resource """


@optendersresource(name='Tender ESCO EU Cancellation Documents',
            collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU cancellation documents")
class TenderESCOEUCancellationDocumentResource(TenderEUCancellationDocumentResource):
    """ Tender ESCO EU Cancellation Document Resource """

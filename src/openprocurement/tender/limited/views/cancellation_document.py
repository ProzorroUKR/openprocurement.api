# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.cancellation_document import TenderCancellationDocumentResource as BaseResource


@optendersresource(name='reporting:Tender Cancellation Documents',
                   collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
                   procurementMethodType='reporting',
                   description="Tender cancellation documents")
class TenderCancellationDocumentResource(BaseResource):
    """ Tender Limited Cancellation Documents """


@optendersresource(name='negotiation:Tender Cancellation Documents',
                   collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
                   procurementMethodType='negotiation',
                   description="Tender cancellation documents")
class TenderNegotiationCancellationDocumentResource(TenderCancellationDocumentResource):
    """ Tender Negotiation Cancellation Documents """


@optendersresource(name='negotiation.quick:Tender Cancellation Documents',
                   collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
                   procurementMethodType='negotiation.quick',
                   description="Tender cancellation documents")
class TenderNegotiationQuickCancellationDocumentResource(TenderNegotiationCancellationDocumentResource):
    """ Tender Negotiation Quick Cancellation Documents """

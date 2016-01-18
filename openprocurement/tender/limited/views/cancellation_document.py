from openprocurement.api.utils import opresource
from openprocurement.api.views.cancellation_document import TenderCancellationDocumentResource as BaseResource


@opresource(name='Tender Limited Cancellation Documents',
            collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
            procurementMethodType='reporting',
            description="Tender cancellation documents")
class TenderCancellationDocumentResource(BaseResource):
    """ Tender Limited Cancellation Documents """

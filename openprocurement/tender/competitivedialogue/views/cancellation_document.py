# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.api.views.cancellation_document import TenderCancellationDocumentResource as BaseResource


@opresource(name='Competitive Dialogue  EU Cancellation Documents',
            collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdEU',
            description="Competitive Dialogue  EU cancellation documents")
class CompetitiveDialogueEUCancellationDocumentResource(BaseResource):
    """ Cancellation Document """
    pass


@opresource(name='Competitive Dialogue UA Cancellation Documents',
            collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdUA',
            description="Competitive Dialogue UA cancellation documents")
class CompetitiveDialogueUACancellationDocumentResource(BaseResource):
    """ Cancellation Document """
    pass

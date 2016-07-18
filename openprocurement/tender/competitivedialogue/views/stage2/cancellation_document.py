# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.cancellation_document import TenderCancellationDocumentResource as TenderCancellationDocumentEUResource
from openprocurement.tender.openua.views.cancellation_document import TenderCancellationDocumentResource as TenderCancellationDocumentUAResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@opresource(name='Competitive Dialogue stage2 EU Cancellation Documents',
            collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Competitive Dialogue stage2 EU cancellation documents")
class CompetitiveDialogueEUCancellationDocumentResource(TenderCancellationDocumentEUResource):
    """ Cancellation Document """
    pass


@opresource(name='Competitive Dialogue stage2 UA Cancellation Documents',
            collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue stage2 UA cancellation documents")
class CompetitiveDialogueUACancellationDocumentResource(TenderCancellationDocumentUAResource):
    """ Cancellation Document """
    pass

# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.cancellation_document import (
    TenderCancellationDocumentResource as TenderCancellationDocumentEUResource
)
from openprocurement.tender.openua.views.cancellation_document import (
    TenderCancellationDocumentResource as TenderCancellationDocumentUAResource
)
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
)


@optendersresource(name='{}:Tender Cancellation Documents'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Competitive Dialogue stage2 EU cancellation documents")
class CompetitiveDialogueEUCancellationDocumentResource(TenderCancellationDocumentEUResource):
    """ Cancellation Document """
    pass


@optendersresource(name='{}:Tender Cancellation Documents'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Competitive Dialogue stage2 UA cancellation documents")
class CompetitiveDialogueUACancellationDocumentResource(TenderCancellationDocumentUAResource):
    """ Cancellation Document """
    pass

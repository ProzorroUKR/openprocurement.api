# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.cancellation_document import (
    TenderCancellationDocumentResource as BaseResource
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE, CD_UA_TYPE
)


@optendersresource(name='{}:Tender Cancellation Documents'.format(CD_EU_TYPE),
                   collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
                   procurementMethodType=CD_EU_TYPE,
                   description="Competitive Dialogue  EU cancellation documents")
class CompetitiveDialogueEUCancellationDocumentResource(BaseResource):
    """ Cancellation Document """
    pass


@optendersresource(name='{}:Tender Cancellation Documents'.format(CD_UA_TYPE),
                   collection_path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}/documents/{document_id}',
                   procurementMethodType=CD_UA_TYPE,
                   description="Competitive Dialogue UA cancellation documents")
class CompetitiveDialogueUACancellationDocumentResource(BaseResource):
    """ Cancellation Document """
    pass

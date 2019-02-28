# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.cancellation import (
    TenderCancellationResource
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE, CD_UA_TYPE
)


@optendersresource(name='{}:Tender Cancellations'.format(CD_EU_TYPE),
                   collection_path='/tenders/{tender_id}/cancellations',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}',
                   procurementMethodType=CD_EU_TYPE,
                   description="Competitive Dialogue UE cancellations")
class CompetitiveDialogueEUCancellationResource(TenderCancellationResource):
    """ TenderEU Cancellations """
    pass


@optendersresource(name='{}:Tender Cancellations'.format(CD_UA_TYPE),
                   collection_path='/tenders/{tender_id}/cancellations',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}',
                   procurementMethodType=CD_UA_TYPE,
                   description="Competitive Dialogue UA cancellations")
class CompetitiveDialogueUACancellationResource(TenderCancellationResource):
    """ TenderUA Cancellations """
    pass

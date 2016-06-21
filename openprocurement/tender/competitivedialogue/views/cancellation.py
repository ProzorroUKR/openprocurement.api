# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.cancellation import TenderCancellationResource
from openprocurement.tender.competitivedialogue.models import CD_EU_TYPE, CD_UA_TYPE


@opresource(name='Competitive Dialogue EU Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType=CD_EU_TYPE,
            description="Competitive Dialogue UE cancellations")
class CompetitiveDialogueEUCancellationResource(TenderCancellationResource):
    """ TenderEU Cancellations """
    pass


@opresource(name='Competitive Dialogue UA Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType=CD_UA_TYPE,
            description="Competitive Dialogue UA cancellations")
class CompetitiveDialogueUACancellationResource(TenderCancellationResource):
    """ TenderUA Cancellations """
    pass

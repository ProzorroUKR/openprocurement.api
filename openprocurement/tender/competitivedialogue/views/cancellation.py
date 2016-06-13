# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.cancellation import TenderCancellationResource


@opresource(name='Competitive Dialogue UA Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdUA',
            description="Competitive Dialogue UA cancellations")
class CompetitiveDialogueUACancellationResource(TenderCancellationResource):
    pass


@opresource(name='Competitive Dialogue EU Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdEU',
            description="Competitive Dialogue UE cancellations")
class CompetitiveDialogueEUCancellationResource(TenderCancellationResource):
    """ TenderEU Cancellations """
    pass

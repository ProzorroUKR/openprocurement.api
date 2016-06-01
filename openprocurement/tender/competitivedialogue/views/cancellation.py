# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.api.views.cancellation import TenderCancellationResource
from openprocurement.tender.competitivedialogue.utils import (cancellation_ua_cancel_lot, cancellation_eu_cancel_lot,
                                                              cancellation_eu_cancel_tender)


@opresource(name='Competitive Dialogue UA Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdUA',
            description="Competitive Dialogue UA cancellations")
class CompetitiveDialogueUACancellationResource(TenderCancellationResource):

    def cancel_lot(self, cancellation=None):
        return cancellation_ua_cancel_lot(self, cancellation=cancellation)


@opresource(name='Competitive Dialogue EU Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdEU',
            description="Competitive Dialogue UE cancellations")
class CompetitiveDialogueEUCancellationResource(TenderCancellationResource):
    """ TenderEU Cancellations """

    def cancel_tender(self):
        return cancellation_eu_cancel_tender(self)

    def cancel_lot(self, cancellation=None):
        return cancellation_eu_cancel_lot(self, cancellation=cancellation)

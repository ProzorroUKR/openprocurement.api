# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.cancellation import TenderUaCancellationResource
from openprocurement.tender.openeu.utils import CancelTenderLot


@optendersresource(
    name="aboveThresholdEU:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender cancellations",
)
class TenderCancellationResource(TenderUaCancellationResource):
    @staticmethod
    def cancel_tender_lot_method(request, cancellation):
        return CancelTenderLot()(request, cancellation)

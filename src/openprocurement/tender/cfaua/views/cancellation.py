# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.cancellation import TenderCancellationResource as BaseCancellationResource
from openprocurement.tender.cfaua.utils import CancelTenderLot


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellations",
)
class TenderCancellationResource(BaseCancellationResource):

    @staticmethod
    def cancel_tender_lot_method(request, cancellation):
        return CancelTenderLot()(request, cancellation)

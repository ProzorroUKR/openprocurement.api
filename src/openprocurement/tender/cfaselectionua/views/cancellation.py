# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.cfaselectionua.utils import CancelTenderLot
from openprocurement.tender.belowthreshold.views.cancellation import \
    TenderCancellationResource as BaseTenderCancellationResource


@optendersresource(
    name="closeFrameworkAgreementSelectionUA:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender cancellations",
)
class TenderCancellationResource(BaseTenderCancellationResource):

    @staticmethod
    def cancel_tender_lot_method(request, cancellation):
        return CancelTenderLot()(request, cancellation)

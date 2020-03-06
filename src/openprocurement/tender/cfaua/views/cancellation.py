# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.cancellation import TenderCancellationResource as BaseCancellationResource
from openprocurement.tender.cfaua.utils import cancel_tender


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellations",
)
class TenderCancellationResource(BaseCancellationResource):

    @staticmethod
    def cancel_tender_method(request):
        return cancel_tender(request)

    def cancel_lot(self, cancellation):
        super(TenderCancellationResource, self).cancel_lot(cancellation)

        # cancel agreements
        tender = self.request.validated["tender"]
        if tender.status == "active.awarded" and tender.agreements:
            cancelled_lots = {i.id for i in tender.lots if i.status == "cancelled"}
            for agreement in tender.agreements:
                if agreement.get_lot_id() in cancelled_lots:
                    agreement.status = "cancelled"

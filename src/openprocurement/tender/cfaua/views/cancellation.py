# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.cancellation import TenderCancellationResource as BaseCancellationResource


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellations",
)
class TenderCancellationResource(BaseCancellationResource):

    def cancel_tender(self):
        super(TenderCancellationResource, self).cancel_tender()

        # cancel agreements
        tender = self.request.validated["tender"]
        for agreement in tender.agreements:
            if agreement.status in ("pending", "active"):
                agreement.status = "cancelled"

    def cancel_lot(self, cancellation):
        super(TenderCancellationResource, self).cancel_lot(cancellation)

        # cancel agreements
        tender = self.request.validated["tender"]
        if tender.status == "active.awarded" and tender.agreements:
            cancelled_lots = {i.id for i in tender.lots if i.status == "cancelled"}
            for agreement in tender.agreements:
                if agreement.get_lot_id() in cancelled_lots:
                    agreement.status = "cancelled"

# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.cancellation import TenderUaCancellationResource
from openprocurement.tender.openeu.utils import cancel_tender


@optendersresource(
    name="aboveThresholdEU:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender cancellations",
)
class TenderCancellationResource(TenderUaCancellationResource):

    @staticmethod
    def cancel_tender_method(request):
        return cancel_tender(request)

    def cancel_lot(self, cancellation):
        tender = self.request.validated["tender"]
        self._cancel_lots(tender, cancellation)
        cancelled_lots, cancelled_items, cancelled_features = self._get_cancelled_lot_objects(tender)

        self._invalidate_lot_bids(tender, cancelled_lots=cancelled_lots, cancelled_features=cancelled_features)
        self._cancel_lot_qualifications(tender, cancelled_lots=cancelled_lots)
        self._lot_update_check_tender_status(tender)
        self._lot_update_check_next_award(tender)

    @staticmethod
    def _get_cancelled_lot_objects(tender):
        cancelled_lots = {i.id for i in tender.lots if i.status == "cancelled"}
        cancelled_items = {i.id for i in tender.items if i.relatedLot in cancelled_lots}
        cancelled_features = {
            i.code
            for i in (tender.features or [])
            if i.featureOf == "lot" and i.relatedItem in cancelled_lots
            or i.featureOf == "item" and i.relatedItem in cancelled_items
        }
        return cancelled_lots, cancelled_items, cancelled_features

    def _lot_update_check_next_award(self, tender):
        if tender.status == "active.auction" and all(
            i.auctionPeriod and i.auctionPeriod.endDate
            for i in self.request.validated["tender"].lots
            if i.status == "active"
        ):
            self.add_next_award_method(self.request)

    @staticmethod
    def _invalidate_lot_bids(tender, cancelled_lots, cancelled_features):
        check_statuses = (
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
        )
        if tender.status in check_statuses:
            def filter_docs(items):
                result = [i for i in items
                          if i.documentOf != "lot"
                          or i.relatedItem not in cancelled_lots]
                return result

            for bid in tender.bids:
                if tender.status == "active.tendering":
                    bid.documents = filter_docs(bid.documents)
                bid.financialDocuments = filter_docs(bid.financialDocuments)
                bid.eligibilityDocuments = filter_docs(bid.eligibilityDocuments)
                bid.qualificationDocuments = filter_docs(bid.qualificationDocuments)
                bid.parameters = [i for i in bid.parameters if i.code not in cancelled_features]
                bid.lotValues = [i for i in bid.lotValues if i.relatedLot not in cancelled_lots]
                if not bid.lotValues and bid.status in ["pending", "active"]:
                    bid.status = "invalid" if tender.status == "active.tendering" else "invalid.pre-qualification"

    @staticmethod
    def _cancel_lot_qualifications(tender, cancelled_lots):
        for qualification in tender.qualifications:
            if qualification.lotID in cancelled_lots:
                qualification.status = "cancelled"

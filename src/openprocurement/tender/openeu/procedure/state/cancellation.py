from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState
from openprocurement.tender.openua.procedure.state.cancellation import OpenUACancellationStateMixing


class OpenEUCancellationStateMixing(OpenUACancellationStateMixing):

    def cancel_tender(self, tender):
        if tender["status"] == "active.tendering":
            tender.pop("bids", None)
        elif tender["status"] in ("active.pre-qualification", "active.pre-qualification.stand-still", "active.auction"):
            for bid in tender.get("bids", ""):
                if bid["status"] in ("pending", "active"):
                    bid["status"] = "invalid.pre-qualification"
        self.set_object_status(tender, "cancelled")

    def cancel_lot(self, tender, cancellation):
        self._cancel_lot(tender, cancellation["relatedLot"])
        cancelled_lots, cancelled_items, cancelled_features = self._get_cancelled_lot_objects(tender)
        # invalidate lot bids
        if tender["status"] in (
            "active.tendering", "active.pre-qualification", "active.pre-qualification.stand-still", "active.auction",
        ):
            for bid in tender.get("bids", ""):
                bid["parameters"] = [i for i in bid.get("parameters", "") if i["code"] not in cancelled_features]
                if not bid["parameters"]:
                    del bid["parameters"]

                bid["lotValues"] = [i for i in bid.get("lotValues", "") if i["relatedLot"] not in cancelled_lots]
                if not bid["lotValues"] and bid["status"] in ("pending", "active"):
                    del bid["lotValues"]
                    bid["status"] = "invalid" if tender["status"] == "active.tendering" else "invalid.pre-qualification"
        # need to switch tender status ?
        self._lot_update_check_tender_status(tender)
        # need to add next award ?
        if tender["status"] == "active.auction" and all(
            "endDate" in i.get("auctionPeriod", "")
            for i in tender.get("lots", "")
            if i["status"] == "active"
        ):
            self.add_next_award()

    @staticmethod
    def _get_cancelled_lot_objects(tender):
        cancelled_lots = {i["id"] for i in tender.get("lots", "") if i["status"] == "cancelled"}
        cancelled_items = {i["id"] for i in tender.get("items", "") if i.get("relatedLot") in cancelled_lots}
        cancelled_features = {
            i["code"]
            for i in tender.get("features", "")
            if i.get("featureOf") == "lot" and i.get("relatedItem") in cancelled_lots
            or i.get("featureOf") == "item" and i.get("relatedItem") in cancelled_items
        }
        return cancelled_lots, cancelled_items, cancelled_features


class OpenEUCancellationState(OpenUACancellationStateMixing, OpenUATenderState):
    pass

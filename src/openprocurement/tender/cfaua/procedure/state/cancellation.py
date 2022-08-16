from openprocurement.tender.openeu.procedure.state.cancellation import OpenEUCancellationStateMixing
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState


class CFAUACancellationStateMixing(OpenEUCancellationStateMixing):
    # + cancel agreements
    def cancel_lot(self, tender, cancellation):
        super().cancel_lot(tender, cancellation)

        if tender["status"] == "active.awarded" and tender.get("agreements"):
            cancelled_lots = {i["id"] for i in tender.get("lots", "") if i["status"] == "cancelled"}
            for agreement in tender.get("agreements", ""):
                if agreement["items"][0]["relatedLot"] in cancelled_lots:
                    self.set_object_status(agreement, "cancelled")

    def cancel_tender(self, tender):
        super().cancel_tender(tender)

        for agreement in tender.get("agreements", ""):
            if agreement["status"] in ("pending", "active"):
                self.set_object_status(agreement, "cancelled")


class CFAUACancellationState(CFAUACancellationStateMixing, CFAUATenderState):
    pass

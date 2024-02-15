from openprocurement.tender.belowthreshold.procedure.state.cancellation import BelowThresholdCancellationStateMixing
from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixing
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState
from openprocurement.api.utils import raise_operation_error


class ReportingCancellationStateMixing(BelowThresholdCancellationStateMixing):
    _before_release_reason_types = ["cancelled", "unsuccessful"]
    _after_release_reason_types = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]


class ReportingCancellationState(ReportingCancellationStateMixing, NegotiationTenderState):
    pass


class NegotiationCancellationStateMixing(CancellationStateMixing):
    _before_release_reason_types = ["cancelled", "unsuccessful"]
    _after_release_reason_types = ["noObjectiveness", "unFixable", "noDemand", "expensesCut", "dateViolation"]

    def validate_cancellation_post(self, data):
        super().validate_cancellation_post(data)

        request, tender = get_request(), get_tender()
        self.validate_absence_complete_lots_on_tender_cancel(request, tender, data)

    def validate_cancellation_patch(self, before, after):
        super().validate_cancellation_patch(before, after)

        request, tender = get_request(), get_tender()
        self.validate_absence_complete_lots_on_tender_cancel(request, tender, after)

    @staticmethod
    def validate_absence_complete_lots_on_tender_cancel(request, tender, cancellation):
        if tender.get("lots") and not cancellation.get("relatedLot"):
            for lot in tender.get("lots"):
                if lot["status"] == "complete":
                    raise_operation_error(request, "Can't perform cancellation, if there is at least one complete lot")

    @staticmethod
    def use_deprecated_activation(cancellation, tender):
        lot_id = cancellation.get("relatedLot")
        if not any(
            i["status"] == "active" for i in tender.get("awards", []) if i.get("lotID") == lot_id or lot_id is None
        ):
            return True


class NegotiationCancellationState(NegotiationCancellationStateMixing, NegotiationTenderState):
    pass

from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixing
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState
from openprocurement.tender.core.procedure.context import get_tender, get_request
from openprocurement.tender.core.procedure.utils import since_2020_rules


class BelowThresholdCancellationStateMixing(CancellationStateMixing):

    _before_release_reason_types = None
    _after_release_reason_types = ["noDemand", "unFixable", "expensesCut"]

    _after_release_statuses = ["draft", "unsuccessful", "active"]

    def validate_cancellation_post(self, data):
        request, tender = get_request(), get_tender()
        self.validate_cancellation_in_allowed_tender_status(request, tender, data)
        self.validate_cancellation_of_active_lot(request, tender, data)

        self.validate_possible_reason_types(request, tender, data)
        self.validate_cancellation_possible_statuses(request, tender, data)

    def validate_cancellation_patch(self, before, after):
        request, tender = get_request(), get_tender()
        self.validate_cancellation_in_allowed_tender_status(request, tender, before)
        self.validate_cancellation_of_active_lot(request, tender, before)
        self.validate_cancellation_status_draft_pending(request, tender, before)

        self.validate_possible_reason_types(request, tender, after)
        self.validate_cancellation_possible_statuses(request, tender, after)


    def cancellation_status_up(self, before, after, cancellation):
        request, tender = get_request(), get_tender()
        if before in ("draft", "pending") and after == "active":
            if since_2020_rules() and (not cancellation["reason"] or not cancellation.get("documents")):
                raise_operation_error(
                    request,
                    "Fields reason, cancellationOf and documents must be filled "
                    "for switch cancellation to active status",
                    status=422,
                )
            self.cancel_tender_lot(cancellation)
        elif before == "draft" and after == "unsuccessful":
            pass
        else:
            raise_operation_error(request, f"Can't switch cancellation status from {before} to {after}")


class BelowThresholdCancellationState(BelowThresholdCancellationStateMixing, BelowThresholdTenderState):
    pass

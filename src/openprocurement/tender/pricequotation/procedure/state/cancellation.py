from openprocurement.tender.belowthreshold.procedure.state.cancellation import BelowThresholdCancellationStateMixing
from openprocurement.tender.pricequotation.procedure.state.tender import PriceQuotationTenderState
from openprocurement.tender.core.procedure.context import get_tender, get_request
from openprocurement.api.utils import raise_operation_error


class PQCancellationStateMixing(BelowThresholdCancellationStateMixing):
    _after_release_reason_types = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]

    def validate_cancellation_post(self, data):
        super().validate_cancellation_post(data)
        self.validate_not_draft_publishing()

    def validate_cancellation_patch(self, before, after):
        super().validate_cancellation_patch(before, after)
        self.validate_not_draft_publishing()

    @staticmethod
    def validate_not_draft_publishing():
        tender = get_tender()
        if tender["status"] == 'draft.publishing':
            raise_operation_error(
                get_request(),
                "Can't perform cancellation in current ({}) status".format("draft.publishing")
            )


class PQCancellationState(PQCancellationStateMixing, PriceQuotationTenderState):
    pass

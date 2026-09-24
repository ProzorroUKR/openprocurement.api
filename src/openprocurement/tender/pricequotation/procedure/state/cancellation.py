from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PQTenderState,
)


class PQCancellationStateMixin(CancellationStateMixin):
    _before_release_reason_types = None
    cancellation_complaint_period_check = False
    procurement_kinds_not_required_sign = ("other",)


class PQCancellationState(PQCancellationStateMixin, PQTenderState):
    pass

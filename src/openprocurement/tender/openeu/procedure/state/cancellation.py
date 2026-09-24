from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixin
from openprocurement.tender.core.procedure.state.tender import TenderState


class OpenEUCancellationStateMixin(CancellationStateMixin):
    cancellation_unsuccessful_items_check = True


class OpenEUCancellationState(OpenEUCancellationStateMixin, TenderState):
    award_class = Award

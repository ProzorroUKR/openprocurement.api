from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixing
from openprocurement.tender.core.procedure.state.tender import TenderState


class OpenEUCancellationStateMixing(CancellationStateMixing):
    cancellation_unsuccessful_items_check = True


class OpenEUCancellationState(OpenEUCancellationStateMixing, TenderState):
    award_class = Award

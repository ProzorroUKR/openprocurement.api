from openprocurement.api.context import get_request
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.arma.procedure.models.award import Award
from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.openua.procedure.state.award import (
    AwardState as BaseAwardState,
)


class AwardState(BaseAwardState, TenderState):
    award_class = Award

    def award_status_up_from_pending_to_active(self, award, tender):
        # todo: temporarily disable award activation for ARMA in order to stop at contracting stage
        raise_operation_error(
            get_request(),
            "Award activation is temporarily disabled",
            status=422,
            name="status",
        )

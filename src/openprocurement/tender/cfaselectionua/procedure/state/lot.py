from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.cfaselectionua.procedure.state.tender_details import CFASelectionTenderDetailsState
from openprocurement.tender.core.procedure.utils import validate_field


class TenderLotState(LotStateMixin, CFASelectionTenderDetailsState):

    def validate_minimal_step(self, data, before=None):
        # override to re-enable minimalStep required validation
        # it's required for cfaselectionua in lot level
        kwargs = {
            "before": before,
            "enabled": data["config"]["hasAuction"] is True,
        }
        validate_field(data, "minimalStep", **kwargs)

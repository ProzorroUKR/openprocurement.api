from openprocurement.tender.core.procedure.context import get_tender_config
from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState
from openprocurement.tender.core.procedure.utils import validate_field


class TenderLotState(LotStateMixin, CFASelectionTenderState):

    def validate_minimal_step(self, data, before=None):
        # override to re-enable minimalStep required validation
        # it's required for cfaselectionua in lot level
        config = get_tender_config()
        kwargs = {
            "before": before,
            "enabled": config.get("hasAuction") is True,
        }
        validate_field(data, "minimalStep", **kwargs)

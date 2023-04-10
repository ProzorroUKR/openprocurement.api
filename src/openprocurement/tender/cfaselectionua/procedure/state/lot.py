from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState


class TenderLotState(LotStateMixin, CFASelectionTenderState):

    def validate_minimal_step(self, data, before=None):
        # override to re-enable minimalStep required validation
        # it's required for cfaselectionua in lot level
        self._validate_auction_only_field("minimalStep", data, before=before)

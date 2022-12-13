from openprocurement.tender.belowthreshold.procedure.state.criterion_rg_requirement import (
    BelowThresholdRequirementStateMixin,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState


class CFASelectionRequirementState(BelowThresholdRequirementStateMixin, CFASelectionTenderState):
    def validate_on_post(self, data: dict) -> None:
        self._validate_operation_criterion_in_tender_status()

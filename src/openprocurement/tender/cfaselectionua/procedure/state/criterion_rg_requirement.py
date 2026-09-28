from openprocurement.tender.cfaselectionua.procedure.state.tender_details import (
    CFASelectionTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin


class CFASelectionRequirementState(RequirementStateMixin, CFASelectionTenderDetailsState):
    # the requirement ids uniqueness isn't checked when a requirement is added through the endpoint
    requirement_post_ids_uniq_check = False

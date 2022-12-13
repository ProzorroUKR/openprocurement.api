from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


class OpenEURequirementState(RequirementStateMixin, OpenEUTenderState):
    pass

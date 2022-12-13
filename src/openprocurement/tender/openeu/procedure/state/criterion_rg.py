from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


class OpenEURequirementGroupState(RequirementGroupStateMixin, OpenEUTenderState):
    pass

from openprocurement.tender.competitivedialogue.procedure.state.criterion_rg_requirement import CDRequirementState


class CDStage2RequirementState(CDRequirementState):
    criterion_owner_exempt_roles = ("Administrator", "admins")

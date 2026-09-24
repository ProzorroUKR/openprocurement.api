from openprocurement.tender.competitivedialogue.procedure.state.criterion_rg import CDRequirementGroupState


class CDStage2RequirementGroupState(CDRequirementGroupState):
    criterion_owner_exempt_roles = ("Administrator", "admins")

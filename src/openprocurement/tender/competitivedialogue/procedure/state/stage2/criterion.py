from openprocurement.tender.competitivedialogue.procedure.state.criterion import CDCriterionState


class CDStage2CriterionState(CDCriterionState):
    criterion_owner_exempt_roles = ("Administrator", "admins")

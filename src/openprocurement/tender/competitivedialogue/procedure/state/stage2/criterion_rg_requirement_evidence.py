from openprocurement.tender.competitivedialogue.procedure.state.criterion_rg_requirement_evidence import (
    CDEligibleEvidenceState,
)


class CDStage2EligibleEvidenceState(CDEligibleEvidenceState):
    criterion_owner_exempt_roles = ("Administrator", "admins")

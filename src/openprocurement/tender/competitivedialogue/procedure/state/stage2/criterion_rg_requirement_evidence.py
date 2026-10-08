from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDStage2EUTenderDetailsState,
    CDStage2UATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement_evidence import EligibleEvidenceStateMixin


class CDStage2EUEligibleEvidenceState(EligibleEvidenceStateMixin, CDStage2EUTenderDetailsState):
    pass


class CDStage2UAEligibleEvidenceState(EligibleEvidenceStateMixin, CDStage2UATenderDetailsState):
    pass

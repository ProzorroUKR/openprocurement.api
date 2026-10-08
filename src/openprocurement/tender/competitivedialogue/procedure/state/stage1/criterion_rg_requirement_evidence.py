from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1EUTenderDetailsState,
    CDStage1UATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement_evidence import EligibleEvidenceStateMixin


class CDStage1EUEligibleEvidenceState(EligibleEvidenceStateMixin, CDStage1EUTenderDetailsState):
    pass


class CDStage1UAEligibleEvidenceState(EligibleEvidenceStateMixin, CDStage1UATenderDetailsState):
    pass

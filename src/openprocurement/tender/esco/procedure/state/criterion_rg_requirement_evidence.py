from openprocurement.tender.core.procedure.state.criterion_rg_requirement_evidence import EligibleEvidenceStateMixin
from openprocurement.tender.esco.procedure.state.tender_details import (
    ESCOTenderDetailsState,
)


class ESCOEligibleEvidenceState(EligibleEvidenceStateMixin, ESCOTenderDetailsState):
    pass

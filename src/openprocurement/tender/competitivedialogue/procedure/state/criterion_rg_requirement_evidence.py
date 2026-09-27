from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1TenderDetailsStateMixin,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement_evidence import EligibleEvidenceStateMixin


class CDEligibleEvidenceState(EligibleEvidenceStateMixin, CDStage1TenderDetailsStateMixin):
    pass

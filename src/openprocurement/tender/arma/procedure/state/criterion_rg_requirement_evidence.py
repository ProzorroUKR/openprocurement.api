from openprocurement.tender.arma.procedure.state.tender_details import (
    ComplexAssetTenderDetailsState,
    SimpleAssetTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement_evidence import EligibleEvidenceStateMixin


class ComplexAssetEligibleEvidenceState(EligibleEvidenceStateMixin, ComplexAssetTenderDetailsState):
    pass


class SimpleAssetEligibleEvidenceState(EligibleEvidenceStateMixin, SimpleAssetTenderDetailsState):
    pass

from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender_details import (
    PQTenderDetailsState,
)


class PQRequirementState(RequirementStateMixin, PQTenderDetailsState):
    pass

from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender_details import (
    PQTenderDetailsState,
)


class PQRequirementGroupState(RequirementGroupStateMixin, PQTenderDetailsState):
    pass

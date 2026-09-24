from openprocurement.tender.core.procedure.state.criterion_rg import (
    RequirementGroupStateMixin,
)

# from openprocurement.tender.pricequotation.procedure.state.criterion import PQCriterionStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PQTenderState,
)

# class PQRequirementGroupStateMixin(PQCriterionStateMixin, RequirementGroupStateMixin):
#     pass


class PQRequirementGroupState(RequirementGroupStateMixin, PQTenderState):
    criterion_allowed_tender_statuses = ["draft"]

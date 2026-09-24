from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    RequirementStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.criterion import (
    RFPCriterionStatusesMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RFPTenderState,
)


class RFPRequirementValidationsMixin:
    requirement_models_by_classification = False
    requirement_change_allowed_tender_statuses = ("draft",)
    requirement_change_legacy_status = "active.enquiries"


class RFPRequirementStateMixin(
    RFPRequirementValidationsMixin,
    RFPCriterionStatusesMixin,
    RequirementStateMixin,
):
    pass


class RFPRequirementState(RFPRequirementStateMixin, RFPTenderState):
    requirement_put_allowed_tender_statuses = ["active.enquiries"]

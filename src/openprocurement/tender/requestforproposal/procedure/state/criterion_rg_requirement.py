from pyramid.request import Request

from openprocurement.api.constants_env import CRITERION_REQUIREMENT_STATUSES_FROM
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import get_first_revision_date, get_now
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    RequirementStateMixin,
)
from openprocurement.tender.core.procedure.validation import (
    base_validate_operation_ecriteria_objects,
)
from openprocurement.tender.requestforproposal.procedure.state.criterion import (
    BaseRequestForProposalCriterionStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class RequestForProposalRequirementValidationsMixin:
    request: Request

    def _validate_change_requirement_objects(self) -> None:
        valid_statuses = ["draft"]
        tender = get_tender()
        tender_creation_date = get_first_revision_date(tender, default=get_now())
        if tender_creation_date < CRITERION_REQUIREMENT_STATUSES_FROM:
            valid_statuses.append("active.enquiries")
        base_validate_operation_ecriteria_objects(self.request, valid_statuses)


class RequestForProposalRequirementStateMixin(
    RequestForProposalRequirementValidationsMixin,
    BaseRequestForProposalCriterionStateMixin,
    RequirementStateMixin,
):
    pass


class RequestForProposalRequirementState(RequestForProposalRequirementStateMixin, RequestForProposalTenderState):
    allowed_put_statuses = ["active.enquiries"]

    def validate_on_post(self, data: dict) -> None:
        self._validate_operation_criterion_in_tender_status()
        self._validate_ids_uniq()
        self.validate_action_with_exist_inspector_review_request()

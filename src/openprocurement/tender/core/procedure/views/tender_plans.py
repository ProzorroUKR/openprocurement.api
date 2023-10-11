from logging import getLogger

from cornice.resource import resource
from schematics.exceptions import ValidationError, ModelValidationError

from openprocurement.api.utils import json_view, handle_data_exceptions
from openprocurement.planning.api.utils import save_plan
from openprocurement.planning.api.validation import validate_plan_not_terminated, validate_plan_has_not_tender
from openprocurement.tender.core.procedure.models.tender_base import PlanRelation, validate_plans
from openprocurement.tender.core.procedure.serializers.plan import PlanSerializer
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_procurement_kind_is_central,
    validate_tender_in_draft, validate_procurement_type_of_first_stage, validate_item_owner,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.validation import (
    validate_tender_plan_data,
    validate_plan_budget_breakdown,
    validate_tender_matches_plan,
)

LOGGER = getLogger(__name__)


@resource(
    name="Tender plans",
    path="/tenders/{tender_id}/plans",
    description="Tender plans relation endpoint"
)
class TenderPlansResource(TenderBaseResource):
    serializer_class = PlanSerializer

    @json_view()
    def get(self):
        tender = self.request.validated["tender"]
        data = [self.serializer_class(b).data for b in tender.get("plans", "")]
        return {"data": data}

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PlanRelation),
            validate_tender_plan_data,
            validate_procurement_kind_is_central,
            validate_tender_in_draft,
            validate_plan_not_terminated,
            validate_plan_has_not_tender,  # we need this because of the plans created before the statuses release
            validate_plan_budget_breakdown,
            validate_procurement_type_of_first_stage,
            validate_tender_matches_plan,  # procuringEntity and items classification group
        ),
        permission="edit_tender",
    )
    def post(self):
        tender = self.request.validated["tender"]
        plan_relation = self.request.validated["data"]
        plan = self.request.validated["plan"]

        if "plans" not in tender:
            tender["plans"] = []
        tender["plans"].append(plan_relation)

        with handle_data_exceptions(self.request):
            # mimic old style validation
            # TODO: refactor this
            try:
                validate_plans(tender, tender["plans"])
            except ValidationError as e:
                raise ModelValidationError({"plans": e})

        save_tender(self.request)
        if not self.request.errors:
            plan.tender_id = tender["_id"]
            save_plan(self.request)

        data = [self.serializer_class(b).data for b in tender.get("plans", "")]
        return {"data": data}

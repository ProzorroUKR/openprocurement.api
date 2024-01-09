from copy import deepcopy
from logging import getLogger

from cornice.resource import resource
from schematics.exceptions import ValidationError, ModelValidationError

from openprocurement.api.utils import json_view, handle_data_exceptions, error_handler
from openprocurement.planning.api.procedure.state.plan import PlanState
from openprocurement.planning.api.procedure.utils import save_plan
from openprocurement.tender.core.procedure.models.tender_base import PlanRelation, validate_plans
from openprocurement.tender.core.procedure.serializers.plan import PlanSerializer
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_item_owner,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource

LOGGER = getLogger(__name__)


@resource(
    name="Tender plans",
    path="/tenders/{tender_id}/plans",
    description="Tender plans relation endpoint"
)
class TenderPlansResource(TenderBaseResource):
    serializer_class = PlanSerializer
    plan_state_class = PlanState

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
        ),
        permission="edit_tender",
    )
    def post(self):
        tender = self.request.validated["tender"]
        plan_relation = self.request.validated["data"]

        # get plan
        plan_id = self.request.validated["data"]["id"]
        plan = self.request.registry.mongodb.plans.get(plan_id)
        if plan is None:
            self.request.errors.add("url", "plan_id", "Not Found")
            self.request.errors.status = 404
            raise error_handler(self.request)
        self.request.validated["plan"] = plan
        self.request.validated["plan_src"] = deepcopy(plan)

        # update tender
        if "plans" not in tender:
            tender["plans"] = []
        tender["plans"].append(plan_relation)

        # update plan
        plan_state = self.plan_state_class(self.request)
        plan_state.tender_plan_on_post(plan, tender)

        # mimic old style validation
        with handle_data_exceptions(self.request):
            # TODO: refactor this
            try:
                validate_plans(tender, tender["plans"])
            except ValidationError as e:
                raise ModelValidationError({"plans": e})

        # save
        save_tender(self.request)
        if not self.request.errors:
            save_plan(self.request)

        data = [self.serializer_class(b).data for b in tender.get("plans", "")]
        return {"data": data}

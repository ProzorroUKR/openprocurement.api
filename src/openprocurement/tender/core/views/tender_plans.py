from logging import getLogger
from openprocurement.api.utils import handle_store_exceptions, json_view
from openprocurement.api.views.base import BaseResource
from openprocurement.tender.core.utils import save_tender, optendersresource
from openprocurement.tender.core.validation import (
    validate_tender_plan_data,
    validate_procurement_type_of_first_stage,
    validate_tender_matches_plan,
    validate_plan_budget_breakdown,
    validate_procurement_kind_is_central,
    validate_tender_in_draft,
)
from openprocurement.planning.api.validation import (
    validate_patch_plan_data,
    validate_plan_data,
    validate_plan_has_not_tender,
    validate_plan_with_tender,
    validate_plan_not_terminated,
    validate_plan_status_update,
)
from openprocurement.planning.api.utils import save_plan


LOGGER = getLogger(__name__)


@optendersresource(name="Tender plans", path="/tenders/{tender_id}/plans", description="Tender plans relation endpoint")
class TenderPlansResource(BaseResource):
    @json_view()
    def get(self):
        return {"data": self.context.serialize("view").get("plans", [])}

    @json_view(
        content_type="application/json",
        validators=(
            validate_procurement_kind_is_central,
            validate_tender_in_draft,
            validate_tender_plan_data,
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
        plan = self.request.validated["plan"]

        tender.link_plan(plan.id)
        save_tender(self.request, validate=True)
        if not self.request.errors:
            plan.tender_id = tender.id
            save_plan(self.request)

        return {"data": self.context.serialize("view").get("plans")}

from openprocurement.api.utils import json_view, context_unpack
from openprocurement.api.views.base import BaseResource
from openprocurement.planning.api.utils import save_plan, opresource
from openprocurement.relocation.api.utils import (
    extract_transfer,
    update_ownership,
    save_transfer,
    get_transfer_location,
)
from openprocurement.relocation.api.validation import (
    validate_ownership_data,
    validate_plan_accreditation_level,
    validate_plan_owner_accreditation_level,
    validate_plan,
    validate_plan_transfer_token,
)


@opresource(name="Plan ownership", path="/plans/{plan_id}/ownership", description="Plans Ownership")
class TenderResource(BaseResource):
    @json_view(
        permission="create_plan",
        validators=(
            validate_plan_accreditation_level,
            validate_plan_owner_accreditation_level,
            validate_ownership_data,
            validate_plan,
            validate_plan_transfer_token,
        ),
    )
    def post(self):
        plan = self.request.validated["plan"]
        data = self.request.validated["ownership_data"]

        location = get_transfer_location(self.request, "Plan", plan_id=plan.id)
        transfer = extract_transfer(self.request, transfer_id=data["id"])

        if transfer.get("usedFor") and transfer.get("usedFor") != location:
            self.request.errors.add("body", "transfer", "Transfer already used")
            self.request.errors.status = 403
            return

        update_ownership(plan, transfer)
        self.request.validated["plan"] = plan

        transfer.usedFor = location
        self.request.validated["transfer"] = transfer

        if save_transfer(self.request):
            self.LOGGER.info(
                "Updated transfer relation {}".format(transfer.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "transfer_relation_update"}),
            )

            if save_plan(self.request):
                self.LOGGER.info(
                    "Updated ownership of tender {}".format(plan.id),
                    extra=context_unpack(self.request, {"MESSAGE_ID": "plan_ownership_update"}),
                )

                return {"data": plan.serialize("view")}

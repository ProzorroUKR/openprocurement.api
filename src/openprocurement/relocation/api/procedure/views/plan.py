from cornice.resource import resource

from openprocurement.api.utils import context_unpack, json_view
from openprocurement.planning.api.procedure.utils import save_plan
from openprocurement.planning.api.procedure.views.base import PlanBaseResource
from openprocurement.relocation.api.procedure.serializers.plan import (
    TransferredPlanSerializer,
)
from openprocurement.relocation.api.procedure.utils import (
    save_transfer,
    update_ownership,
)
from openprocurement.relocation.api.procedure.validation import (
    validate_ownership_data,
    validate_plan,
    validate_plan_owner_accreditation_level,
    validate_plan_transfer_accreditation_level,
    validate_plan_transfer_token,
)
from openprocurement.relocation.api.utils import (
    extract_transfer_doc,
    get_transfer_location,
)


@resource(
    name="Plan ownership",
    path="/plans/{plan_id}/ownership",
    description="Plans Ownership",
)
class PlanResource(PlanBaseResource):
    serializer_class = TransferredPlanSerializer

    @json_view(
        permission="create_plan",
        validators=(
            validate_plan_transfer_accreditation_level,
            validate_plan_owner_accreditation_level,
            validate_ownership_data,
            validate_plan,
            validate_plan_transfer_token,
        ),
    )
    def post(self):
        plan = self.request.validated["plan"]
        data = self.request.validated["ownership_data"]
        route_name = f"Plans"
        location = get_transfer_location(self.request, route_name, plan_id=plan["_id"])
        transfer = extract_transfer_doc(self.request, transfer_id=data["id"])

        if transfer.get("usedFor") and transfer.get("usedFor") != location:
            self.request.errors.add("body", "transfer", "Transfer already used")
            self.request.errors.status = 403
            return

        update_ownership(plan, transfer)
        self.request.validated["plan"] = plan

        transfer["usedFor"] = location
        self.request.validated["transfer"] = transfer

        if save_transfer(self.request):
            self.LOGGER.info(
                "Updated transfer relation {}".format(transfer["_id"]),
                extra=context_unpack(self.request, {"MESSAGE_ID": "transfer_relation_update"}),
            )

            if save_plan(self.request):
                self.LOGGER.info(
                    "Updated ownership of plan {}".format(plan["_id"]),
                    extra=context_unpack(self.request, {"MESSAGE_ID": "plan_ownership_update"}),
                )

                return {"data": self.serializer_class(plan).data}

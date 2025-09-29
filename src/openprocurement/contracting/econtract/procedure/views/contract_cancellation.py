from cornice.resource import resource

from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.utils import get_items
from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_in_pending_status,
    validate_contract_participant,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.contracting.econtract.procedure.models.cancellation import (
    PostContractCancellation,
)
from openprocurement.contracting.econtract.procedure.state.contract_cancellation import (
    CancellationState,
)


def resolve_cancellation(request):
    match_dict = request.matchdict
    if match_dict.get("cancellation_id"):
        cancellation_id = match_dict["cancellation_id"]
        contract = request.validated["contract"]
        cancellations = get_items(request, contract, "cancellations", cancellation_id)
        request.validated["cancellation"] = cancellations[0]


@resource(
    name="EContract cancellations",
    collection_path="/contracts/{contract_id}/cancellations",
    path="/contracts/{contract_id}/cancellations/{cancellation_id}",
    contractType="eContract",
    description="EContracts cancellations",
)
class EContractsCancellationsResource(ContractBaseResource):
    """Contract cancellations resource"""

    serializer_class = BaseSerializer
    state_class = CancellationState

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_cancellation(request)

    @json_view(permission="view_contract")
    def collection_get(self):
        """Return Contract Cancellations list"""
        return {
            "data": [self.serializer_class(i).data for i in self.request.validated["contract"].get("cancellations", "")]
        }

    @json_view(permission="view_contract")
    def get(self):
        """Return Contract Cancellation"""
        return {"data": self.serializer_class(self.request.validated["cancellation"]).data}

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_administrator(unless_admins(validate_contract_participant)),
            validate_input_data(PostContractCancellation),
            validate_contract_in_pending_status,
        ),
    )
    def collection_post(self):
        """Contract cancellation create"""
        contract = self.request.validated["contract"]

        cancellation = self.request.validated["data"]

        if not contract.get("cancellations"):
            contract["cancellations"] = []

        self.state.cancellation_on_post(cancellation)

        contract["cancellations"].append(cancellation)

        if save_contract(self.request):
            self.LOGGER.info(
                f"Created cancellation {cancellation['id']} for contract {contract['_id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "contract_cancellation_create"},
                    {"cancellation_id": cancellation["id"], "contract_id": contract["_id"]},
                ),
            )
            self.request.response.status = 201
            return {"data": self.serializer_class(cancellation).data}

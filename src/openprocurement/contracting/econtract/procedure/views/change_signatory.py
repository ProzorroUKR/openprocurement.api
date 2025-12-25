from cornice.resource import resource

from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.validation import unless_admins, validate_input_data
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_change_action_not_in_allowed_contract_status,
    validate_contract_change_update_not_in_allowed_change_status,
    validate_contract_participant,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.contracting.core.procedure.views.change import resolve_change
from openprocurement.contracting.econtract.procedure.models.signatory import (
    PostSignatory,
)
from openprocurement.contracting.econtract.procedure.state.change_signatory import (
    SignatoryState,
)


@resource(
    name="EContract change signatories",
    path="/contracts/{contract_id}/changes/{change_id}/signatories",
    contractType="eContract",
    description="EContracts Change Signatories",
)
class EContractsChangeSignatoriesResource(ContractBaseResource):
    serializer_class = BaseSerializer
    state_class = SignatoryState

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        if not context:
            resolve_change(request)

    @json_view(
        validators=(
            unless_admins(validate_contract_participant),
            validate_contract_change_action_not_in_allowed_contract_status,
            validate_contract_change_update_not_in_allowed_change_status,
            validate_input_data(PostSignatory),
        ),
        permission="edit_contract",
    )
    def post(self):
        contract = self.request.validated["contract"]
        change = self.request.validated["change"]

        signatory = self.request.validated["data"]

        if not change.get("signatories"):
            change["signatories"] = []

        self.state.signatory_on_post(signatory)

        change["signatories"].append(signatory)

        if save_contract(self.request):
            self.LOGGER.info(
                f"Created signatory for change {change['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "contract_signatory_create"},
                    {"change_id": change["id"], "contract_id": contract["_id"]},
                ),
            )
            self.request.response.status = 201
            return {"data": self.serializer_class(signatory).data}

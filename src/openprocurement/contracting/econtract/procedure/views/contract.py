from hashlib import sha512
from uuid import uuid4

from cornice.resource import resource

from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.validation import validate_input_data
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_in_pending_status,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.contracting.econtract.procedure.models.access import PostAccess
from openprocurement.contracting.econtract.procedure.state.contract_access import (
    ContractAccessState,
)


@resource(
    name="EContract access",
    path="/contracts/{contract_id}/access",
    contractType="eContract",
    description="Contract access",
)
class ContractAccessResource(ContractBaseResource):
    state_class = ContractAccessState
    serializer_class = BaseSerializer

    @json_view(
        permission="edit_contract", validators=(validate_input_data(PostAccess), validate_contract_in_pending_status)
    )
    def post(self):
        contract = self.request.validated["contract"]
        data = self.request.validated["data"]
        role = self.state.get_role(data, contract)
        self.state.validate_on_post(contract, role)
        token = uuid4().hex
        self.state.set_token(contract, role, token)

        access = {"token": token}

        if role == AccessRole.BUYER:
            transfer_token = uuid4().hex
            contract["transfer_token"] = sha512(transfer_token.encode("utf-8")).hexdigest()
            access["transfer"] = transfer_token

        if save_contract(self.request):
            self.LOGGER.info(
                f"Generate Contract access {contract['_id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
            )
            self.request.response.status = 201
            return {
                "data": self.serializer_class(data).data,
                "access": access,
            }

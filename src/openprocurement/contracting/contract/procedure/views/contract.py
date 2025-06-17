from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
    validate_patch_data_simple,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.procedure.models.contract import Contract
from openprocurement.contracting.core.procedure.serializers.contract import (
    ContractBaseSerializer,
)
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_owner,
    validate_contract_update_not_in_allowed_status,
    validate_credentials_generate,
    validate_tender_owner,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.contracting.core.procedure.views.contract import (
    ContractResource as BaseContractResource,
)
from openprocurement.contracting.core.procedure.views.contract import (
    conditional_contract_model,
)
from openprocurement.tender.core.procedure.utils import set_ownership


@resource(
    name="Contract",
    path="/contracts/{contract_id}",
    contractType="contract",
    description="Contracts operations",
    accept="application/json",
)
class ContractResource(BaseContractResource):
    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_admins(unless_administrator(validate_contract_owner)),
            validate_input_data(conditional_contract_model),
            validate_patch_data_simple(Contract, item_name="contract"),
            unless_admins(unless_administrator(validate_contract_update_not_in_allowed_status)),
        ),
    )
    def patch(self):
        return super().patch()


@resource(
    name="Contract credentials",
    path="/contracts/{contract_id}/credentials",
    contractType="contract",
    description="Contract credentials",
)
class ContractCredentialsResource(ContractBaseResource):
    serializer_class = ContractBaseSerializer

    @json_view(
        permission="edit_contract",
        validators=(
            unless_admins(validate_tender_owner),
            validate_credentials_generate,
        ),
    )
    def patch(self):
        contract = self.request.validated["contract"]
        access = set_ownership(contract, self.request, access_role=AccessRole.CONTRACT)
        if save_contract(self.request):
            self.LOGGER.info(
                f"Generate Contract credentials {contract['_id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
            )
            return {
                "data": self.serializer_class(contract).data,
                "config": contract["config"],
                "access": access,
            }

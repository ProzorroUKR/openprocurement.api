from cornice.resource import resource

from openprocurement.api.procedure.models.signer_info import SignerInfo
from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.contracting.contract.procedure.state.signer_info import (
    ContractSignerInfoState,
)
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_in_pending_status,
    validate_contract_owner,
    validate_contract_supplier,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource


class BaseSignerInfoResource(ContractBaseResource):
    state_class = ContractSignerInfoState
    serializer_class = BaseSerializer
    parent_obj_name: str

    def put(self):
        contract = self.request.validated["contract"]
        signer_info = self.request.validated["data"]

        parent_obj = contract[self.parent_obj_name]
        if self.parent_obj_name == "suppliers":
            parent_obj = contract[self.parent_obj_name][0]

        self.state.signer_info_on_put(signer_info)

        parent_obj["signerInfo"] = signer_info

        if save_contract(self.request):
            self.LOGGER.info(
                f"Updated contract {contract['_id']} {self.parent_obj_name} signerInfo",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": f"contract_{self.parent_obj_name}_signerInfo_put"},
                ),
            )
            return {"data": self.serializer_class(signer_info).data}


@resource(
    name="Contract buyer signerInfo",
    path="/contracts/{contract_id}/buyer/signer_info",
    description="Contracts buyer signer info operations",
    contractType="contract",
    accept="application/json",
)
class ContractBuyerSignerInfoResource(BaseSignerInfoResource):
    parent_obj_name = "buyer"

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_admins(unless_administrator(validate_contract_owner)),
            validate_input_data(SignerInfo),
            unless_admins(unless_administrator(validate_contract_in_pending_status)),
        ),
    )
    def put(self):
        return super().put()


@resource(
    name="Contract suppliers signerInfo",
    path="/contracts/{contract_id}/suppliers/signer_info",
    description="Contracts suppliers signer info operations",
    contractType="contract",
    accept="application/json",
)
class ContractSuppliersSignerInfoResource(BaseSignerInfoResource):
    parent_obj_name = "suppliers"

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_admins(unless_administrator(validate_contract_supplier)),
            validate_input_data(SignerInfo),
            unless_admins(unless_administrator(validate_contract_in_pending_status)),
        ),
    )
    def put(self):
        return super().put()

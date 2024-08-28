from cornice.resource import resource

from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_owner,
    validate_contract_supplier,
    validate_signer_info_update_in_not_allowed_status,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.contracting.econtract.procedure.models.organization import (
    SignerInfo,
)
from openprocurement.contracting.econtract.procedure.state.signer_info import (
    EContractSignerInfoState,
)


class BaseSignerInfoResource(ContractBaseResource):
    state_class = EContractSignerInfoState
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
    name="EContract buyer signerInfo",
    path="/contracts/{contract_id}/buyer/signer_info",
    description="Econtracts buyer signer info operations",
    accept="application/json",
)
class EContractBuyerSignerInfoResource(BaseSignerInfoResource):
    parent_obj_name = "buyer"

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_admins(unless_administrator(validate_contract_owner)),
            validate_input_data(SignerInfo),
            unless_admins(unless_administrator(validate_signer_info_update_in_not_allowed_status)),
        ),
    )
    def put(self):
        return super().put()


@resource(
    name="EContract suppliers signerInfo",
    path="/contracts/{contract_id}/suppliers/signer_info",
    description="Econtracts suppliers signer info operations",
    accept="application/json",
)
class EContractSuppliersSignerInfoResource(BaseSignerInfoResource):
    parent_obj_name = "suppliers"

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_admins(unless_administrator(validate_contract_supplier)),
            validate_input_data(SignerInfo),
            unless_admins(unless_administrator(validate_signer_info_update_in_not_allowed_status)),
        ),
    )
    def put(self):
        return super().put()

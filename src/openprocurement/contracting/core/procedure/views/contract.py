from cornice.resource import resource

from openprocurement.api.context import get_request
from openprocurement.api.database import atomic_transaction
from openprocurement.api.procedure.context import get_contract
from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
    validate_patch_data_simple,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.api.views.base import (
    MongodbResourceListing,
    RestrictedResourceListingMixin,
)
from openprocurement.contracting.core.procedure.mask import CONTRACT_MASK_MAPPING
from openprocurement.contracting.core.procedure.models.contract import (
    AdministratorPatchContract,
    Contract,
    PatchContract,
    PatchContractPending,
)
from openprocurement.contracting.core.procedure.serializers.contract import (
    ContractBaseSerializer,
)
from openprocurement.contracting.core.procedure.state.contract import ContractState
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_owner,
    validate_contract_update_not_in_allowed_status,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.tender.core.procedure.utils import save_tender


def conditional_contract_model(data):
    request = get_request()
    contract_status = request.validated["contract"]["status"]
    if request.authenticated_role == "Administrator":
        model = AdministratorPatchContract
    elif contract_status == "pending":
        model = PatchContractPending
    else:
        model = PatchContract
    return model(data)


@resource(
    name="Contracts",
    path="/contracts",
    description="Contracts listing",
    request_method=("GET",),
)
class ContractsResource(RestrictedResourceListingMixin, MongodbResourceListing, ContractBaseResource):
    listing_name = "Contracts"
    listing_default_fields = {
        "dateModified",
    }
    listing_allowed_fields = {
        "dateCreated",
        "contractID",
        "dateModified",
        "status",
    }
    mask_mapping = CONTRACT_MASK_MAPPING

    serializer_class = ContractBaseSerializer

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.db_listing_method = request.registry.mongodb.contracts.list


@resource(
    name="Contract",
    path="/contracts/{contract_id}",
    description="Contracts operations",
    accept="application/json",
)
class ContractResource(ContractBaseResource):
    state_class = ContractState
    serializer_class = ContractBaseSerializer

    @json_view(permission="view_contract")
    def get(self):
        contract = get_contract()
        return {
            "data": self.serializer_class(contract).data,
            "config": contract["config"],
        }

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
        """Contract Edit (partial)"""
        updated = self.request.validated["data"]
        contract_src = self.request.validated["contract_src"]
        if updated:
            contract = self.request.validated["contract"] = updated
            self.state.on_patch(contract_src, contract)
            with atomic_transaction():
                if save_contract(self.request):
                    if self.request.validated.get("contract_was_changed"):
                        if save_tender(self.request):
                            self.LOGGER.info(
                                f"Updated tender {self.request.validated['tender']['_id']} contract {contract['_id']}",
                                extra=context_unpack(
                                    self.request,
                                    {"MESSAGE_ID": "tender_contract_update_status"},
                                ),
                            )

                    self.LOGGER.info(
                        f"Updated contract {contract['_id']}",
                        extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
                    )
                    return {
                        "data": self.serializer_class(contract).data,
                        "config": contract["config"],
                    }

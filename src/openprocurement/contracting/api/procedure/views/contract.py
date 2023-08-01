from cornice.resource import resource

from openprocurement.api.utils import context_unpack, json_view
from openprocurement.api.views.base import MongodbResourceListing
from openprocurement.api.context import get_request
from openprocurement.api.auth import ACCR_3, ACCR_5
from openprocurement.contracting.api.procedure.utils import save_contract
from openprocurement.contracting.api.procedure.validation import (
    validate_update_contract_value_net_required,
    validate_update_contract_paid_net_required,
    validate_update_contracting_value_readonly,
    validate_update_contracting_value_identical,
    validate_update_contracting_value_amount,
    validate_update_contracting_paid_amount,
    validate_contract_update_not_in_allowed_status,
    validate_terminate_contract_without_amountPaid,
    validate_credentials_generate,
    validate_tender_owner,
)
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    unless_administrator,
    validate_item_owner,
)
from openprocurement.tender.core.procedure.validation import (
    validate_accreditation_level,
    validate_input_data,
    validate_patch_data_simple,
)
from openprocurement.contracting.api.procedure.models.contract import (
    PostContract,
    PatchContract,
    AdministratorPatchContract,
    Contract,
)
from openprocurement.contracting.api.procedure.views.base import ContractBaseResource
from openprocurement.contracting.api.procedure.serializers.contract import ContractBaseSerializer
from openprocurement.tender.core.procedure.utils import set_ownership


def conditional_contract_model(data):
    if get_request().authenticated_role == "Administrator":
        model = AdministratorPatchContract
    else:
        model = PatchContract
    return model(data)


@resource(
    name="Contracts",
    path="/contracts",
    description="Contracts listing",
    # request_method=("GET",),
)
class ContractsResource(MongodbResourceListing, ContractBaseResource):
    serializer_class = ContractBaseSerializer

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.listing_name = "Contracts"
        self.listing_default_fields = {"dateModified"}
        self.listing_allowed_fields = {"dateCreated", "contractID", "dateModified"}
        self.db_listing_method = request.registry.mongodb.contracts.list

    @json_view(
        content_type="application/json",
        permission="create_contract",
        validators=(
            validate_input_data(PostContract),
            validate_accreditation_level(
                levels=(ACCR_3, ACCR_5),
                item="contract",
                operation="creation",
                source="data",
            ),
        )
    )
    def post(self):
        contract = self.request.validated["data"]

        self.state.on_post(contract)

        self.request.validated["contract"] = contract
        self.request.validated["contract_src"] = {}
        if save_contract(self.request, insert=True):
            self.LOGGER.info(
                f"Created contract {contract['_id']} ({contract['contractID']})",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "contract_create"},
                    {"contract_id": contract["_id"], "contractID": contract["contractID"] or ""},
                ),
            )
            self.request.response.status = 201
            return {"data": self.serializer_class(contract).data, "access": {"token": contract["owner_token"]}}


@resource(
    name="Contract",
    # collection_path="/contracts",
    path="/contracts/{contract_id}",
    description="Base ontracts operations",
    accept="application/json",
)
class ContractResource(ContractBaseResource):
    serializer_class = ContractBaseSerializer

    @json_view(permission="view_contract")
    def get(self):
        return {"data": self.serializer_class(self.request.validated["contract"]).data}

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_admins(unless_administrator(validate_item_owner("contract"))),
            validate_input_data(conditional_contract_model),
            validate_patch_data_simple(Contract, item_name="contract"),
            unless_admins(unless_administrator(validate_contract_update_not_in_allowed_status)),
            validate_update_contract_value_net_required,
            validate_update_contract_paid_net_required,
            validate_update_contracting_value_readonly,
            validate_update_contracting_value_identical,
            validate_update_contracting_value_amount,
            validate_update_contracting_paid_amount,
            validate_terminate_contract_without_amountPaid,
        ),
    )
    def patch(self):
        """Contract Edit (partial)
        """
        updated = self.request.validated["data"]
        if updated:
            self.request.validated["contract"] = updated
            self.state.on_patch(self.request.validated["contract_src"], updated)
            if save_contract(self.request):
                self.LOGGER.info(
                    f"Updated contract {updated['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
                )
        return {"data": self.serializer_class(self.request.validated["contract"]).data}


@resource(
    name="Contract credentials", path="/contracts/{contract_id}/credentials", description="Contract credentials"
)
class ContractCredentialsResource(ContractBaseResource):

    serializer_class = ContractBaseSerializer

    @json_view(
        permission="edit_contract",
        validators=(
            unless_admins(validate_tender_owner),
            validate_credentials_generate,
        ))
    def patch(self):
        contract = self.request.validated["contract"]
        access = set_ownership(contract, self.request)
        if save_contract(self.request):
            self.LOGGER.info(
                f"Generate Contract credentials {contract['_id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
            )
            return {"data": self.serializer_class(contract).data, "access": access}

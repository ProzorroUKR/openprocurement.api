from cornice.resource import resource

from openprocurement.api.utils import context_unpack, json_view
from openprocurement.api.views.base import MongodbResourceListing
from openprocurement.api.auth import ACCR_3, ACCR_5
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_credentials_generate,
    validate_tender_owner,
)
from openprocurement.tender.core.procedure.validation import unless_admins
from openprocurement.tender.core.procedure.validation import (
    validate_accreditation_level,
    validate_input_data,
)
from openprocurement.contracting.api.procedure.models.contract import PostContract
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.contracting.core.procedure.serializers.contract import ContractBaseSerializer
from openprocurement.tender.core.procedure.utils import set_ownership


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


class ContractResource(ContractBaseResource):
    serializer_class = ContractBaseSerializer

    @json_view(permission="view_contract")
    def get(self):
        return {"data": self.serializer_class(self.request.validated["contract"]).data}

    @json_view(
        content_type="application/json",
        permission="edit_contract"
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
    name="Contract credentials",
    path="/contracts/{contract_id}/credentials",
    description="Contract credentials",
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

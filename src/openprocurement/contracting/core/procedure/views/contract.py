from hashlib import sha512
from uuid import uuid4

from cornice.resource import resource

from openprocurement.api.database import atomic_transaction
from openprocurement.api.procedure.context import get_contract
from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.validation import unless_admins, validate_input_data
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.api.views.base import (
    MongodbResourceListing,
    RestrictedResourceListingMixin,
)
from openprocurement.contracting.core.procedure.mask import CONTRACT_MASK_MAPPING
from openprocurement.contracting.core.procedure.models.access import (
    PatchAccess,
    PostAccess,
)
from openprocurement.contracting.core.procedure.serializers.contract import (
    ContractBaseSerializer,
)
from openprocurement.contracting.core.procedure.state.contract_access import (
    ContractAccessState,
)
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_in_pending_status,
    validate_credentials_generate,
    validate_tender_owner,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource
from openprocurement.tender.core.procedure.utils import save_tender, set_ownership


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


class ContractResource(ContractBaseResource):
    serializer_class = ContractBaseSerializer

    @json_view(permission="view_contract")
    def get(self):
        contract = get_contract()
        return {
            "data": self.serializer_class(contract).data,
            "config": contract["config"],
        }

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
        ),
    )
    def patch(self):
        contract = self.request.validated["contract"]
        access = set_ownership(contract, self.request)
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


@resource(
    name="Contract access",
    path="/contracts/{contract_id}/access",
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

        # TODO: ASK
        if role == "buyer":
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

    @json_view(
        permission="edit_contract", validators=(validate_input_data(PatchAccess), validate_contract_in_pending_status)
    )
    def patch(self):
        contract = self.request.validated["contract"]
        data = self.request.validated["data"]
        role = self.state.get_role(data, contract)
        self.state.validate_on_patch(contract, role)
        self.state.set_owner(contract, role)
        if save_contract(self.request):
            self.LOGGER.info(
                f"Submit Contract access {contract['_id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_patch"}),
            )
            return {"data": self.serializer_class(data).data}

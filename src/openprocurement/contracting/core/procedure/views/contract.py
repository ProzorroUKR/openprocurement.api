from cornice.resource import resource

from openprocurement.api.database import atomic_transaction
from openprocurement.api.procedure.context import get_contract
from openprocurement.api.procedure.validation import unless_admins
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.api.views.base import (
    MongodbResourceListing,
    RestrictedResourceListingMixin,
)
from openprocurement.contracting.core.procedure.mask import CONTRACT_MASK_MAPPING
from openprocurement.contracting.core.procedure.serializers.contract import (
    ContractBaseSerializer,
)
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
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

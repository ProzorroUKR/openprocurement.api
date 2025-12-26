from cornice.resource import resource

from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_contract
from openprocurement.api.utils import get_tender_by_id, json_view, request_init_tender
from openprocurement.api.views.base import (
    MongodbResourceListing,
    RestrictedResourceListingMixin,
)
from openprocurement.contracting.core.procedure.mask import CONTRACT_MASK_MAPPING
from openprocurement.contracting.core.procedure.models.contract import (
    AdministratorPatchContract,
    PatchContract,
    PatchContractPending,
)
from openprocurement.contracting.core.procedure.serializers.contract import (
    ContractBaseSerializer,
)
from openprocurement.contracting.core.procedure.state.contract import ContractState
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource


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
        "public_modified",
        "public_ts",
    }
    mask_mapping = CONTRACT_MASK_MAPPING

    serializer_class = ContractBaseSerializer

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.db_listing_method = request.registry.mongodb.contracts.list


class ContractResource(ContractBaseResource):
    state_class = ContractState
    serializer_class = ContractBaseSerializer

    @json_view(permission="view_contract")
    def get(self):
        contract = get_contract()
        if not contract.get("contractChangeRationaleTypes"):
            tender_doc = get_tender_by_id(self.request, contract["tender_id"])
            request_init_tender(self.request, tender_doc)
        return {
            "data": self.serializer_class(contract, tender=self.request.validated.get("tender")).data,
            "config": contract["config"],
        }

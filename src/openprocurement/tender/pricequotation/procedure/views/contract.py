from logging import getLogger

from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.validation import (
    validate_contract_input_data,
    validate_contract_supplier,
    validate_forbid_contract_action_after_date,
)
from openprocurement.tender.core.procedure.views.contract import TenderContractResource
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.procedure.models.contract import (
    Contract,
    PatchContract,
    PatchContractSupplier,
    PostContract,
)
from openprocurement.tender.pricequotation.procedure.state.contract import (
    PQContractState,
)

LOGGER = getLogger(__name__)


@resource(
    name=f"{PQ}:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType="priceQuotation",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class PQContractResource(TenderContractResource):
    state_class = PQContractState

    @json_view(
        content_type="application/json",
        permission="create_contract",
        validators=(
            validate_forbid_contract_action_after_date("contract"),
            validate_input_data(PostContract),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            validate_forbid_contract_action_after_date("contract"),
            unless_admins(validate_contract_supplier()),
            validate_contract_input_data(model=PatchContract, supplier_model=PatchContractSupplier),
            validate_patch_data_simple(Contract, item_name="contract"),
        ),
    )
    def patch(self):
        return super().patch()

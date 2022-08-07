from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.contract import TenderContractResource
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_patch_data_simple,
    validate_contract_supplier,
    validate_contract_input_data,
)
from openprocurement.tender.cfaselectionua.procedure.state.contract import CFASelectionContractState
from openprocurement.tender.cfaselectionua.procedure.models.contract import (
    Contract,
    PostContract,
    PatchContract,
    PatchContractSupplier,
)
from cornice.resource import resource
from logging import getLogger

LOGGER = getLogger(__name__)


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender contracts",
)
class CFASelectionContractResource(TenderContractResource):
    state_class = CFASelectionContractState

    @json_view(
        content_type="application/json",
        permission="create_contract",
        validators=(
            validate_input_data(PostContract),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_admins(validate_contract_supplier()),
            validate_contract_input_data(model=PatchContract, supplier_model=PatchContractSupplier),
            validate_patch_data_simple(Contract, item_name="contract"),
        ),
    )
    def patch(self):
        return super().patch()

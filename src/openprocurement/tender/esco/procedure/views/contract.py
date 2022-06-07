from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_patch_data_simple,
    validate_contract_supplier,
    validate_contract_operation_not_in_allowed_status,
    validate_update_contract_value_with_award,
    validate_update_contract_value_amount,
    validate_update_contract_value_net_required,
    validate_update_contract_status_by_supplier,
    validate_update_contract_status,
    validate_update_contract_only_for_active_lots,
    validate_update_contract_value,
    validate_contract_input_data,
)
from openprocurement.tender.openeu.procedure.views.contract import EUContractResource
from openprocurement.tender.openua.procedure.validation import validate_contract_update_with_accepted_complaint
from openprocurement.tender.esco.procedure.validation import validate_update_contract_value_esco
from openprocurement.tender.esco.procedure.serializers.contract import ContractSerializer
from openprocurement.tender.esco.procedure.models.contract import (
    Contract,
    PostContract,
    PatchContract,
    PatchContractSupplier,
)
from cornice.resource import resource
from logging import getLogger

LOGGER = getLogger(__name__)


@resource(
    name="esco:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType="esco",
    description="Tender ESCO contracts",
)
class ESCOContractResource(EUContractResource):
    serializer_class = ContractSerializer

    @json_view(
        content_type="application/json",
        permission="create_contract",
        validators=(
                validate_input_data(PostContract),
                validate_contract_operation_not_in_allowed_status,
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
                unless_admins(validate_contract_supplier()),
                validate_contract_operation_not_in_allowed_status,
                validate_contract_input_data(model=PatchContract, supplier_model=PatchContractSupplier),
                validate_patch_data_simple(Contract, item_name="contract"),
                validate_update_contract_only_for_active_lots,
                validate_update_contract_status_by_supplier,
                validate_update_contract_value_esco,
                validate_update_contract_status,
                validate_contract_update_with_accepted_complaint,
                validate_update_contract_value,
                validate_update_contract_value_net_required,
                validate_update_contract_value_with_award,
                validate_update_contract_value_amount,
        ),
    )
    def patch(self):
        return super().patch()

from openprocurement.api.utils import json_view
from openprocurement.tender.openua.procedure.views.contract import UAContractResource
from openprocurement.tender.openeu.procedure.views.contract import EUContractResource
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_patch_data,
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
from openprocurement.tender.openua.procedure.validation import validate_contract_update_with_accepted_complaint
from openprocurement.tender.openua.procedure.state.contract import OpenUAContractState
from openprocurement.tender.competitivedialogue.procedure.models.contract import (
    UAContract,
    UAPostContract,
    UAPatchContract,
    UAPatchContractSupplier,
    EUContract,
    EUPostContract,
    EUPatchContract,
    EUPatchContractSupplier,
)
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from cornice.resource import resource
from logging import getLogger

LOGGER = getLogger(__name__)


@resource(
    name="{}:Tender Contracts".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU contracts",
)
class CDStage2EUTenderContractResource(EUContractResource):
    @json_view(
        content_type="application/json",
        permission="create_contract",
        validators=(
                validate_input_data(EUPostContract),
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
                validate_contract_input_data(model=EUPatchContract, supplier_model=EUPatchContractSupplier),
                validate_patch_data(EUContract, item_name="contract"),
                validate_update_contract_only_for_active_lots,
                validate_update_contract_status_by_supplier,
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


@resource(
    name="{}:Tender Contracts".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA contracts",
)
class CDStage2UATenderContractResource(UAContractResource):
    state_class = OpenUAContractState

    @json_view(
        content_type="application/json",
        permission="create_contract",
        validators=(
            validate_input_data(UAPostContract),
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
                validate_contract_input_data(model=UAPatchContract, supplier_model=UAPatchContractSupplier),
                validate_patch_data(UAContract, item_name="contract"),
                validate_update_contract_only_for_active_lots,
                validate_update_contract_status_by_supplier,
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

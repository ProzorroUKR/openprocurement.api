from logging import getLogger

from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.procedure.models.stage2.contract import (
    EUContract,
    EUPatchContract,
    EUPatchContractSupplier,
    EUPostContract,
    UAContract,
    UAPatchContract,
    UAPatchContractSupplier,
    UAPostContract,
)
from openprocurement.tender.core.procedure.validation import (
    validate_contract_input_data,
    validate_contract_supplier,
    validate_forbid_contract_action_after_date,
)
from openprocurement.tender.openeu.procedure.views.contract import EUContractResource
from openprocurement.tender.openua.procedure.state.contract import OpenUAContractState
from openprocurement.tender.openua.procedure.views.contract import UAContractResource

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
            validate_forbid_contract_action_after_date("contract"),
            validate_input_data(EUPostContract),
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
            validate_contract_input_data(model=EUPatchContract, supplier_model=EUPatchContractSupplier),
            validate_patch_data_simple(EUContract, item_name="contract"),
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
            validate_forbid_contract_action_after_date("contract"),
            validate_input_data(UAPostContract),
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
            validate_contract_input_data(model=UAPatchContract, supplier_model=UAPatchContractSupplier),
            validate_patch_data_simple(UAContract, item_name="contract"),
        ),
    )
    def patch(self):
        return super().patch()

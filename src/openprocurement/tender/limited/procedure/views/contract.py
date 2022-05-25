from openprocurement.api.utils import json_view, get_now
from openprocurement.tender.core.procedure.views.contract import TenderContractResource
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data,
    validate_update_contract_value,
    validate_update_contract_value_with_award,
    validate_update_contract_value_amount,
    validate_update_contract_value_net_required,
)
from openprocurement.tender.limited.procedure.models.contract import (
    ReportingContract,
    ReportingPostContract,
    ReportingPatchContract,
    NegotiationContract,
    NegotiationPostContract,
    NegotiationPatchContract,
)
from openprocurement.tender.limited.procedure.state.contract import (
    LimitedReportingContractState,
    LimitedNegotiationContractState,
)
from openprocurement.tender.limited.procedure.validation import (
    validate_contract_update_in_cancelled,
    validate_contract_operation_not_in_active,
    validate_contract_items_count_modification,
    validate_update_contract_status,
)
from cornice.resource import resource
from logging import getLogger

LOGGER = getLogger(__name__)


@resource(
    name="reporting:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType="reporting",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class ReportingContractResource(TenderContractResource):
    state_class = LimitedReportingContractState

    @json_view(
        content_type="application/json",
        permission="create_contract",
        validators=(
            validate_input_data(ReportingPostContract),
            validate_contract_operation_not_in_active,
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
                validate_contract_operation_not_in_active,
                validate_input_data(ReportingPatchContract),
                validate_patch_data(ReportingContract, item_name="contract"),
                validate_contract_update_in_cancelled,
                validate_update_contract_status,
                validate_update_contract_value,
                validate_update_contract_value_net_required,
                validate_update_contract_value_with_award,
                validate_update_contract_value_amount,
                validate_contract_items_count_modification,
        ),
    )
    def patch(self):
        self.request.validated["contract"]["date"] = get_now()
        return super().patch()


@resource(
    name="negotiation:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType="negotiation",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class NegotiationContractResource(ReportingContractResource):
    state_class = LimitedNegotiationContractState

    @json_view(
        content_type="application/json",
        permission="create_contract",
        validators=(
                validate_input_data(NegotiationPostContract),
                validate_contract_operation_not_in_active,
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
                validate_contract_operation_not_in_active,
                validate_input_data(NegotiationPatchContract),
                validate_patch_data(NegotiationContract, item_name="contract"),
                validate_contract_update_in_cancelled,
                validate_update_contract_status,
                validate_update_contract_value,
                validate_update_contract_value_net_required,
                validate_update_contract_value_with_award,
                validate_update_contract_value_amount,
                validate_contract_items_count_modification,
        ),
    )
    def patch(self):
        return super().patch()


@resource(
    name="negotiation.quick:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    procurementMethodType="negotiation.quick",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    description="Tender contracts",
)
class NegotiationQuickContractResource(NegotiationContractResource):
    pass

from logging import getLogger

from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.validation import (
    validate_forbid_contract_action_after_date,
)
from openprocurement.tender.core.procedure.views.contract import TenderContractResource
from openprocurement.tender.limited.procedure.models.contract import (
    NegotiationContract,
    NegotiationPatchContract,
    NegotiationPostContract,
    ReportingContract,
    ReportingPatchContract,
    ReportingPostContract,
)
from openprocurement.tender.limited.procedure.state.contract import (
    LimitedNegotiationContractState,
    LimitedReportingContractState,
)

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
            validate_forbid_contract_action_after_date("contract"),
            validate_input_data(ReportingPostContract),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            validate_forbid_contract_action_after_date("contract"),
            unless_admins(validate_item_owner("tender")),
            validate_input_data(ReportingPatchContract),
            validate_patch_data_simple(ReportingContract, item_name="contract"),
        ),
    )
    def patch(self):
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
            validate_forbid_contract_action_after_date("contract"),
            validate_input_data(NegotiationPostContract),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            validate_forbid_contract_action_after_date("contract"),
            unless_admins(validate_item_owner("tender")),
            validate_input_data(NegotiationPatchContract),
            validate_patch_data_simple(NegotiationContract, item_name="contract"),
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

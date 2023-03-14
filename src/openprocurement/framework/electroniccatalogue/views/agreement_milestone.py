from openprocurement.api.utils import json_view
from openprocurement.framework.core.utils import contractresource
from openprocurement.framework.core.views.milestone import CoreContractMilestoneResource
from openprocurement.framework.core.validation import (
    validate_milestone_data,
    validate_patch_milestone_data,
    validate_agreement_operation_not_in_allowed_status,
    validate_contract_operation_not_in_allowed_status,
    validate_milestone_type,
    validate_contract_suspended,
    validate_patch_not_activation_milestone,
    validate_action_in_milestone_status,
    validate_patch_milestone_status,
)
from openprocurement.framework.electroniccatalogue.constants import ELECTRONIC_CATALOGUE_TYPE


@contractresource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Agreements Contracts Milestones",
    collection_path="/agreements/{agreement_id}/contracts/{contract_id}/milestones",
    path="/agreements/{agreement_id}/contracts/{contract_id}/milestones/{milestone_id}",
    agreementType=ELECTRONIC_CATALOGUE_TYPE,
    description="Agreements Contracts Milestones",
)
class ContractMilestoneResource(CoreContractMilestoneResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_milestone_data,
            validate_agreement_operation_not_in_allowed_status,
            validate_contract_operation_not_in_allowed_status,
            validate_contract_suspended,
            validate_milestone_type,
        ),
        permission="edit_agreement"
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_milestone_data,
            validate_agreement_operation_not_in_allowed_status,
            validate_contract_operation_not_in_allowed_status,
            validate_contract_suspended,
            validate_patch_not_activation_milestone,
            validate_action_in_milestone_status,
            validate_patch_milestone_status,
        ),
        permission="edit_agreement"
    )
    def patch(self):
        return super().patch()

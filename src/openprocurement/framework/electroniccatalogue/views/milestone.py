from openprocurement.api.utils import APIResource, json_view, upload_objects_documents
from openprocurement.framework.core.utils import apply_patch
from openprocurement.framework.core.validation import validate_milestone_data
from openprocurement.framework.electroniccatalogue.utils import contractresource, MILESTONE_CONTRACT_STATUSES
from openprocurement.framework.electroniccatalogue.validation import (
    validate_agreement_operation_not_in_allowed_status,
    validate_milestone_type,
    validate_contract_operation_not_in_allowed_status,
    validate_contract_banned,
)


@contractresource(
    name="electronicCatalogue:Agreements:Contracts:Milestones",
    collection_path="/agreements/{agreement_id}/contracts/{contract_id}/milestones",
    path="/agreements/{agreement_id}/contracts/{contract_id}/milestones/{milestone_id}",
    agreementType="electronicCatalogue",
    description="Agreement contract milestones resource",
)
class ContractMilestoneResource(APIResource):
    @json_view(permission="view_agreement")
    def collection_get(self):
        contract = self.context
        return {"data": [milestone.serialize("view") for milestone in contract.milestones]}

    @json_view(permission="view_agreement")
    def get(self):
        return {"data": self.request.validated["milestone"].serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
                validate_milestone_data,
                validate_agreement_operation_not_in_allowed_status,
                validate_contract_operation_not_in_allowed_status,
                validate_contract_banned,
                validate_milestone_type,
        ),
        permission="edit_agreement"
    )
    def collection_post(self):
        milestone = self.request.validated["milestone"]
        self.request.context.date = milestone.dateModified
        self.request.context.milestones.append(milestone)
        upload_objects_documents(
            self.request, milestone,
            route_kwargs={"milestone_id": milestone.id},
        )
        if apply_patch(
            self.request,
            obj_name="agreement",
            data={"status": MILESTONE_CONTRACT_STATUSES[milestone.type]},
            src=self.request.validated["contract"].to_primitive()
        ):
            self.request.response.status = 201
            return {"data": milestone.serialize("view")}

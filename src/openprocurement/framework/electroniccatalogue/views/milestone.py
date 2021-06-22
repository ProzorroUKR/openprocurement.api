from openprocurement.api.utils import APIResource, json_view, upload_objects_documents, context_unpack, get_now
from openprocurement.framework.core.utils import apply_patch, save_agreement
from openprocurement.framework.core.validation import validate_milestone_data, validate_patch_milestone_data
from openprocurement.framework.electroniccatalogue.utils import contractresource, MILESTONE_CONTRACT_STATUSES
from openprocurement.framework.electroniccatalogue.validation import (
    validate_agreement_operation_not_in_allowed_status,
    validate_contract_operation_not_in_allowed_status,
    validate_milestone_type,
    validate_contract_suspended,
    validate_patch_not_activation_milestone,
    validate_action_in_milestone_status,
    validate_patch_milestone_status,
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
                validate_contract_suspended,
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
        # PATCH now working only for milestone type `activation`
        milestone = self.request.context
        apply_patch(self.request, obj_name="agreement", save=False, src=milestone.to_primitive())

        if milestone.status == "met":
            contract = self.request.validated["contract"]
            contract.status = "terminated"

            for i in contract.milestones:
                if i.status == 'scheduled':
                    i.status = 'notMet'

        if save_agreement(self.request, additional_obj_names=("milestone",)):
            self.LOGGER.info(
                f"Updated milestone {milestone.id}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "milestone_patch"}),
            )

        return {"data": milestone.serialize("view")}

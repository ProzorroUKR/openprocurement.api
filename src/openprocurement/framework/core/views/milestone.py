from openprocurement.api.utils import (
    json_view,
    upload_objects_documents,
    context_unpack,
)
from openprocurement.api.views.base import BaseResource
from openprocurement.framework.core.utils import (
    apply_patch,
    save_agreement,
    MILESTONE_CONTRACT_STATUSES,
)
from openprocurement.framework.core.validation import validate_restricted_access


class CoreContractMilestoneResource(BaseResource):
    @json_view(
        validators=(
            validate_restricted_access("agreement")
        ),
        permission="view_agreement",
    )
    def collection_get(self):
        contract = self.context
        return {"data": [milestone.serialize("view") for milestone in contract.milestones]}

    @json_view(
        validators=(
            validate_restricted_access("agreement")
        ),
        permission="view_agreement",
    )
    def get(self):
        return {"data": self.request.validated["milestone"].serialize("view")}

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

    def patch(self):
        milestone = self.request.context
        apply_patch(
            self.request,
            obj_name="agreement",
            save=False,
            src=milestone.to_primitive(),
        )

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

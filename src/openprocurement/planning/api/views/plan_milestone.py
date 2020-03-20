# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import (
    context_unpack,
    get_now,
    generate_id,
    json_view,
    set_ownership,
    APIResourceListing,
    raise_operation_error,
)
from openprocurement.planning.api.models import Milestone
from openprocurement.planning.api.utils import (
    generate_plan_id,
    save_plan,
    plan_serialize,
    apply_patch,
    opresource,
    APIResource
)
from openprocurement.planning.api.validation import (
    validate_plan_not_terminated,
    validate_milestone_data,
    validate_patch_milestone_data,
    validate_milestone_author,
    validate_milestone_status_scheduled,
)
LOGGER = getLogger(__name__)


@opresource(
    name='Plan Milestones',
    collection_path="/plans/{plan_id}/milestones",
    path='/plans/{plan_id}/milestones/{milestone_id}',
    description="Plan milestone view",
)
class PlanMilestoneResource(APIResource):

    @json_view()
    def get(self):
        return {'data': self.request.validated['milestone'].serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_plan_not_terminated,
            validate_milestone_data,
            validate_milestone_author,
            validate_milestone_status_scheduled,
        ),
        permission="post_plan_milestone",
    )
    def collection_post(self):
        plan = self.request.validated["plan"]
        milestone = self.request.validated["milestone"]
        access = set_ownership(milestone, self.request)
        plan.milestones.append(milestone)
        plan.dateModified = milestone.dateModified
        plan.modified = False
        if save_plan(self.request):
            self.LOGGER.info(
                "Created plan milestone {}".format(milestone.id),
                extra=context_unpack(self.request,
                                     {"MESSAGE_ID": "tender_milestone_post"},
                                     {"milestone_id": milestone.id, "plan_id": plan.id}),
            )
            self.request.response.status = 201
            milestone_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers["Location"] = self.request.current_route_url(
                _route_name=milestone_route, milestone_id=milestone.id, _query={}
            )
            return {"data": milestone.serialize("view"), "access": access}

    @json_view(
        content_type="application/json",
        validators=(
            validate_plan_not_terminated,
            validate_patch_milestone_data,
        ),
        permission="update_milestone",
    )
    def patch(self):
        plan = self.request.validated['plan']
        milestone = self.request.context
        status = milestone.status
        prev_due_date = milestone.dueDate
        description = milestone.description

        if apply_patch(self.request, src=self.request.context.serialize(), save=False):
            plan.dateModified = milestone.dateModified = get_now()
            plan.modified = False
            if status != milestone.status:  # Allowed status changes: scheduled -> met/notMet
                if (
                        status == Milestone.STATUS_SCHEDULED
                        and milestone.status in (Milestone.STATUS_MET, Milestone.STATUS_NOT_MET)
                ):
                    if milestone.status == Milestone.STATUS_MET:
                        milestone.dateMet = milestone.dateModified
                else:
                    raise_operation_error(
                        self.request,
                        "Can't update milestone status from '{}' to '{}'".format(status, milestone.status)
                    )

            if prev_due_date != milestone.dueDate and status != Milestone.STATUS_SCHEDULED:
                raise_operation_error(
                    self.request,
                    "Can't update dueDate at '{}' milestone status".format(status)
                )

            if (
                description != milestone.description and
                status not in (Milestone.STATUS_SCHEDULED, Milestone.STATUS_MET)
            ):
                raise_operation_error(
                    self.request,
                    "Can't update description at '{}' milestone status".format(status)
                )

            save_plan(self.request)
            self.LOGGER.info('Updated plan milestone {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'plan_milestone_patch'}))

        return {'data': self.request.context.serialize("view")}

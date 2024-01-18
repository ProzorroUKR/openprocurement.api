# -*- coding: utf-8 -*-
from logging import getLogger

from cornice.resource import resource

from openprocurement.api.utils import json_view, update_logging_context, context_unpack
from openprocurement.tender.core.procedure.utils import set_ownership
from openprocurement.api.procedure.utils import get_items, set_item
from openprocurement.api.procedure.validation import (
    validate_patch_data_simple,
    validate_input_data,
    validate_data_documents, validate_item_owner,
)
from openprocurement.planning.api.procedure.models.milestone import PostMilestone, PatchMilestone, Milestone
from openprocurement.planning.api.procedure.serializers.milestone import MilestoneSerializer
from openprocurement.planning.api.procedure.state.plan_milestone import MilestoneState
from openprocurement.planning.api.procedure.utils import save_plan
from openprocurement.planning.api.procedure.views.base import PlanBaseResource

LOGGER = getLogger(__name__)


def resolve_milestone(request):
    match_dict = request.matchdict
    if match_dict.get("milestone_id"):
        milestone_id = match_dict["milestone_id"]
        milestones = get_items(request, request.validated["plan"], "milestones", milestone_id)
        request.validated["milestone"] = milestones[0]


@resource(
    name='Plan Milestones',
    collection_path="/plans/{plan_id}/milestones",
    path='/plans/{plan_id}/milestones/{milestone_id}',
)
class PlanMilestoneResource(PlanBaseResource):
    serializer_class = MilestoneSerializer
    state_class = MilestoneState

    def __init__(self, request, context=None):
        super().__init__(request, context)
        resolve_milestone(request)

    @json_view(permission="view_plan")
    def get(self):
        plan = self.request.validated["plan"]
        return {"data": self.serializer_class(plan).data}

    @json_view(
        content_type="application/json",
        permission="post_plan_milestone",
        validators=(
            validate_input_data(PostMilestone),
            validate_data_documents(route_key="milestone_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        update_logging_context(self.request, {"milestone_id": "__new__"})

        plan = self.request.validated["plan"]
        milestone = self.request.validated["data"]
        access = set_ownership(milestone, self.request, with_transfer=False)

        self.state.milestone_on_post(milestone)

        if "milestones" not in plan:
            plan["milestones"] = []
        plan["milestones"].append(milestone)

        self.state.on_patch(self.request.validated["plan_src"], plan)

        if save_plan(self.request):
            LOGGER.info(
                "Created plan milestone {}".format(milestone["id"]),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "plan_milestone_create"},
                    {"milestone_id": milestone["id"]},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "Plan Milestones",
                plan_id=plan["_id"],
                milestone_id=milestone["id"],
            )
            return {"data": self.serializer_class(milestone).data, "access": access}

    @json_view(
        content_type="application/json",
        permission="update_milestone",
        validators=(
            validate_item_owner("milestone"),
            validate_input_data(PatchMilestone, none_means_remove=True),
            validate_patch_data_simple(Milestone, item_name="milestone"),
        ),
    )
    def patch(self):
        plan = self.request.validated["plan"]
        milestone = self.request.validated["milestone"]
        updated_milestone = self.request.validated["data"]
        if updated_milestone:
            self.state.milestone_on_patch(milestone, updated_milestone)
            self.state.on_patch(self.request.validated["plan_src"], plan)
            set_item(plan, "milestones", milestone["id"], updated_milestone)
            if save_plan(self.request):
                self.LOGGER.info(
                    f"Updated plan milestone {milestone['id']}",
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "plan_milestone_patch"},
                        {"milestone_id": milestone["id"]},
                    ),
                )
            milestone = updated_milestone
        return {"data": self.serializer_class(milestone).data}

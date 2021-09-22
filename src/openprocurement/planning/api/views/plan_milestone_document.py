# -*- coding: utf-8 -*-
from openprocurement.planning.api.utils import opresource
from openprocurement.api.utils import get_now, json_view
from openprocurement.planning.api.validation import validate_plan_not_terminated
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.planning.api.views.plan_document import PlansDocumentResource


@opresource(
    name="Plan Milestone Documents",
    collection_path="/plans/{plan_id}/milestones/{milestone_id}/documents",
    path="/plans/{plan_id}/milestones/{milestone_id}/documents/{document_id}",
    description="Plan milestone related files",
)
class PlanMilestoneDocumentResource(PlansDocumentResource):
    context_name = "plan_milestone"

    def update_modified(self):
        plan = self.request.validated["plan"]
        milestone = self.request.validated["milestone"]
        plan.dateModified = milestone.dateModified = get_now()
        plan.is_modified = False

    @json_view(
        permission="update_milestone",
        validators=(validate_file_upload, validate_plan_not_terminated)
    )
    def collection_post(self):
        self.update_modified()
        return super(PlanMilestoneDocumentResource, self).collection_post()

    @json_view(
        permission="update_milestone",
        validators=(validate_file_update, validate_plan_not_terminated)
    )
    def put(self):
        self.update_modified()
        return super(PlanMilestoneDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="update_milestone",
        validators=(validate_patch_document_data, validate_plan_not_terminated),
    )
    def patch(self):
        self.update_modified()
        return super(PlanMilestoneDocumentResource, self).patch()

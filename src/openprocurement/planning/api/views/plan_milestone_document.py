# -*- coding: utf-8 -*-
from openprocurement.planning.api.utils import opresource
from openprocurement.api.utils import get_now, context_unpack, json_view
from openprocurement.planning.api.validation import validate_plan_not_terminated
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data
from openprocurement.planning.api.views.plan_document import PlansDocumentResource


@opresource(
    name="Plan Milestone Documents",
    collection_path="/plans/{plan_id}/milestones/{milestone_id}/documents",
    path="/plans/{plan_id}/milestones/{milestone_id}/documents/{document_id}",
    description="Plan milestone related files",
)
class PlanMilestoneDocumentResource(PlansDocumentResource):

    def update_modified_dates(self):
        plan = self.request.validated["plan"]
        milestone = self.request.validated["milestone"]
        plan.dateModified = milestone.dateModified = get_now()
        plan.modified = False

    @json_view(
        permission="update_milestone",
        validators=(validate_file_upload, validate_plan_not_terminated)
    )
    def collection_post(self):
        self.update_modified_dates()
        return super(PlanMilestoneDocumentResource, self).collection_post()

    @json_view(
        permission="update_milestone",
        validators=(validate_file_update, validate_plan_not_terminated)
    )
    def put(self):
        self.update_modified_dates()
        return super(PlanMilestoneDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="update_milestone",
        validators=(validate_patch_document_data, validate_plan_not_terminated),
    )
    def patch(self):
        self.update_modified_dates()
        return super(PlanMilestoneDocumentResource, self).patch()

    def _post_document_log(self, document):
        self.LOGGER.info(
            "Created plan milestone document {}".format(document.id),
            extra=context_unpack(
                self.request,
                {"MESSAGE_ID": "plan_milestone_document_create"},
                {"document_id": document.id}
            ),
        )

    def _put_document_log(self):
        self.LOGGER.info(
            "Updated plan milestone document {}".format(self.request.context.id),
            extra=context_unpack(self.request,
                                 {"MESSAGE_ID": "plan_milestone_document_put"}),
        )

    def _patch_document_log(self):
        self.LOGGER.info(
            "Updated plan milestone document {}".format(self.request.context.id),
            extra=context_unpack(self.request,
                                 {"MESSAGE_ID": "plan_milestone_document_patch"}),
        )

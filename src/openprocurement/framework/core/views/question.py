from openprocurement.api.context import get_now
from openprocurement.api.views.base import BaseResource
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    update_logging_context,
)
from openprocurement.framework.core.utils import apply_patch, save_framework
from openprocurement.framework.core.validation import (
    validate_item_owner,
    validate_post_question_data,
    validate_patch_question_data,
    validate_framework_question_operation_not_in_allowed_status,
    validate_framework_question_operation_not_in_enquiry_period,
)


class CoreQuestionResource(BaseResource):

    @json_view(permission="view_framework")
    def collection_get(self):
        """
        List questions
        """
        framework = self.context
        return {"data": [question.serialize("view") for question in framework.questions] if framework.questions else []}

    @json_view(permission="view_framework")
    def get(self):
        """
        Retrieving the question
        """
        data = self.request.validated["question"].serialize("view")
        return {"data": data}

    @json_view(
        content_type="application/json",
        permission="create_question",
        validators=(
            validate_post_question_data,
            validate_framework_question_operation_not_in_allowed_status,
            validate_framework_question_operation_not_in_enquiry_period,
        ),
    )
    def collection_post(self):
        update_logging_context(self.request, {"question_id": "__new__"})
        framework = self.request.validated["framework"]
        question = self.request.validated["question"]
        self.request.context.questions.append(question)

        if save_framework(self.request):
            self.LOGGER.info(
                f"Created framework question {question['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "framework_question_create"},
                    {"question_id": question["id"]},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                f"{framework.frameworkType}:Framework Questions",
                framework_id=framework["_id"],
                question_id=question["id"]
            )
            return {"data": question.serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("framework"),
            validate_patch_question_data,
            validate_framework_question_operation_not_in_allowed_status,
            validate_framework_question_operation_not_in_enquiry_period,
        ),
        permission="edit_question",
    )
    def patch(self):
        """
        Patch a question
        """
        question = self.request.context
        question.dateAnswered = get_now().isoformat()
        if apply_patch(self.request, obj_name="framework", src=question.to_primitive()):
            self.LOGGER.info(
                f"Updated framework question {question['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "framework_question_patch"},
                ),
            )
            return {"data": question.serialize("view")}

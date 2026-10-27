from openprocurement.api.procedure.utils import get_items, set_item
from openprocurement.api.utils import context_unpack, json_view, update_logging_context
from openprocurement.framework.core.procedure.serializers.question import (
    QuestionSerializer,
)
from openprocurement.framework.core.procedure.state.question import QuestionState
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource


def resolve_question(request):
    match_dict = request.matchdict
    if match_dict.get("question_id"):
        question_id = match_dict["question_id"]
        question = get_items(request, request.validated["framework"], "questions", question_id)
        request.validated["question"] = question[0]


class CoreQuestionResource(FrameworkBaseResource):
    serializer_class = QuestionSerializer
    state_class = QuestionState

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_question(request)

    @json_view(permission="view_framework")
    def collection_get(self):
        """
        List questions
        """
        framework = self.request.validated["framework"]
        data = tuple(
            self.serializer_class(question, framework=framework).data for question in framework.get("questions", [])
        )
        return {"data": data}

    @json_view(permission="view_framework")
    def get(self):
        """
        Retrieving the question
        """
        framework = self.request.validated["framework"]
        question = self.request.validated["question"]
        data = self.serializer_class(question, framework=framework).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        permission="create_question",
    )
    def collection_post(self):
        self.state.validate_question_post_request()
        update_logging_context(self.request, {"question_id": "__new__"})

        framework = self.request.validated["framework"]
        question = self.request.validated["data"]

        if "questions" not in framework:
            framework["questions"] = []
        framework["questions"].append(question)
        self.state.validate_question_on_post()

        if save_object(self.request, "framework"):
            self.LOGGER.info(
                f"Created framework question {question['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "framework_question_create"},
                    {"framework_id": framework["_id"], "question_id": question["id"]},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                f"{framework['frameworkType']}:Framework Questions",
                framework_id=framework["_id"],
                question_id=question["id"],
            )
            return {"data": self.serializer_class(question, framework=framework).data}

    @json_view(
        content_type="application/json",
        permission="edit_question",
    )
    def patch(self):
        """
        Patch a question
        """
        self.state.validate_question_patch_request()
        updated = self.request.validated["data"]
        if updated:
            framework = self.request.validated["framework"]
            question = self.request.validated["question"]
            set_item(framework, "questions", question["id"], updated)
            self.state.on_patch(question, updated)
            if save_object(self.request, "framework"):
                self.LOGGER.info(
                    f"Updated framework question {question['id']}",
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "framework_question_patch"},
                    ),
                )
                return {"data": self.serializer_class(updated, framework=framework).data}

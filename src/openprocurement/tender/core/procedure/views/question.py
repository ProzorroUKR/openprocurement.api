from pyramid.security import Allow, Everyone, ALL_PERMISSIONS
from openprocurement.api.utils import json_view, update_logging_context
from openprocurement.api.utils import context_unpack
from openprocurement.tender.core.procedure.state.question import TenderQuestionState
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.serializers.question import QuestionSerializer
from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.tender.core.procedure.utils import (
    save_tender,
    set_item,
)
from openprocurement.tender.core.procedure.models.question import (
    PostQuestion,
    PatchQuestion,
    Question,
)
from openprocurement.tender.core.procedure.validation import (
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
    validate_operation_with_lot_cancellation_in_pending, validate_accreditation_level,
)


def resolve_question(request):
    match_dict = request.matchdict
    if match_dict.get("question_id"):
        question_id = match_dict["question_id"]
        question = get_items(request, request.validated["tender"], "questions", question_id)
        request.validated["question"] = question[0]


class TenderQuestionResource(TenderBaseResource):
    # model_class = Question
    serializer_class = QuestionSerializer
    state_class = TenderQuestionState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_question"),
            (Allow, "g:brokers", "edit_question"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_question(request)

    @json_view(permission="view_tender")
    def collection_get(self):
        """List questions
        """
        tender = self.request.validated["tender"]
        data = tuple(self.serializer_class(question).data for question in tender.get("questions", []))
        return {"data": data}

    @json_view(permission="view_tender")
    def get(self):
        """Retrieving the question
        """
        data = self.serializer_class(self.request.validated["question"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        permission="create_question",
        validators=(
            validate_input_data(PostQuestion),
        ),
    )
    def collection_post(self):
        update_logging_context(self.request, {"question_id": "__new__"})

        tender = self.request.validated["tender"]
        question = self.request.validated["data"]

        self.state.question_on_post(question)

        if "questions" not in tender:
            tender["questions"] = []
        tender["questions"].append(question)

        self.state.always(tender)

        if save_tender(self.request):
            self.LOGGER.info(
                f"Created tender question {question['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_question_create"},
                    {"question_id": question["id"]},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Questions".format(tender["procurementMethodType"]),
                tender_id=tender["_id"],
                question_id=question["id"]
            )
            return {"data": self.serializer_class(question).data}

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PatchQuestion),
            validate_patch_data_simple(Question, item_name="question"),
            validate_operation_with_lot_cancellation_in_pending("question"),
        ),
        permission="edit_question",
    )
    def patch(self):
        """Patch a question
        """
        updated = self.request.validated["data"]
        if updated:
            question = self.request.validated["question"]
            set_item(self.request.validated["tender"], "questions", question["id"], updated)
            self.state.question_on_patch(question, updated)
            self.state.always(self.request.validated["tender"])
            if save_tender(self.request):
                self.LOGGER.info(
                    "Updated tender question {}".format(question["id"]),
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "tender_question_patch"},
                    ),
                )
                return {"data": self.serializer_class(updated).data}

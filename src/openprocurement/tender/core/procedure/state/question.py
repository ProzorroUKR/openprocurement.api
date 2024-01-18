from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.context import get_now
from openprocurement.api.procedure.validation import validate_accreditation_level


class TenderQuestionStateMixin:
    question_create_accreditations: set = None  # formerly tender.edit_accreditations

    def question_on_post(self, question):
        self.validate_question_accreditation_level()
        self.validate_question_on_post(question)

    def question_on_patch(self, before, question):
        self.validate_question_on_patch(before, question)
        question["dateAnswered"] = get_now().isoformat()

    def validate_question_on_post(self, question):
        self.validate_question_operation(get_tender(), question)

    def validate_question_on_patch(self, before, question):
        self.validate_question_operation(get_tender(), question)

    def validate_question_accreditation_level(self):
        if not self.question_create_accreditations:
            raise AttributeError("Question create accreditations are not configured")
        validate_accreditation_level(
            levels=self.question_create_accreditations,
            item="question",
            operation="creation",
        )(get_request())

    def validate_question_operation(self, tender, question):
        items_dict = {item["id"]: item.get("relatedLot") for item in tender.get("items", [])}
        if any(
            lot["status"] != "active"
            for lot in tender.get("lots", [])
            if question["questionOf"] == "lot"
            and lot["id"] == question["relatedItem"]
            or question["questionOf"] == "item"
            and lot["id"] == items_dict[question["relatedItem"]]
        ):
            raise_operation_error(
                get_request(),
                "Can add/update question only in active lot status",
            )


class TenderQuestionState(TenderQuestionStateMixin, TenderState):
    pass

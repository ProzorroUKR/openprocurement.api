from typing import Callable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.validation import validate_accreditation_level
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import get_supplier_contract


class TenderQuestionStateMixin:
    always: Callable  # method from TenderState

    question_create_accreditations: set = None  # formerly tender.edit_accreditations

    def question_on_post(self, question):
        self.validate_question_accreditation_level()
        self.validate_question_on_post(question)

        self.always(get_tender())

    def question_on_patch(self, before, question):
        self.validate_question_on_patch(before, question)
        question["dateAnswered"] = get_request_now().isoformat()

        self.always(get_tender())

    def validate_question_on_post(self, question):
        tender = get_tender()
        self.validate_question_add(tender)
        self.validate_question_operation(tender, question)
        self.validate_question_author(question)

    def validate_question_on_patch(self, before, question):
        tender = get_tender()
        self.validate_question_update(tender)
        self.validate_question_operation(tender, question)

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

    def validate_question_add(self, tender):
        now = get_request_now().isoformat()
        enquiry_period = tender["enquiryPeriod"]

        if not enquiry_period["startDate"] <= now <= enquiry_period["endDate"]:
            raise_operation_error(
                get_request(),
                "Can add question only in enquiryPeriod",
            )

    def validate_question_update(self, tender):
        now = get_request_now().isoformat()
        enquiry_period = tender["enquiryPeriod"]

        if tender["status"] not in ("active.enquiries", "active.tendering"):
            raise_operation_error(
                get_request(),
                "Can't update question in current ({}) tender status".format(tender["status"]),
            )

        if "clarificationsUntil" in enquiry_period and now > enquiry_period["clarificationsUntil"]:
            raise_operation_error(
                get_request(),
                "Can update question only before enquiryPeriod.clarificationsUntil",
            )

    def validate_question_author(self, question):
        tender = get_tender()
        if not tender["config"]["hasPreSelectionAgreement"]:
            return

        agreement_id = tender["agreements"][0]["id"]
        agreement = get_request().registry.mongodb.agreements.get(agreement_id)
        supplier_contract = get_supplier_contract(
            agreement["contracts"],
            [question["author"]],
        )
        if not supplier_contract:
            raise_operation_error(get_request(), "Forbidden to add question for non-qualified suppliers")


class TenderQuestionState(TenderQuestionStateMixin, TenderState):
    pass

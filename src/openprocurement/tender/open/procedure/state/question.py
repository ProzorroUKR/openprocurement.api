from openprocurement.api.auth import ACCR_4
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.question import (
    TenderQuestionStateMixin,
)
from openprocurement.tender.core.procedure.utils import get_supplier_contract
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenTenderQuestionStateMixin(TenderQuestionStateMixin):
    def validate_question_on_post(self, question):
        super().validate_question_on_post(question)
        self.validate_question_author(question)

    def validate_question_operation(self, tender, question):
        super().validate_question_operation(tender, question)
        if tender["status"] != "active.tendering":
            raise_operation_error(
                get_request(),
                "Can't update question in current ({}) tender status".format(tender["status"]),
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


class OpenTenderQuestionState(OpenTenderQuestionStateMixin, OpenTenderState):
    question_create_accreditations = (ACCR_4,)

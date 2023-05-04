from openprocurement.api.auth import ACCR_2
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState
from openprocurement.tender.core.procedure.context import get_request, get_tender
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin


class BelowThresholdTenderQuestionStateMixin(TenderQuestionStateMixin):
    def validate_question_on_post(self, question):
        self.validate_question_add(get_tender())
        super().validate_question_on_post(question)

    def validate_question_on_patch(self, before, question):
        self.validate_question_update(get_tender())
        super().validate_question_on_patch(before, question)

    def validate_question_add(self, tender):
        now = get_now().isoformat()
        period = tender["enquiryPeriod"]
        if (
            tender["status"] != "active.enquiries"
            or period.get("startDate") and now < period["startDate"] or now > period["endDate"]
        ):
            raise_operation_error(
                get_request(),
                "Can add question only in enquiryPeriod",
            )

    def validate_question_update(self, tender):
        if tender["status"] not in ("active.enquiries", "active.tendering"):
            raise_operation_error(
                get_request(),
                "Can't update question in current ({}) tender status".format(tender["status"]),
            )


class BelowThresholdTenderQuestionState(BelowThresholdTenderQuestionStateMixin, BelowThresholdTenderState):
    create_accreditations = (ACCR_2,)

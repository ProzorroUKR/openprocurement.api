# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, json_view, context_unpack, APIResource, raise_operation_error
from openprocurement.tender.core.validation import (
    validate_question_data,
    validate_patch_question_data,
    validate_operation_with_lot_cancellation_in_pending,
)

from openprocurement.tender.core.utils import save_tender, optendersresource, apply_patch


@optendersresource(
    name="belowThreshold:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType="belowThreshold",
    description="Tender questions",
)
class TenderQuestionResource(APIResource):
    def validate_question(self, operation):
        """ TODO move validators
        This class is inherited in openua package, but validate_question function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        tender = self.request.validated["tender"]
        if operation == "add" and (
            tender.status != "active.enquiries"
            or tender.enquiryPeriod.startDate
            and get_now() < tender.enquiryPeriod.startDate
            or get_now() > tender.enquiryPeriod.endDate
        ):
            raise_operation_error(self.request, "Can add question only in enquiryPeriod")
        if operation == "update" and tender.status != "active.enquiries":
            raise_operation_error(
                self.request, "Can't update question in current ({}) tender status".format(tender.status)
            )
        question = self.request.validated["question"]
        items_dict = {i.id: i.relatedLot for i in tender.items}
        if any(
            [
                i.status != "active"
                for i in tender.lots
                if question.questionOf == "lot"
                and i.id == question.relatedItem
                or question.questionOf == "item"
                and i.id == items_dict[question.relatedItem]
            ]
        ):
            raise_operation_error(self.request, "Can {} question only in active lot status".format(operation))
        return True

    @json_view(content_type="application/json", validators=(validate_question_data,), permission="create_question")
    def collection_post(self):
        """Post a question
        """
        if not self.validate_question("add"):
            return
        question = self.request.validated["question"]
        self.request.context.questions.append(question)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender question {}".format(question.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_question_create"}, {"question_id": question.id}
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Questions".format(self.request.context.procurementMethodType),
                tender_id=self.request.context.id,
                question_id=question.id,
            )
            return {"data": question.serialize("view")}

    @json_view(permission="view_tender")
    def collection_get(self):
        """List questions
        """
        return {
            "data": [
                i.serialize(self.request.validated["tender"].status) for i in self.request.validated["tender"].questions
            ]
        }

    @json_view(permission="view_tender")
    def get(self):
        """Retrieving the question
        """
        return {"data": self.request.validated["question"].serialize(self.request.validated["tender"].status)}

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_patch_question_data,
            validate_operation_with_lot_cancellation_in_pending("question"),
        )
    )
    def patch(self):
        """Post an Answer
        """
        if not self.validate_question("update"):
            return
        self.context.dateAnswered = get_now()
        if apply_patch(self.request, src=self.request.context.serialize()):
            self.LOGGER.info(
                "Updated tender question {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_question_patch"}),
            )
            return {"data": self.request.context.serialize(self.request.validated["tender_status"])}

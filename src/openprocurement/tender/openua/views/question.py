# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, raise_operation_error
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.question import TenderQuestionResource


@optendersresource(
    name="aboveThresholdUA:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender questions",
)
class TenderUaQuestionResource(TenderQuestionResource):
    def validate_question(self, operation):
        """ TODO move validators
        This class is inherited from below package, but validate_question function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        tender = self.request.validated["tender"]
        now = get_now()

        if operation == "add" and (now < tender.enquiryPeriod.startDate or now > tender.enquiryPeriod.endDate):
            raise_operation_error(self.request, "Can add question only in enquiryPeriod")
        if operation == "update" and tender.status != "active.tendering":
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
        if operation == "update" and now > tender.enquiryPeriod.clarificationsUntil:
            raise_operation_error(self.request, "Can update question only before enquiryPeriod.clarificationsUntil")
        return True

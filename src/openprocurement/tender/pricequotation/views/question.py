# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.utils import get_now, json_view, context_unpack, APIResource, raise_operation_error
from openprocurement.tender.belowthreshold.views.question\
    import TenderQuestionResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.validation import\
    validate_question_data, validate_patch_question_data
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Questions".format(PMT),
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType=PMT,
    description="Tender questions",
)
class PQTenderQuestionResource(TenderQuestionResource):

    def validate_question(self, operation):
        """ TODO move validators
        This class is inherited in openua package, but validate_question function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        tender = self.request.validated["tender"]
        if operation == "add" and (
            tender.status != "active.tendering"
            or tender.tenderPeriod.startDate
            and get_now() < tender.tenderPeriod.startDate
            or get_now() > tender.tenderPeriod.endDate
        ):
            raise_operation_error(self.request, "Can add question only in tenderPeriod")
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
        return True

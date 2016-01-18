# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.models import get_now
from openprocurement.api.utils import (
    apply_patch,
    save_tender,
    opresource,
    json_view,
    context_unpack,
)
from openprocurement.api.validation import (
    validate_question_data,
    validate_patch_question_data,
)

from openprocurement.api.views.question import TenderQuestionResource

LOGGER = getLogger(__name__)

# TODO: Remove COPY&PASTE (diff in tender.status not in ['active.tendering'])

@opresource(name='Tender UA Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender questions")
class TenderUaQuestionResource(TenderQuestionResource):

    @json_view(content_type="application/json", validators=(validate_question_data,), permission='create_question')
    def collection_post(self):
        """Post a question
        """
        tender = self.request.validated['tender']
        now = get_now()
        if  now< tender.enquiryPeriod.startDate or now > tender.enquiryPeriod.endDate:
            self.request.errors.add('body', 'data', 'Can add question only in enquiryPeriod')
            self.request.errors.status = 403
            return
        question = self.request.validated['question']
        if any([i.status != 'active' for i in tender.lots if i.id == question.relatedItem]):
            self.request.errors.add('body', 'data', 'Can add question only in active lot status')
            self.request.errors.status = 403
            return
        tender.questions.append(question)
        if save_tender(self.request):
            LOGGER.info('Created tender question {}'.format(question.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_question_create'}, {'question_id': question.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('Tender Questions', tender_id=tender.id, question_id=question.id)
            return {'data': question.serialize("view")}

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_patch_question_data,))
    def patch(self):
        """Post an Answer
        """
        tender = self.request.validated['tender']
        if tender.status != 'active.tendering':
            self.request.errors.add('body', 'data', 'Can\'t update question in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in tender.lots if i.id == self.request.context.relatedItem]):
            self.request.errors.add('body', 'data', 'Can update question only in active lot status')
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            LOGGER.info('Updated tender question {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_question_patch'}))
            return {'data': self.request.context.serialize(tender.status)}

# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.question import TenderUaQuestionResource as TenderQuestionResource


@opresource(name='Tender UA.defense Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender questions")
class TenderUaQuestionResource(TenderQuestionResource):
    """ """

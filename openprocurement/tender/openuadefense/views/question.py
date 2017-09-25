# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.question import (
    TenderUaQuestionResource as TenderQuestionResource
)


@optendersresource(name='aboveThresholdUA.defense:Tender Questions',
                   collection_path='/tenders/{tender_id}/questions',
                   path='/tenders/{tender_id}/questions/{question_id}',
                   procurementMethodType='aboveThresholdUA.defense',
                   description="Tender questions")
class TenderUaQuestionResource(TenderQuestionResource):
    """ """

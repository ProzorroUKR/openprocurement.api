# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.question import TenderUaQuestionResource
from openprocurement.tender.openeu.views.question import TenderQuestionResource as TenderEUQuestionResource


@opresource(name='Tender ESCO UA Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType='esco.UA',
            description="Tender ESCO UA questions")
class TenderESCOUAQuestionResource(TenderUaQuestionResource):
    """ Tender ESCO UA Question Resource """


@opresource(name='Tender ESCO EU Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU questions")
class TenderESCOEUQuestionResource(TenderEUQuestionResource):
    """ Tender ESCO EU Question Resource """

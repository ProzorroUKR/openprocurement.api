# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.question import TenderQuestionResource as TenderEUQuestionResource


@optendersresource(name='Tender ESCO EU Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU questions")
class TenderESCOEUQuestionResource(TenderEUQuestionResource):
    """ Tender ESCO EU Question Resource """

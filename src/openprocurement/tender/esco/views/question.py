# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.question import TenderQuestionResource as TenderEUQuestionResource


# @optendersresource(
#     name="esco:Tender Questions",
#     collection_path="/tenders/{tender_id}/questions",
#     path="/tenders/{tender_id}/questions/{question_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO questions",
# )
class TenderESCOQuestionResource(TenderEUQuestionResource):
    """ Tender ESCO Question Resource """

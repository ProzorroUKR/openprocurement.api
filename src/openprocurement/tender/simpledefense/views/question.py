# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.question import TenderUaQuestionResource as TenderQuestionResource


# @optendersresource(
#     name="simple.defense:Tender Questions",
#     collection_path="/tenders/{tender_id}/questions",
#     path="/tenders/{tender_id}/questions/{question_id}",
#     procurementMethodType="simple.defense",
#     description="Tender questions",
# )
class TenderSimpleDefQuestionResource(TenderQuestionResource):
    """ """

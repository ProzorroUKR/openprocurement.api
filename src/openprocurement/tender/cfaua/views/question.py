# -*- coding: utf-8 -*-
from openprocurement.tender.openua.views.question import TenderUaQuestionResource as BaseResource
from openprocurement.tender.core.utils import optendersresource


# @optendersresource(
#     name="closeFrameworkAgreementUA:Tender Questions",
#     collection_path="/tenders/{tender_id}/questions",
#     path="/tenders/{tender_id}/questions/{question_id}",
#     procurementMethodType="closeFrameworkAgreementUA",
#     description="Tender questions",
# )
class TenderQuestionResource(BaseResource):
    """ TenderEU Questions """

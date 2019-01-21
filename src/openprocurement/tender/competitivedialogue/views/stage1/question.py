# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.question import (
    TenderUaQuestionResource as BaseResource
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE, CD_UA_TYPE
)


@optendersresource(name='{}:Tender Questions'.format(CD_EU_TYPE),
                   collection_path='/tenders/{tender_id}/questions',
                   path='/tenders/{tender_id}/questions/{question_id}',
                   procurementMethodType=CD_EU_TYPE,
                   description="competitiveDialogue UE questions")
class CompetitiveDialogueEUQuestionResource(BaseResource):
    """ TenderEU Questions """


@optendersresource(name='{}:Tender Questions'.format(CD_UA_TYPE),
                   collection_path='/tenders/{tender_id}/questions',
                   path='/tenders/{tender_id}/questions/{question_id}',
                   procurementMethodType=CD_UA_TYPE,
                   description="competitiveDialogue UA questions")
class CompetitiveDialogueUAQuestionResource(BaseResource):
    """ TenderUA Questions """

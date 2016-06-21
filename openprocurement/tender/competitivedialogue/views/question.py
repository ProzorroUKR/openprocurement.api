# -*- coding: utf-8 -*-
from openprocurement.tender.openua.views.question import TenderUaQuestionResource as BaseResource
from openprocurement.api.utils import opresource
from openprocurement.tender.competitivedialogue.models import CD_EU_TYPE, CD_UA_TYPE


@opresource(name='Competitive Dialogue EU Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType=CD_EU_TYPE,
            description="competitiveDialogue UE questions")
class CompetitiveDialogueEUQuestionResource(BaseResource):
    """ TenderEU Questions """


@opresource(name='Competitive Dialogue UA Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType=CD_UA_TYPE,
            description="competitiveDialogue UA questions")
class CompetitiveDialogueUAQuestionResource(BaseResource):
    """ TenderUA Questions """

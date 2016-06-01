# -*- coding: utf-8 -*-
from openprocurement.tender.openua.views.question import TenderUaQuestionResource as BaseResource
from openprocurement.api.utils import opresource


@opresource(name='Competitive Dialogue UA Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdUA',
            description="competitiveDialogue UA questions")
class CompetitiveDialogueUAQuestionResource(BaseResource):
    """ TenderEU Questions """


@opresource(name='Competitive Dialogue EU Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdEU',
            description="competitiveDialogue UE questions")
class CompetitiveDialogueEUQuestionResource(BaseResource):
    """ TenderEU Questions """

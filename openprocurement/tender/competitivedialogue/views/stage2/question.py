# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.question import TenderUaQuestionResource
from openprocurement.tender.openeu.views.question import TenderQuestionResource as TenderEUQuestionResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@opresource(name='Competitive Dialogue Stage 2 EU  Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Competitive Dialogue Stage 2 EU questions")
class CompetitiveDialogueStage2EUQuestionResource(TenderEUQuestionResource):
    """ Competitive Dialogue Stage 2 EU Questions """


@opresource(name='Competitive Dialogue Stage 2 UA  Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue Stage 2 UA questions")
class CompetitiveDialogueStage2UAQuestionResource(TenderUaQuestionResource):
    """ Competitive Dialogue Stage 2 UA Questions """


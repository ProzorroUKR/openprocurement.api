# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource, json_view
from openprocurement.tender.openua.views.question import TenderUaQuestionResource
from openprocurement.tender.openeu.views.question import TenderQuestionResource as TenderEUQuestionResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.validation import validate_post_question_data_stage2


@opresource(name='Competitive Dialogue Stage 2 EU  Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Competitive Dialogue Stage 2 EU questions")
class CompetitiveDialogueStage2EUQuestionResource(TenderEUQuestionResource):
    """ Competitive Dialogue Stage 2 EU Questions """

    @json_view(content_type="application/json",
               validators=(validate_post_question_data_stage2,),
               permission='create_question')
    def collection_post(self):
        return super(CompetitiveDialogueStage2EUQuestionResource, self).collection_post()


@opresource(name='Competitive Dialogue Stage 2 UA  Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue Stage 2 UA questions")
class CompetitiveDialogueStage2UAQuestionResource(TenderUaQuestionResource):
    """ Competitive Dialogue Stage 2 UA Questions """

    @json_view(content_type="application/json",
               validators=(validate_post_question_data_stage2,),
               permission='create_question')
    def collection_post(self):
        return super(CompetitiveDialogueStage2UAQuestionResource, self).collection_post()

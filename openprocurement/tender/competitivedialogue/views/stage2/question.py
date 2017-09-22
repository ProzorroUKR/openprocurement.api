# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import (
    optendersresource
)
from openprocurement.tender.openua.views.question import (
    TenderUaQuestionResource
)
from openprocurement.tender.openeu.views.question import (
    TenderQuestionResource as TenderEUQuestionResource
)
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
)
from openprocurement.tender.competitivedialogue.validation import (
    validate_post_question_data_stage2
)


@optendersresource(name='{}:Tender Questions'.format(STAGE_2_EU_TYPE),
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


@optendersresource(name='{}:Tender Questions'.format(STAGE_2_UA_TYPE),
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

# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.api.views.question import TenderQuestionResource as BaseResource

LOGGER = getLogger(__name__)


@opresource(name='TenderEU Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender questions")
class TenderQuestionResource(BaseResource):
    """ TenderEU Questions """

# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.award import TenderUaAwardResource
from openprocurement.tender.openeu.views.award import TenderAwardResource as TenderEUAwardResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@opresource(name='Competitive Dialogue Stage 2 EU Awards',
            collection_path='/tenders/{tender_id}/awards',
            path='/tenders/{tender_id}/awards/{award_id}',
            description="Competitive Dialogue Stage 2 EU awards",
            procurementMethodType=STAGE_2_EU_TYPE)
class CompetitiveDialogueStage2EUAwardResource(TenderEUAwardResource):
    """ Competitive Dialogue Stage 2 EU award resource """


@opresource(name='Competitive Dialogue Stage 2 UA Awards',
            collection_path='/tenders/{tender_id}/awards',
            path='/tenders/{tender_id}/awards/{award_id}',
            description="Competitive Dialogue Stage 2 UA awards",
            procurementMethodType=STAGE_2_UA_TYPE)
class CompetitiveDialogueStage2UAAwardResource(TenderUaAwardResource):
    """ Competitive Dialogue Stage 2 UA award resource """

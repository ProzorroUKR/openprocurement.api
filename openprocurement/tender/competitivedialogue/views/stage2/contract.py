# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.contract import TenderUaAwardContractResource
from openprocurement.tender.openeu.views.contract import TenderAwardContractResource as TenderEUAwardContractResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@opresource(name='Competitive Dialogue Stage 2 EU Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Competitive Dialogue Stage 2 EU contracts")
class CompetitiveDialogueStage2AwardContractResource(TenderEUAwardContractResource):
    pass


@opresource(name='Competitive Dialogue Stage 2 UA Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue Stage 2 UA contracts")
class CompetitiveDialogueStage2AwardContractResource(TenderUaAwardContractResource):
    pass

# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.contract import (
    TenderUaAwardContractResource
)
from openprocurement.tender.openeu.views.contract import (
    TenderAwardContractResource as TenderEUAwardContractResource
)
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
)


@optendersresource(name='{}:Tender Contracts'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/contracts',
                   path='/tenders/{tender_id}/contracts/{contract_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Competitive Dialogue Stage 2 EU contracts")
class CompetitiveDialogueEUStage2AwardContractResource(TenderEUAwardContractResource):
    pass


@optendersresource(name='{}:Tender Contracts'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/contracts',
                   path='/tenders/{tender_id}/contracts/{contract_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Competitive Dialogue Stage 2 UA contracts")
class CompetitiveDialogueUAStage2AwardContractResource(TenderUaAwardContractResource):
    pass

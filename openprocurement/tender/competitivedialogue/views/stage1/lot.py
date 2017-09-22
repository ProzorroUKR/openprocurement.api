# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.lot import (
    TenderEULotResource as TenderLotResource
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE, CD_UA_TYPE
)


@optendersresource(name='{}:Tender Lots'.format(CD_EU_TYPE),
                   collection_path='/tenders/{tender_id}/lots',
                   path='/tenders/{tender_id}/lots/{lot_id}',
                   procurementMethodType=CD_EU_TYPE,
                   description="Competitive Dialogue EU lots")
class CompetitiveDialogueEULotResource(TenderLotResource):
    pass


@optendersresource(name='{}:Tender Lots'.format(CD_UA_TYPE),
                   collection_path='/tenders/{tender_id}/lots',
                   path='/tenders/{tender_id}/lots/{lot_id}',
                   procurementMethodType=CD_UA_TYPE,
                   description="Competitive Dialogue UA lots")
class CompetitiveDialogueUALotResource(TenderLotResource):
    pass

# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.views.lot import TenderEULotResource as TenderLotResource
from openprocurement.api.utils import opresource
from openprocurement.tender.competitivedialogue.models import CD_EU_TYPE, CD_UA_TYPE


@opresource(name='Competitive Dialogue EU Lots',
            collection_path='/tenders/{tender_id}/lots',
            path='/tenders/{tender_id}/lots/{lot_id}',
            procurementMethodType=CD_EU_TYPE,
            description="Competitive Dialogue EU lots")
class CompetitiveDialogueEULotResource(TenderLotResource):
    pass


@opresource(name='Competitive Dialogue UA Lots',
            collection_path='/tenders/{tender_id}/lots',
            path='/tenders/{tender_id}/lots/{lot_id}',
            procurementMethodType=CD_UA_TYPE,
            description="Competitive Dialogue UA lots")
class CompetitiveDialogueUALotResource(TenderLotResource):
    pass

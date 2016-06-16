# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.views.lot import TenderEULotResource as TenderLotResource

from openprocurement.api.utils import (
    opresource,
)


@opresource(name='Competitive Dialogue EU Lots',
            collection_path='/tenders/{tender_id}/lots',
            path='/tenders/{tender_id}/lots/{lot_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdEU',
            description="Competitive Dialogue EU lots")
class CompetitiveDialogueEULotResource(TenderLotResource):
    pass


@opresource(name='Competitive Dialogue UA Lots',
            collection_path='/tenders/{tender_id}/lots',
            path='/tenders/{tender_id}/lots/{lot_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdUA',
            description="Competitive Dialogue UA lots")
class CompetitiveDialogueUALotResource(TenderLotResource):
    pass

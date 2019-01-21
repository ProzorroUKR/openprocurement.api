# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    get_now,
)
from openprocurement.tender.core.utils import (
    optendersresource,
    save_tender
)
from openprocurement.tender.core.validation import (
    validate_lot_data,
    validate_tender_period_extension,
    validate_lot_operation_not_in_allowed_status
)

from openprocurement.tender.openua.views.lot import (
    TenderUaLotResource as TenderLotResource
)


@optendersresource(name='aboveThresholdEU:Tender Lots',
                   collection_path='/tenders/{tender_id}/lots',
                   path='/tenders/{tender_id}/lots/{lot_id}',
                   procurementMethodType='aboveThresholdEU',
                   description="Tender EU lots")
class TenderEULotResource(TenderLotResource):
    pass

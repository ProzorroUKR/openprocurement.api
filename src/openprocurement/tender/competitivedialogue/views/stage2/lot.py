# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view

from openprocurement.tender.core.utils import (
    optendersresource
)
from openprocurement.tender.openua.views.lot import TenderUaLotResource
from openprocurement.tender.openeu.views.lot import TenderEULotResource
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
)
from openprocurement.tender.competitivedialogue.validation import validate_lot_operation_for_stage2


@optendersresource(name='{}:Lots'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/lots',
                   path='/tenders/{tender_id}/lots/{lot_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Tender stage2 UA lots")
class TenderStage2UALotResource(TenderUaLotResource):

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_lot_operation_for_stage2,))
    def patch(self):
        """ Update of lot """

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_lot_operation_for_stage2,))
    def collection_post(self):
        """ Add a lot """


    @json_view(permission='edit_tender', validators=(validate_lot_operation_for_stage2,))
    def delete(self):
        """Lot deleting """


@optendersresource(name='{}:Tender Lots'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/lots',
                   path='/tenders/{tender_id}/lots/{lot_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Tender stage2 EU lots")
class TenderStage2EULotResource(TenderEULotResource):

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_lot_operation_for_stage2,))
    def patch(self):
        """Update of lot """

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_lot_operation_for_stage2,))
    def collection_post(self):
        """Add a lot """

    @json_view(permission='edit_tender', validators=(validate_lot_operation_for_stage2,))
    def delete(self):
        """Lot deleting """

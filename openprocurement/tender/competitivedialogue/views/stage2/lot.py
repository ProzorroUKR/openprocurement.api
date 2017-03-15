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


@optendersresource(name='{}:Lots'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/lots',
                   path='/tenders/{tender_id}/lots/{lot_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Tender stage2 UA lots")
class TenderStage2UALotResource(TenderUaLotResource):

    @json_view(content_type="application/json", permission='edit_tender')
    def patch(self):
        """ Update of lot """
        self.request.errors.add('body', 'data', 'Can\'t update lot for tender stage2')
        self.request.errors.status = 403
        return

    @json_view(content_type="application/json", permission='edit_tender')
    def collection_post(self):
        """ Add a lot
        """
        self.request.errors.add('body', 'data', 'Can\'t create lot for tender stage2')
        self.request.errors.status = 403
        return

    @json_view(permission='edit_tender')
    def delete(self):
        """Lot deleting
        """
        self.request.errors.add('body', 'data', 'Can\'t delete lot for tender stage2')
        self.request.errors.status = 403
        return


@optendersresource(name='{}:Tender Lots'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/lots',
                   path='/tenders/{tender_id}/lots/{lot_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Tender stage2 EU lots")
class TenderStage2EULotResource(TenderEULotResource):

    @json_view(content_type="application/json", permission='edit_tender')
    def patch(self):
        """Update of lot
        """
        self.request.errors.add('body', 'data', 'Can\'t update lot for tender stage2')
        self.request.errors.status = 403
        return

    @json_view(content_type="application/json", permission='edit_tender')
    def collection_post(self):
        """Add a lot
        """
        self.request.errors.add('body', 'data', 'Can\'t create lot for tender stage2')
        self.request.errors.status = 403
        return

    @json_view(permission='edit_tender')
    def delete(self):
        """Lot deleting
        """
        self.request.errors.add('body', 'data', 'Can\'t delete lot for tender stage2')
        self.request.errors.status = 403
        return

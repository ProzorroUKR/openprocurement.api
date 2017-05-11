# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.cancellation import TenderCancellationResource as TenderEUCancellationResource


@opresource(name='Tender ESCO EU Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU Cancellations")
class TenderESCOEUCancellationResource(TenderEUCancellationResource):
    """ Tender ESCO EU Cancellation Resource """

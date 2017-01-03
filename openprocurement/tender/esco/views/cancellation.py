# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.cancellation import TenderUaCancellationResource
from openprocurement.tender.openeu.views.cancellation import TenderCancellationResource as TenderEUCancellationResource
from openprocurement.tender.limited.views.cancellation import TenderCancellationResource as TenderReportingCancellationResource


@opresource(name='Tender ESCO UA Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='esco.UA',
            description="Tender ESCO UA Cancellations")
class TenderESCOUACancellationResource(TenderUaCancellationResource):
    """ Tender ESCO UA Cancellation Resource """


@opresource(name='Tender ESCO EU Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU Cancellations")
class TenderESCOEUCancellationResource(TenderEUCancellationResource):
    """ Tender ESCO EU Cancellation Resource """


@opresource(name='Tender ESCO Reporting Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='esco.reporting',
            description="Tender ESCO Reporting Cancellations")
class TenderESCOReportingCancellationResource(TenderReportingCancellationResource):
    """ Tender ESCO Reporting Cancellation Resource """

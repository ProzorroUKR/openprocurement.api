# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.complaint import TenderUaComplaintResource
from openprocurement.tender.openeu.views.complaint import TenderEUComplaintResource


@optendersresource(name='Tender ESCO UA Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType='esco.UA',
            description="Tender ESCO UA Complaints")
class TenderESCOUAComplaintResource(TenderUaComplaintResource):
    """ Tender ESCO UA Complaint Resource """


@optendersresource(name='Tender ESCO EU Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU Complaints")
class TenderESCOEUComplaintResource(TenderEUComplaintResource):
    """ Tender ESCO EU Complaint Resource """

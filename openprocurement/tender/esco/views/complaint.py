# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.complaint import TenderEUComplaintResource


@opresource(name='Tender ESCO EU Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU Complaints")
class TenderESCOEUComplaintResource(TenderEUComplaintResource):
    """ Tender ESCO EU Complaint Resource """

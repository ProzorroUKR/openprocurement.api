# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.complaint import TenderEUComplaintResource


@optendersresource(name='esco.EU:Tender Complaints',
                   collection_path='/tenders/{tender_id}/complaints',
                   path='/tenders/{tender_id}/complaints/{complaint_id}',
                   procurementMethodType='esco.EU',
                   description="Tender ESCO EU Complaints")
class TenderESCOEUComplaintResource(TenderEUComplaintResource):
    """ Tender ESCO EU Complaint Resource """

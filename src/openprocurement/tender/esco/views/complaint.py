# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.complaint import TenderEUComplaintResource


@optendersresource(name='esco:Tender Complaints',
                   collection_path='/tenders/{tender_id}/complaints',
                   path='/tenders/{tender_id}/complaints/{complaint_id}',
                   procurementMethodType='esco',
                   description="Tender ESCO Complaints")
class TenderESCOComplaintResource(TenderEUComplaintResource):
    """ Tender ESCO Complaint Resource """

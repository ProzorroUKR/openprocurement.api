# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.award_complaint import TenderEUAwardComplaintResource


@optendersresource(name='esco.EU:TenderAward Complaints',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/complaints',
                   path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}',
                   procurementMethodType='esco.EU',
                   description="Tender ESCO EU Award complaints")
class TenderESCOEUAwardComplaintResource(TenderEUAwardComplaintResource):
    """ Tender ESCO EU Award Complaint Resource """

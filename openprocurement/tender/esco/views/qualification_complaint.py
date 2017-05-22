# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_complaint import TenderEUQualificationComplaintResource


@qualifications_resource(name='esco.EU:Tender Qualification Complaints',
                   collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints',
                   path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}',
                   procurementMethodType='esco.EU',
                   description="Tender ESCO EU qualification complaints")
class TenderESCOEUQualificationComplaintResource(TenderEUQualificationComplaintResource):
    """ Tender ESCO EU Qualification Complaints Resource """

# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification import \
    TenderQualificationResource as TenderEUQualificationResource


@qualifications_resource(name='esco.EU:Tender Qualification',
                         collection_path='/tenders/{tender_id}/qualifications',
                         path='/tenders/{tender_id}/qualifications/{qualification_id}',
                         procurementMethodType='esco.EU',
                         description="Tender ESCO EU Qualification")
class TenderESCOEULotResource(TenderEUQualificationResource):
    """ Tender ESCO EU Lot Resource """

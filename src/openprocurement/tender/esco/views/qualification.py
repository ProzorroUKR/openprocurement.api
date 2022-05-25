# -*- coding: utf-8 -*-
from cornice.resource import resource
from openprocurement.tender.core.procedure.views.qualification import TenderQualificationResource


@resource(
    name="esco:Tender Qualification",
    collection_path="/tenders/{tender_id}/qualifications",
    path="/tenders/{tender_id}/qualifications/{qualification_id}",
    procurementMethodType="esco",
    description="Tender ESCO Qualification",
)
class TenderESCOLotResource(TenderQualificationResource):
    """ Tender ESCO Lot Resource """

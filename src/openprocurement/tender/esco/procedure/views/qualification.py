# -*- coding: utf-8 -*-
from cornice.resource import resource
from openprocurement.tender.core.procedure.views.qualification import TenderQualificationResource
from openprocurement.tender.esco.procedure.state.qualification import ESCOQualificationState


@resource(
    name="esco:Tender Qualification",
    collection_path="/tenders/{tender_id}/qualifications",
    path="/tenders/{tender_id}/qualifications/{qualification_id}",
    procurementMethodType="esco",
    description="Tender ESCO Qualification",
)
class TenderESCOQualificationResource(TenderQualificationResource):
    """ Tender ESCO Lot Resource """
    state_class = ESCOQualificationState

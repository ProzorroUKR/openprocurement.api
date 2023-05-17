# -*- coding: utf-8 -*-
from openprocurement.tender.core.procedure.views.qualification import TenderQualificationResource
from cornice.resource import resource


@resource(
    name="aboveThreshold:Tender Qualification",
    collection_path="/tenders/{tender_id}/qualifications",
    path="/tenders/{tender_id}/qualifications/{qualification_id}",
    procurementMethodType="aboveThreshold",
    description="aboveThreshold Qualification",
)
class TenderEUQualificationResource(TenderQualificationResource):
    pass

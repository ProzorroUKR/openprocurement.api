# -*- coding: utf-8 -*-
from openprocurement.tender.core.procedure.views.qualification import TenderQualificationResource
from cornice.resource import resource


@resource(
    name="aboveThresholdEU:Tender Qualification",
    collection_path="/tenders/{tender_id}/qualifications",
    path="/tenders/{tender_id}/qualifications/{qualification_id}",
    procurementMethodType="aboveThresholdEU",
    description="TenderEU Qualification",
)
class TenderEUQualificationResource(TenderQualificationResource):
    pass

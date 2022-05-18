# -*- coding: utf-8 -*-
from cornice.resource import resource
from openprocurement.tender.core.procedure.views.qualification import TenderQualificationResource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@resource(
    name="{}:Tender Qualification".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications",
    path="/tenders/{tender_id}/qualifications/{qualification_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU Qualification",
)
class CompetitiveDialogueEUQualificationResource(TenderQualificationResource):
    pass


@resource(
    name="{}:Tender Qualification".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications",
    path="/tenders/{tender_id}/qualifications/{qualification_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA Qualification",
)
class CompetitiveDialogueUAQualificationResource(TenderQualificationResource):
    pass

# -*- coding: utf-8 -*-
from cornice.resource import resource
from openprocurement.tender.core.procedure.views.qualification import TenderQualificationResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE


@resource(
    name="{}:Tender Qualification".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications",
    path="/tenders/{tender_id}/qualifications/{qualification_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU Qualification",
)
class CompetitiveDialogueStage2(TenderQualificationResource):
    pass

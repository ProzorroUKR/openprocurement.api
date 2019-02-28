# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_document import (
    TenderQualificationDocumentResource as BaseTenderQualificationDocumentResource
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE, CD_UA_TYPE
)


@qualifications_resource(
    name='{}:Tender Qualification Documents'.format(CD_EU_TYPE),
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/documents',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}',
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU Qualification Documents")
class CompetitiveDialogueEUQualificationDocumentResource(BaseTenderQualificationDocumentResource):
    pass


@qualifications_resource(
    name='{}:Tender Qualification Documents'.format(CD_UA_TYPE),
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/documents',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}',
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA Qualification Documents")
class CompetitiveDialogueUAQualificationDocumentResource(BaseTenderQualificationDocumentResource):
    pass

# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_document import (
    TenderQualificationDocumentResource as TenderEUQualificationDocumentResource,
)


@qualifications_resource(
    name="esco:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO qualification documents",
)
class TenderESCOQualificationDocumentResource(TenderEUQualificationDocumentResource):
    """ Tender ESCO Qualification Documents Resource """

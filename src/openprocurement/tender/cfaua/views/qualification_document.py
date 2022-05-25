# -*- coding: utf-8 -*-
from openprocurement.tender.cfaua.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_document import TenderQualificationDocumentResource


# @qualifications_resource(
#     name="closeFrameworkAgreementUA:Tender Qualification Documents",
#     collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
#     path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
#     procurementMethodType="closeFrameworkAgreementUA",
#     description="Tender qualification documents",
# )
class TenderQualificationDocumentResource(TenderQualificationDocumentResource):
    pass

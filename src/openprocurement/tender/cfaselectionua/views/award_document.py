# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.award_document import TenderAwardDocumentResource


# @optendersresource(
#     name="closeFrameworkAgreementSelectionUA:Tender Award Documents",
#     collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
#     path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
#     procurementMethodType="closeFrameworkAgreementSelectionUA",
#     description="Tender award documents",
# )
class TenderAwardDocumentResource(TenderAwardDocumentResource):
    pass

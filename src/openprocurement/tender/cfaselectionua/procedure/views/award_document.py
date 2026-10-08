from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.award_document import (
    CFAUAAwardDocumentState,
)
from openprocurement.tender.core.procedure.views.award_document import (
    BaseAwardDocumentResource,
)


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender award documents",
)
class CFASelectionTenderBidDocumentResource(BaseAwardDocumentResource):
    state_class = CFAUAAwardDocumentState

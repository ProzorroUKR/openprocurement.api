from cornice.resource import resource

from openprocurement.tender.cfaua.constants import CFA_UA
from openprocurement.tender.cfaua.procedure.state.qualification_document import (
    CFAUAQualificationDocumentState,
)
from openprocurement.tender.core.procedure.views.qualification_document import (
    BaseQualificationDocumentResource,
)


@resource(
    name=f"{CFA_UA}:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=CFA_UA,
    description="Tender qualification documents",
)
class CFAUAQualificationDocumentResource(BaseQualificationDocumentResource):
    state_class = CFAUAQualificationDocumentState

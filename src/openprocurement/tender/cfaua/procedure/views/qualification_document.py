from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.cfaua.procedure.state.qualification_document import (
    CFAUAQualificationDocumentState,
)
from openprocurement.tender.core.procedure.views.qualification_document import (
    BaseQualificationDocumentResource,
)


@resource(
    name=f"{ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA}:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
    description="Tender qualification documents",
)
class CFAUAQualificationDocumentResource(BaseQualificationDocumentResource):
    state_class = CFAUAQualificationDocumentState

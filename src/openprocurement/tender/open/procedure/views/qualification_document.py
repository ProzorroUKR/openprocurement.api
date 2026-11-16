from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.qualification_document import BaseQualificationDocumentResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    description="Tender qualification documents",
    procurementMethodType=[
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL,
        ProcurementMethodType.OPEN_TENDERING,
    ],
)
class OpenBaseQualificationDocumentResource(BaseQualificationDocumentResource):
    pass

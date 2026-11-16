from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_document import (
    BaseAwardDocumentResource,
)
from openprocurement.tender.limited.procedure.state.award_document import LimitedAwardDocumentState


@resource(
    name="reporting:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.REPORTING,
    description="Tender award documents",
)
class ReportingAwardDocumentResource(BaseAwardDocumentResource):
    state_class = LimitedAwardDocumentState


@resource(
    name="negotiation:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION,
    description="Tender award documents",
)
class NegotiationAwardDocumentResource(ReportingAwardDocumentResource):
    pass


@resource(
    name="negotiation.quick:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION_QUICK,
    description="Tender award documents",
)
class NegotiationQuickAwardDocumentResource(ReportingAwardDocumentResource):
    pass

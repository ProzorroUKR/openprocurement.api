from openprocurement.tender.openua.procedure.views.tender_document import UATenderDocumentResource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from cornice.resource import resource


@resource(
    name=f"{CD_EU_TYPE}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description=f"Tender {CD_EU_TYPE} related binary files (PDFs, etc.)",
)
class CDEUTenderDocumentResource(UATenderDocumentResource):
    pass


@resource(
    name=f"{CD_UA_TYPE}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description=f"Tender {CD_UA_TYPE} related binary files (PDFs, etc.)",
)
class CDUATenderDocumentResource(UATenderDocumentResource):
    pass

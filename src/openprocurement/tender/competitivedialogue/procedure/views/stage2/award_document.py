from openprocurement.tender.openua.procedure.views.award_document import UATenderAwardDocumentResource
from openprocurement.tender.openeu.procedure.views.award_document import EUTenderBidDocumentResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_UA_TYPE, STAGE_2_EU_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Award Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender award documents",
)
class CDStage2EUTenderAwardDocumentResource(EUTenderBidDocumentResource):
    pass


@resource(
    name="{}:Tender Award Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA award documents",
)
class CDStage2UATenderAwardDocumentResource(UATenderAwardDocumentResource):
    pass

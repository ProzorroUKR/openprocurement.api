from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.openua.procedure.views.award_document import (
    UATenderAwardDocumentResource,
)


@resource(
    name="complexAsset.arma:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender award documents",
)
class AwardDocumentResource(UATenderAwardDocumentResource):
    pass

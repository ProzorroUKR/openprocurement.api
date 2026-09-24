from openprocurement.tender.competitivedialogue.procedure.models.document import (
    CDBidDocument,
    CDBidPatchDocument,
    CDBidPostDocument,
)
from openprocurement.tender.core.procedure.state.bid_document import (
    BidDocumentState,
    BidFinancialDocumentState,
)


class CDBidDocumentState(BidDocumentState):
    post_data_model = CDBidPostDocument
    patch_data_model = CDBidPatchDocument
    data_model = CDBidDocument


class CDBidFinancialDocumentState(BidFinancialDocumentState):
    post_data_model = CDBidPostDocument
    patch_data_model = CDBidPatchDocument
    data_model = CDBidDocument

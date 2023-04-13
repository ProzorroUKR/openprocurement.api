from openprocurement.tender.esco.procedure.state.tender import ESCOTenderStateMixin
from openprocurement.tender.openua.procedure.state.tender_document import UATenderDocumentState


class ESCOTenderDocumentState(ESCOTenderStateMixin, UATenderDocumentState):
    pass
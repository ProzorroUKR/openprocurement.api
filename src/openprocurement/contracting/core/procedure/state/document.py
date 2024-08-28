from openprocurement.contracting.core.procedure.state.contract import BaseContractState
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing


class BaseDocumentState(BaseDocumentStateMixing, BaseContractState):
    pass

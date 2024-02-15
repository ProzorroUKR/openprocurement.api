from openprocurement.contracting.api.procedure.state.contract import ContractState
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing


class BaseDocumentState(BaseDocumentStateMixing, ContractState):
    pass

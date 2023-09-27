from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing
from openprocurement.contracting.api.procedure.state.contract import ContractState


class BaseDocumentState(BaseDocumentStateMixing, ContractState):
    pass

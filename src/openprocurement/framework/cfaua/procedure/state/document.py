from openprocurement.framework.cfaua.procedure.state.agreement import AgreementState
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing


class AgreementDocumentState(BaseDocumentStateMixing, AgreementState):
    item_name = "agreement"

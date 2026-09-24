from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.state.qualification_document import (
    QualificationDocumentStateMixing,
)


class CFAUAQualificationDocumentState(QualificationDocumentStateMixing, BaseDocumentState):
    all_documents_should_be_public = True

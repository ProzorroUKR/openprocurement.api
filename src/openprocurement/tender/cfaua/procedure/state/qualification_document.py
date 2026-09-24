from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.state.qualification_document import (
    QualificationDocumentStateMixin,
)


class CFAUAQualificationDocumentState(QualificationDocumentStateMixin, BaseDocumentState):
    all_documents_should_be_public = True

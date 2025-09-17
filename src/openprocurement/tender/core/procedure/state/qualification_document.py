from copy import deepcopy

from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.validation import validate_doc_type_quantity


class QualificationDocumentState(BaseDocumentState):
    def document_always(self, data):
        super().document_always(data)
        self.validate_sign_documents_already_exists(data)

    def validate_sign_documents_already_exists(self, doc_data):
        qualification = self.request.validated["qualification"]
        qualification_docs = deepcopy(qualification.get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            qualification_docs.extend(new_documents)
        else:  # PATCH/PUT
            qualification_docs.append(doc_data)
        validate_doc_type_quantity(qualification_docs, document_type="deviationReport", obj_name="qualification")

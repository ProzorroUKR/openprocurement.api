from openprocurement.tender.core.procedure.state.complaint_post import (
    ComplaintPostState,
)
from openprocurement.tender.core.procedure.validation import (
    validate_edrpou_confidentiality_doc,
)


class CFAUAComplaintPostState(ComplaintPostState):
    def validate_docs(self, data):
        for doc in data.get("documents", []):
            validate_edrpou_confidentiality_doc(doc, should_be_public=True)

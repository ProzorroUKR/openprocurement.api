from openprocurement.tender.core.procedure.state.complaint_appeal import (
    ComplaintAppealState,
)
from openprocurement.tender.core.procedure.validation import (
    validate_edrpou_confidentiality_doc,
)


class CFAUAComplaintAppealState(ComplaintAppealState):
    def validate_docs(self, data):
        for doc in data.get("documents", []):
            validate_edrpou_confidentiality_doc(doc, should_be_public=True)

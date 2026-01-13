from openprocurement.api.constants_env import CANCELLATION_REPORT_DOC_REQUIRED_FROM
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.core.procedure.validation import (
    validate_doc_type_quantity,
    validate_edrpou_confidentiality_doc,
)
from openprocurement.tender.openeu.procedure.state.cancellation import (
    OpenEUCancellationStateMixing,
)


class CFAUACancellationStateMixing(OpenEUCancellationStateMixing):
    def validate_docs(self, data):
        documents = data.get("documents", [])
        for doc in documents:
            validate_edrpou_confidentiality_doc(doc, should_be_public=True)
        if tender_created_after(CANCELLATION_REPORT_DOC_REQUIRED_FROM):
            validate_doc_type_quantity(documents, document_type="cancellationReport")


class CFAUACancellationState(CFAUACancellationStateMixing, CFAUATenderState):
    pass

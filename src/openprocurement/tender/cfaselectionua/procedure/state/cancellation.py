from openprocurement.api.constants_env import CANCELLATION_REPORT_DOC_REQUIRED_FROM
from openprocurement.tender.belowthreshold.procedure.state.cancellation import (
    BelowThresholdCancellationStateMixing,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.core.procedure.validation import (
    validate_doc_type_quantity,
    validate_edrpou_confidentiality_doc,
)


class CFASelectionCancellationState(BelowThresholdCancellationStateMixing, CFASelectionTenderState):
    _before_release_reason_types = None
    _after_release_reason_types = [
        "noDemand",
        "unFixable",
        "forceMajeure",
        "expensesCut",
    ]

    def validate_docs(self, data):
        documents = data.get("documents", [])
        for doc in documents:
            validate_edrpou_confidentiality_doc(doc, should_be_public=True)
        if tender_created_after(CANCELLATION_REPORT_DOC_REQUIRED_FROM):
            validate_doc_type_quantity(documents, document_type="cancellationReport")

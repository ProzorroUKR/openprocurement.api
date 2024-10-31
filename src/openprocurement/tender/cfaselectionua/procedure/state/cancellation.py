from openprocurement.tender.belowthreshold.procedure.state.cancellation import (
    BelowThresholdCancellationStateMixing,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.procedure.validation import (
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
        for doc in data.get("documents", []):
            validate_edrpou_confidentiality_doc(doc, should_be_public=True)

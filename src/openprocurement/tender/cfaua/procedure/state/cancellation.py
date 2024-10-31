from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.validation import (
    validate_edrpou_confidentiality_doc,
)
from openprocurement.tender.openeu.procedure.state.cancellation import (
    OpenEUCancellationStateMixing,
)


class CFAUACancellationStateMixing(OpenEUCancellationStateMixing):
    def validate_docs(self, data):
        for doc in data.get("documents", []):
            validate_edrpou_confidentiality_doc(doc, should_be_public=True)


class CFAUACancellationState(CFAUACancellationStateMixing, CFAUATenderState):
    pass

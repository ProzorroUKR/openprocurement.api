from openprocurement.tender.core.procedure.state.qualification_claim import (
    QualificationClaimStateMixin,
)
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState


class OpenEUQualificationClaimState(QualificationClaimStateMixin, BaseOpenEUTenderState):
    pass

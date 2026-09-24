from openprocurement.tender.core.procedure.state.qualification_claim import (
    QualificationClaimStateMixin,
)
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


class OpenEUQualificationClaimState(QualificationClaimStateMixin, OpenEUTenderState):
    pass

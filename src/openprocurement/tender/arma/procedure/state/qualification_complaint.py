from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.qualification_complaint import (
    QualificationComplaintStateMixin,
)


class QualificationComplaintState(QualificationComplaintStateMixin, TenderState):
    pass

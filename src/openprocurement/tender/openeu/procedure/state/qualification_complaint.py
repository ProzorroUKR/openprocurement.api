from openprocurement.tender.core.procedure.state.qualification_complaint import (
    QualificationComplaintStateMixin,
)
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


class OpenEUQualificationComplaintState(QualificationComplaintStateMixin, OpenEUTenderState):
    pass

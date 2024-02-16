from openprocurement.tender.core.procedure.state.qualification_complaint import (
    QualificationComplaintStateMixin,
)
from openprocurement.tender.esco.procedure.state.complaint import (
    ESCOComplaintStateMixin,
)
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class ESCOQualificationComplaintState(ESCOComplaintStateMixin, QualificationComplaintStateMixin, ESCOTenderState):
    pass

from openprocurement.tender.core.procedure.state.qualification_complaint import QualificationComplaintState
from openprocurement.tender.esco.procedure.state.complaint import ESCOComplaintMixin


class ESCOQualificationComplaintState(ESCOComplaintMixin, QualificationComplaintState):
    pass

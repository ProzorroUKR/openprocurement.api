from openprocurement.tender.core.procedure.state.qualification import QualificationState
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderStateMixin


class ESCOQualificationState(ESCOTenderStateMixin, QualificationState):
    pass
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.qualification_complaint import (
    QualificationComplaintStateMixin,
)


class CFAUAQualificationComplaintState(QualificationComplaintStateMixin, CFAUATenderState):
    all_documents_should_be_public = True

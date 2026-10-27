from openprocurement.framework.core.procedure.state.qualification import (
    QualificationState,
)
from openprocurement.framework.dps.procedure.models.qualification import Qualification


class DPSQualificationState(QualificationState):
    data_model = Qualification

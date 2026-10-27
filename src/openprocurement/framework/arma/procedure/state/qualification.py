from openprocurement.framework.arma.procedure.models.qualification import Qualification
from openprocurement.framework.core.procedure.state.qualification import (
    QualificationState,
)


class ARMAQualificationState(QualificationState):
    data_model = Qualification

from openprocurement.framework.core.procedure.state.qualification import (
    QualificationState,
)
from openprocurement.framework.electroniccatalogue.procedure.models.qualification import Qualification


class ElectronicDialogueQualificationState(QualificationState):
    data_model = Qualification

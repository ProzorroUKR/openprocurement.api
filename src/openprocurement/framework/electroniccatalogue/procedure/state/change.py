from openprocurement.framework.core.procedure.state.change import ChangeState
from openprocurement.framework.electroniccatalogue.procedure.state.framework import (
    ElectronicDialogueFrameworkState,
)


class ElectronicDialogueChangeState(ElectronicDialogueFrameworkState, ChangeState):
    pass

from openprocurement.framework.core.procedure.state.change import ChangeState
from openprocurement.framework.ifi.procedure.state.framework import (
    IFIFrameworkState,
)


class IFIChangeState(IFIFrameworkState, ChangeState):
    pass

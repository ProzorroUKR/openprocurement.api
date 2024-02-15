from openprocurement.framework.core.procedure.state.framework import FrameworkState

from .agreement import AgreementState


class CFAUAFrameworkState(FrameworkState):
    agreement_class = AgreementState

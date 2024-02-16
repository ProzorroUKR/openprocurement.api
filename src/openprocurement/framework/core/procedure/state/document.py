from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.framework.core.procedure.state.milestone import MilestoneState
from openprocurement.framework.core.procedure.state.qualification import (
    QualificationState,
)
from openprocurement.framework.core.procedure.state.submission import SubmissionState
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing


class BaseFrameworkDocumentState(BaseDocumentStateMixing, FrameworkState):
    item_name = "framework"


class SubmissionDocumentState(BaseDocumentStateMixing, SubmissionState):
    item_name = "submission"


class QualificationDocumentState(BaseDocumentStateMixing, QualificationState):
    item_name = "qualification"


class MilestoneDocumentState(BaseDocumentStateMixing, MilestoneState):
    item_name = "milestone"

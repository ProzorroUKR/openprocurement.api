from openprocurement.framework.core.procedure.state.qualification import (
    QualificationState,
)
from openprocurement.framework.ifi.procedure.models.qualification import Qualification


class IFIQualificationState(QualificationState):
    data_model = Qualification

    evaluation_reports_doc_required = False

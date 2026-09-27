from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1TenderDetailsStateMixin,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class CDCriterionState(CriterionStateMixin, CDStage1TenderDetailsStateMixin):
    pass

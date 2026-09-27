from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1TenderDetailsStateMixin,
)
from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin


class CDRequirementGroupState(RequirementGroupStateMixin, CDStage1TenderDetailsStateMixin):
    pass

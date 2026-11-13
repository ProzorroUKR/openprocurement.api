from openprocurement.tender.competitivedialogue.procedure.models.award import CDAward, CDPatchAward, CDPostAward
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.award import AwardStateMixin
from openprocurement.tender.core.procedure.state.tender import TenderState


class CDStage2AwardState(AwardStateMixin, TenderState):
    award_class = Award
    post_data_model = CDPostAward
    patch_data_model = CDPatchAward
    data_model = CDAward

    items_unit_required: bool = False
    items_quantity_required: bool = False

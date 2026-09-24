from openprocurement.tender.core.procedure.models.tender_base import PlanRelation
from openprocurement.tender.core.procedure.state.tender import TenderState


class TenderPlansState(TenderState):
    post_data_model = PlanRelation

    def validate_post_request(self):
        self.validate_item_owner("tender")
        self.validate_input_data(self.get_post_data_model())

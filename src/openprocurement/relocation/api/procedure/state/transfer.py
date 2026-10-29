from openprocurement.api.procedure.state.base import BaseState
from openprocurement.relocation.api.procedure.models.transfer import PostTransfer


class TransferState(BaseState):
    post_data_model = PostTransfer

    # --- request validation (called from the views) ---

    def validate_transfer_post_request(self):
        self.validate_input_data(self.get_post_data_model())

from openprocurement.api.procedure.models.signer_info import SignerInfo
from openprocurement.contracting.core.procedure.state.contract import ContractState
from openprocurement.contracting.core.procedure.utils import get_tender_award_by_contract


class ContractSignerInfoState(ContractState):
    post_data_model = SignerInfo

    # --- request validation (called from the views) ---

    def validate_buyer_signer_info_put_request(self):
        exempt = self.request.authenticated_role in ("admins", "Administrator")
        if not exempt:
            self.validate_contract_owner()
        self.validate_input_data(self.get_post_data_model())
        if not exempt:
            self.validate_contract_status_pending()

    def validate_suppliers_signer_info_put_request(self):
        exempt = self.request.authenticated_role in ("admins", "Administrator")
        if not exempt:
            self.validate_contract_supplier()
        self.validate_input_data(self.get_post_data_model())
        if not exempt:
            self.validate_contract_status_pending()

    def signer_info_on_put(self, data: dict) -> None:
        tender = self.request.validated["tender"]
        award = get_tender_award_by_contract(tender, self.request.validated["contract"])
        self.validate_cancellation_blocks(self.request, tender, lot_id=award.get("lotID"))

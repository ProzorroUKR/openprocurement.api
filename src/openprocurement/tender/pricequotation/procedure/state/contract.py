from copy import deepcopy
from logging import getLogger
from hashlib import sha512


from openprocurement.tender.core.procedure.state.contract import ContractStateMixing
from openprocurement.tender.pricequotation.procedure.state.tender import PriceQuotationTenderState
from openprocurement.api.utils import context_unpack, get_now
from openprocurement.tender.core.procedure.context import get_tender

from openprocurement.contracting.api.procedure.utils import save_contract

LOGGER = getLogger(__name__)


class PQContractState(ContractStateMixing, PriceQuotationTenderState):

    def contract_on_post(self, data):
        pass

    def _prepare_contract_data(self, data):
        disallowed_fields = (
            "title",
            "title_en",
            "title_ru",
            "description",
            "description_en",
            "description_ru",

        )
        tender = get_tender()

        contract = deepcopy(data)

        for i in disallowed_fields:
            if contract.get(i):
                del contract[i]

        contract["owner"] = tender["owner"]
        contract["tender_token"] = sha512(tender["owner_token"].encode("utf-8")).hexdigest()
        contract["tender_id"] = tender["_id"]
        contract["buyer"] = tender["buyer"] if tender.get("buyer") else tender["procuringEntity"]

        return contract

    def contract_on_save(self, data):
        contract = self._prepare_contract_data(data)
        if save_contract(self.request, insert=True, contract=contract, contract_src={}):
            return True

    def check_tender_status_method(self) -> None:
        tender = self.request.validated["tender"]
        last_award_status = tender["awards"][-1]["status"] if tender.get("awards") else ""
        if last_award_status == "unsuccessful":
            LOGGER.info(
                f"Switched tender {tender['id']} to unsuccessful",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "switched_tender_unsuccessful"}
                ),
            )
            self.set_object_status(tender, "unsuccessful")
        if (
                tender.get("contracts")
                and any([contract["status"] == "active" for contract in tender["contracts"]])
                and not any([contract["status"] == "pending" for contract in tender["contracts"]])
        ):
            self.set_object_status(tender, "complete")

    def contract_on_patch(self, before: dict, after: dict):
        self.validate_contract_items(before, after)
        super().contract_on_patch(before, after)

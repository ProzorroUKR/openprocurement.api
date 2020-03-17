# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.views.contract import TenderAwardContractResource
from openprocurement.api.utils import context_unpack, json_view, get_now, raise_operation_error
from openprocurement.tender.openua.utils import check_tender_status
from openprocurement.tender.core.validation import (
    validate_contract_signing,
    validate_patch_contract_data,
    validate_update_contract_value,
    validate_update_contract_only_for_active_lots,
    validate_contract_operation_not_in_allowed_status,
    validate_update_contract_value_with_award,
    validate_update_contract_value_amount,
    validate_update_contract_value_net_required,
)
from openprocurement.tender.core.utils import save_tender, apply_patch, optendersresource
from openprocurement.tender.openua.validation import validate_contract_update_with_accepted_complaint


@optendersresource(
    name="aboveThresholdUA:Tender Contracts",
    collection_path="/tenders/{tender_id}/contracts",
    path="/tenders/{tender_id}/contracts/{contract_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender contracts",
)
class TenderUaAwardContractResource(TenderAwardContractResource):
    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            validate_patch_contract_data,
            validate_contract_operation_not_in_allowed_status,
            validate_update_contract_only_for_active_lots,
            validate_contract_update_with_accepted_complaint,
            validate_update_contract_value,
            validate_contract_signing,
            validate_update_contract_value_net_required,
            validate_update_contract_value_with_award,
            validate_update_contract_value_amount,
        ),
    )
    def patch(self):
        """Update of contract
        """
        contract_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if contract_status != self.request.context.status and (
            contract_status != "pending" or self.request.context.status != "active"
        ):
            raise_operation_error(self.request, "Can't update contract status")
        if self.request.context.status == "active" and not self.request.context.dateSigned:
            self.request.context.dateSigned = get_now()
        check_tender_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender contract {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_contract_patch"}),
            )
            return {"data": self.request.context.serialize()}
